import logging
import sqlite3

import pandas as pd
import sqlalchemy
from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger(__name__)

Base = declarative_base()


class Customer(Base):
    """Creates a data model for the database to be set up for capturing churn data."""
    __tablename__ = "churn"

    id = Column(Integer, primary_key=True)
    state = Column(String(2), unique=False, nullable=True)
    account_length = Column(Integer, unique=False, nullable=True)
    area_code = Column(Integer, unique=False, nullable=True)
    international_plan = Column(String(3), unique=False, nullable=True)
    voice_mail_plan = Column(String(3), unique=False, nullable=True)
    number_vmail_messages = Column(Integer, unique=False, nullable=True)
    total_day_minutes = Column(Float, unique=False, nullable=True)
    total_day_calls = Column(Integer, unique=False, nullable=True)
    total_day_charge = Column(Float, unique=False, nullable=True)
    total_eve_minutes = Column(Float, unique=False, nullable=True)
    total_eve_calls = Column(Integer, unique=False, nullable=True)
    total_eve_charge = Column(Float, unique=False, nullable=True)
    total_night_minutes = Column(Float, unique=False, nullable=True)
    total_night_calls = Column(Integer, unique=False, nullable=True)
    total_night_charge = Column(Float, unique=False, nullable=True)
    total_intl_minutes = Column(Float, unique=False, nullable=True)
    total_intl_calls = Column(Integer, unique=False, nullable=True)
    total_intl_charge = Column(Float, unique=False, nullable=True)
    customer_service_calls = Column(Integer, unique=False, nullable=True)
    churn = Column(Boolean, unique=False, nullable=False)

    def __repr__(self):
        return f'<Customer {self.id}>'


def create_db(engine_string: str) -> None:
    """Create database with churn data model from provided engine string.

    Args:
        engine_string (str): SQLAlchemy engine string specifying which database
            to write to

    Returns: None

    """
    engine = sqlalchemy.create_engine(engine_string)

    try:
        Base.metadata.create_all(engine)
    except sqlalchemy.exe.OperationalError as e:
        logger.error("Cannot connect to the database. Error: %s", e)
    else:
        logger.info("Database created.")


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
            raise ValueError("Need either an engine string or a Flask app to initialize")

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
            logger.error("You might have connection error. Have you configured SQLALCHEMY_DATABASE_URI"
                         "variable correctly and connected to Northwestern VPN? Error: %s ", e)
        except sqlite3.OperationalError as e:
            logger.error("Error page returned. Not able to add customer data to local sqlite "
                         "database. Is it the right path? Error: %s ", e)
        else:
            logger.info("%d records were added to the table", len(data_list))
