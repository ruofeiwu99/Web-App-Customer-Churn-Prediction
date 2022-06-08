import logging
import sqlite3

import pandas as pd
import sqlalchemy
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger('create-db')

Base = declarative_base()


class Customer(Base):
    """Creates a data model for the database to be set up for capturing customer data."""
    __tablename__ = 'churn'

    id = Column(Integer, primary_key=True)
    international_plan = Column(String(3), unique=False, nullable=False)
    voice_mail_plan = Column(String(3), unique=False, nullable=False)
    number_vmail_messages = Column(Integer, unique=False, nullable=False)
    total_day_minutes = Column(Float, unique=False, nullable=False)
    total_eve_minutes = Column(Float, unique=False, nullable=False)
    total_night_minutes = Column(Float, unique=False, nullable=False)
    total_intl_minutes = Column(Float, unique=False, nullable=False)
    total_intl_calls = Column(Integer, unique=False, nullable=False)
    customer_service_calls = Column(Integer, unique=False, nullable=False)
    churn = Column(String(3), unique=False, nullable=False)

    def __repr__(self):
        return f'<Customer {self.id}>'


def create_db(engine_string: str) -> None:
    """Create database with customer data model from provided engine string.

    Args:
        engine_string (str): SQLAlchemy engine string specifying which database to write to

    Returns: None
    """
    engine = sqlalchemy.create_engine(engine_string)

    try:
        Base.metadata.create_all(engine)
    except sqlalchemy.exe.OperationalError as e:
        logger.error('Cannot connect to the database. Error: %s', e)
    else:
        logger.info('Database created.')


class ChurnManager:
    def __init__(self, app=None, engine_string=None):
        if app:
            self.database = SQLAlchemy(app)
            self.session = self.database.session
        elif engine_string:
            engine = sqlalchemy.create_engine(engine_string)
            session_maker = sqlalchemy.orm.sessionmaker(bind=engine)
            self.session = session_maker()
        else:
            raise ValueError('Need either an engine string or a Flask app to initialize')

    def close(self) -> None:
        # closes session
        self.session.close()

    def add_customer_data(self, input_path: str) -> None:
        session = self.session
        # convert the raw dataframe to a list of dictionaries
        raw_data_list = pd.read_csv(input_path).to_dict(orient='records')
        data_list = []
        for data in raw_data_list:
            data_list.append(Customer(**data))

        try:
            session.add_all(data_list)
            session.commit()
        except sqlalchemy.exc.OperationalError as e:
            logger.error('You might have connection error. Have you configured SQLALCHEMY_DATABASE_URI '
                         'variable correctly and connected to Northwestern VPN? Error: %s ', e)
        except sqlite3.OperationalError as e:
            logger.error('Error page returned. Not able to add customer data to local sqlite '
                         'database. Is it the right path? Error: %s ', e)
        else:
            logger.info('%d records were added to the table', len(data_list))

    def add_one_record(self, cust_id: int, international_plan: str,
                       voice_mail_plan: str, number_vmail_messages: int, total_day_minutes: float,
                       total_eve_minutes: float, total_night_minutes: float, total_intl_minutes: float,
                       total_intl_calls: int, customer_service_calls: int, churn: str):
        """
        Add one customer record to the database.
        Args:
            cust_id (int): customer id (unique)
            international_plan (str): whether a customer has international plan ("Yes" or "No")
            voice_mail_plan (str): whether a customer has voice mail plan ("Yes" or "No")
            number_vmail_messages (int): number of voice mail messages
            total_day_minutes (float): total minutes used on a day-use plan
            total_eve_minutes (float): total minutes used on an evening-use plan
            total_night_minutes (float): total minutes used on a night-use plan
            total_intl_minutes (float): total minutes used on an international plan
            total_intl_calls (int): total calls made on an international plan
            customer_service_calls (int): total number of customer service calls
            churn (str): churn label for a customer ("Yes" or "No")

        Returns:
            None
        """
        session = self.session
        try:
            customer = Customer(id=cust_id, international_plan=international_plan, voice_mail_plan=voice_mail_plan,
                                number_vmail_messages=number_vmail_messages, total_day_minutes=total_day_minutes,
                                total_eve_minutes=total_eve_minutes, total_night_minutes=total_night_minutes,
                                total_intl_minutes=total_intl_minutes, total_intl_calls=total_intl_calls,
                                customer_service_calls=customer_service_calls, churn=churn)

        except sqlalchemy.exc.OperationalError as e:
            logger.error(
                "Cannot connect to the database.  "
                "Please check configuration of SQLALCHEMY_DATABASE_URI and VPN. Error: %s ", e)

        # exception handling for non-unique customer id
        except sqlalchemy.exc.IntegrityError:
            logger.error('Customer id %d already exists in the database.', cust_id)

        else:
            session.add(customer)
            session.commit()
            logger.info('One customer record added to database: customer id %s', cust_id)
