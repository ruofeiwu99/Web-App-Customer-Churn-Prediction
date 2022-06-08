import logging.config

import sqlite3
import traceback
import pickle

import pandas as pd
import yaml
import sqlalchemy.exc
from flask import Flask, render_template, request, redirect, url_for

# pylint: disable=locally-disabled, invalid-name

# For setting up the Flask-SQLAlchemy database session
from src.create_db import ChurnManager, Customer
from src.modeling import pred_one_record
from src.process_data import validate_input

# Initialize the Flask application
app = Flask(__name__, template_folder='app/templates',
            static_folder='app/static')

# Configure flask app from flask_config.py
app.config.from_pyfile('config/flaskconfig.py')

# Define LOGGING_CONFIG in flask_config.py - path to config file for setting
# up the logger (e.g. config/logging/local.conf)
logging.config.fileConfig(app.config['LOGGING_CONFIG'])
logger = logging.getLogger(app.config['APP_NAME'])
logger.debug(
    'Web app should be viewable at %s:%s if docker run command maps local '
    'port to the same port as configured for the Docker container '
    'in config/flaskconfig.py (e.g. `-p 5000:5000`). Otherwise, go to the '
    'port defined on the left side of the port mapping '
    '(`i.e. -p THISPORT:5000`). If you are running from a Windows machine, '
    'go to 127.0.0.1 instead of 0.0.0.0.', app.config['HOST']
    , app.config['PORT'])

# Initialize the database session
churn_manager = ChurnManager(app)


@app.route('/')
def index():
    """Main view of customer data from churn table in the database.

    Create view into index page that uses data queried from Customer database and
    inserts it into the app/templates/index.html template.

    Returns:
        Rendered html template

    """
    try:
        customers = churn_manager.session.query(Customer).order_by(Customer.id).\
            limit(app.config['MAX_ROWS_SHOW'])

        logger.debug('Index page accessed')
        return render_template('index.html', customers=customers)
    except sqlite3.OperationalError as e:
        logger.error(
            'Error page returned. Not able to query local sqlite database: %s.'
            ' Error: %s ',
            app.config['SQLALCHEMY_DATABASE_URI'], e)
        return render_template('error.html')
    except sqlalchemy.exc.OperationalError as e:
        logger.error(
            'Error page returned. Not able to query MySQL database: %s. '
            'Error: %s ',
            app.config['SQLALCHEMY_DATABASE_URI'], e)
        return render_template('error.html')
    except:
        traceback.print_exc()
        logger.error('Not able to display customer data, error page returned')
        return render_template('error.html')


@app.route('/predict', methods=['POST'])
def predict_churn():
    """
        Predict customer churn given a POST form of input data.
        Returns:
            Redirect to index page
    """
    intl_plan = 'No'
    if 'IntlPlan' in request.form:
        intl_plan = 'Yes'
    vm_plan = 'No'
    if 'VMPlan' in request.form:
        vm_plan = 'Yes'
    cust_id = request.form['id']
    vm_msg = request.form['vm_msg']
    day_mins = request.form['day_mins']
    eve_mins = request.form['eve_mins']
    night_mins = request.form['night_mins']
    intl_mins = request.form['intl_mins']
    intl_calls = request.form['intl_calls']
    service_calls = request.form['service_calls']

    # Load configuration file
    with open('config/config.yaml', 'r', encoding='utf8') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    record = {'id': cust_id,
              'international_plan': intl_plan,
              'voice_mail_plan': vm_plan,
              'number_vmail_messages': vm_msg,
              'total_day_minutes': day_mins,
              'total_eve_minutes': eve_mins,
              'total_night_minutes': night_mins,
              'total_intl_minutes': intl_mins,
              'total_intl_calls': intl_calls,
              'customer_service_calls': service_calls}
    record_df = pd.DataFrame(record, index=[0])
    # Validate user input data
    try:
        valid_record_df = validate_input(record_df, **config['process_data']['validate_input'])
    except ValueError as e:
        logger.error('Error: %s', e)
        return render_template('error.html')

    # Predict churn label
    try:
        with open('models/rf_model.pkl', 'rb') as f:
            rf_model = pickle.load(f)
    except FileNotFoundError:
        logger.error('File not found, please check if model object is saved')
    churn_pred = pred_one_record(rf_model,
                                 columns=config['modeling']['pred_one_record']['columns'],
                                 record_df=valid_record_df)
    if churn_pred == 0:
        final_churn_pred = 'No'
    else:
        final_churn_pred = 'Yes'

    try:
        churn_manager.add_one_record(valid_record_df['id'].item(), intl_plan, vm_plan,
                                     valid_record_df['number_vmail_messages'].item(),
                                     valid_record_df['total_day_minutes'].item(),
                                     valid_record_df['total_eve_minutes'].item(),
                                     valid_record_df['total_night_minutes'].item(),
                                     valid_record_df['total_intl_minutes'].item(),
                                     valid_record_df['total_intl_calls'].item(),
                                     valid_record_df['customer_service_calls'].item(),
                                     final_churn_pred)
        logger.info('One customer record added: customer id %s', request.form['id'])
        return redirect(url_for('index'))
    except sqlite3.OperationalError as e:
        logger.error(
            'Error page returned. Not able to add customer record to local sqlite '
            'database: %s. Error: %s ',
            app.config['SQLALCHEMY_DATABASE_URI'], e)
        return render_template('error.html')
    except sqlalchemy.exc.OperationalError as e:
        logger.error(
            'Error page returned. Not able to add customer record to MySQL database: %s. '
            'Error: %s ',
            app.config['SQLALCHEMY_DATABASE_URI'], e)
        return render_template('error.html')
    # exception handling for non-unique customer id
    except sqlalchemy.exc.IntegrityError as e:
        logger.error(
            'Error page returned. Not able to add customer record to MySQL database: %s. '
            'Error: %s ',
            app.config['SQLALCHEMY_DATABASE_URI'], e)
        return render_template('error.html')


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], port=app.config['PORT'],
            host=app.config['HOST'])
