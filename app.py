import logging.config
import sqlite3
import traceback

import pandas as pd
import yaml
import sqlalchemy.exc
from flask import Flask, render_template, request, redirect, url_for

# For setting up the Flask-SQLAlchemy database session
from src.create_db import ChurnManager, Customer
from src.modeling import pred_one_record

# Initialize the Flask application
app = Flask(__name__, template_folder="app/templates",
            static_folder="app/static")

# Configure flask app from flask_config.py
app.config.from_pyfile('config/flaskconfig.py')

# Define LOGGING_CONFIG in flask_config.py - path to config file for setting
# up the logger (e.g. config/logging/local.conf)
logging.config.fileConfig(app.config["LOGGING_CONFIG"])
logger = logging.getLogger(app.config["APP_NAME"])
logger.debug(
    'Web app should be viewable at %s:%s if docker run command maps local '
    'port to the same port as configured for the Docker container '
    'in config/flaskconfig.py (e.g. `-p 5000:5000`). Otherwise, go to the '
    'port defined on the left side of the port mapping '
    '(`i.e. -p THISPORT:5000`). If you are running from a Windows machine, '
    'go to 127.0.0.1 instead of 0.0.0.0.', app.config["HOST"]
    , app.config["PORT"])

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
        customers = churn_manager.session.query(Customer).order_by(Customer.id.desc()).\
            limit(app.config["MAX_ROWS_SHOW"])

        logger.debug("Index page accessed")
        return render_template('index.html', customers=customers)
    except sqlite3.OperationalError as e:
        logger.error(
            "Error page returned. Not able to query local sqlite database: %s."
            " Error: %s ",
            app.config['SQLALCHEMY_DATABASE_URI'], e)
        return render_template('error.html')
    except sqlalchemy.exc.OperationalError as e:
        logger.error(
            "Error page returned. Not able to query MySQL database: %s. "
            "Error: %s ",
            app.config['SQLALCHEMY_DATABASE_URI'], e)
        return render_template('error.html')
    except:
        traceback.print_exc()
        logger.error("Not able to display tracks, error page returned")
        return render_template('error.html')


@app.route('/add', methods=['POST'])
def add_entry():
    """View that process a POST with new customer record

    Returns:
        redirect to index page
    """
    try:
        churn_manager.add_one_record(int(request.form['id']), request.form['intl_plan'], request.form['vm_plan'],
                                     int(request.form['vm_msg']), float(request.form['day_mins']),
                                     float(request.form['eve_mins']), float(request.form['night_mins']),
                                     float(request.form['intl_mins']), int(request.form['intl_calls']),
                                     int(request.form['service_calls']), request.form['churn_label'])
        logger.info("One customer record added: customer id %s", request.form['id'])
        return redirect(url_for('index'))
    except sqlite3.OperationalError as e:
        logger.error(
            "Error page returned. Not able to add song to local sqlite "
            "database: %s. Error: %s ",
            app.config['SQLALCHEMY_DATABASE_URI'], e)
        return render_template('error.html')
    except sqlalchemy.exc.OperationalError as e:
        logger.error(
            "Error page returned. Not able to add song to MySQL database: %s. "
            "Error: %s ",
            app.config['SQLALCHEMY_DATABASE_URI'], e)
        return render_template('error.html')


@app.route("/predict", methods=["POST"])
def predict_churn():
    """
        Predict customer churn given a POST form of input data.
        Returns:
            Redirect to index page
    """
    record = {'id': int(request.form['id']),
              'international_plan': request.form['intl_plan'],
              'voice_mail_plan': request.form['vm_plan'],
              'number_vmail_messages': int(request.form['vm_msg']),
              'total_day_minutes': float(request.form['day_mins']),
              'total_eve_minutes': float(request.form['eve_mins']),
              'total_night_minutes': float(request.form['night_mins']),
              'total_intl_minutes': float(request.form['intl_mins']),
              'total_intl_calls': int(request.form['intl_calls']),
              'customer_service_calls': int(request.form['service_calls'])}
    record_df = pd.DataFrame(record, index=[0])

    # Ensure all columns (& order) match the original training data
    # validated_df = model.validate_dataframe(input_df)
    with open('config/config.yaml', "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    churn_pred = pred_one_record(**config['modeling']['pred_one_record'], record_df=record_df)
    if churn_pred == 0:
        final_churn_pred = 'No'
    else:
        final_churn_pred = 'Yes'

    try:
        churn_manager.add_one_record(int(request.form['id']), request.form['intl_plan'], request.form['vm_plan'],
                                     int(request.form['vm_msg']), float(request.form['day_mins']),
                                     float(request.form['eve_mins']), float(request.form['night_mins']),
                                     float(request.form['intl_mins']), int(request.form['intl_calls']),
                                     int(request.form['service_calls']), final_churn_pred)
        logger.info("One customer record added: customer id %s", request.form['id'])
        return redirect(url_for('index'))
    except sqlite3.OperationalError as e:
        logger.error(
            "Error page returned. Not able to add song to local sqlite "
            "database: %s. Error: %s ",
            app.config['SQLALCHEMY_DATABASE_URI'], e)
        return render_template('error.html')
    except sqlalchemy.exc.OperationalError as e:
        logger.error(
            "Error page returned. Not able to add song to MySQL database: %s. "
            "Error: %s ",
            app.config['SQLALCHEMY_DATABASE_URI'], e)
        return render_template('error.html')


if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"],
            host=app.config["HOST"])
