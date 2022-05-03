import os
import logging
import sqlalchemy as sql
from sqlalchemy import Column, Integer, String, Float, Boolean
import sqlalchemy.exc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from config.flaskconfig import SQLALCHEMY_DATABASE_URI

logger = logging.getLogger(__name__)

Base = declarative_base()


class ChurnData(Base):
    """Creates a data model for the database to be set up for capturing churn data."""
    __tablename__ = "churn"

    id = Column(Integer, primary_key=True)
    state = Column(String(2), unique=False, nullable=True)
    account_len = Column(Integer, unique=False, nullable=True)
    area_code = Column(Integer, unique=False, nullable=True)
    intl_plan = Column(String(3), unique=False, nullable=True)
    voice_mail_plan = Column(String(3), unique=False, nullable=True)
    num_mail_plan = Column(Integer, unique=False, nullable=True)
    total_day_mins = Column(Float, unique=False, nullable=True)
    total_day_calls = Column(Integer, unique=False, nullable=True)
    total_day_charge = Column(Float, unique=False, nullable=True)
    total_eve_mins = Column(Float, unique=False, nullable=True)
    total_eve_calls = Column(Integer, unique=False, nullable=True)
    total_eve_charge = Column(Float, unique=False, nullable=True)
    total_night_mins = Column(Float, unique=False, nullable=True)
    total_night_calls = Column(Integer, unique=False, nullable=True)
    total_night_charge = Column(Float, unique=False, nullable=True)
    total_intl_mins = Column(Float, unique=False, nullable=True)
    total_intl_calls = Column(Integer, unique=False, nullable=True)
    total_intl_charge = Column(Float, unique=False, nullable=True)
    cust_serv_calls = Column(Integer, unique=False, nullable=True)
    churn = Column(Boolean, unique=False, nullable=False)

    def __repr__(self):
        return f'<Customer {self.id}>'


def create_db(engine_string: str) -> None:
    """Create database with Tracks() data model from provided engine string.

    Args:
        engine_string (str): SQLAlchemy engine string specifying which database
            to write to

    Returns: None

    """
    engine = sqlalchemy.create_engine(engine_string)

    Base.metadata.create_all(engine)
    logger.info("Database created.")


if __name__ == "__main__":
    # set up mysql connection
    engine = sql.create_engine(SQLALCHEMY_DATABASE_URI)

    # test database connection
    try:
        engine.connect()
    except sqlalchemy.exc.OperationalError as e:
        logger.error("Cannot connect to database!")
        raise e

    # create the tracks table
    Base.metadata.create_all(engine)

    # create a db session
    Session = sessionmaker(bind=engine)
    session = Session()

    session.commit()
    logger.info(
            "Database created"
    )

    session.close()


