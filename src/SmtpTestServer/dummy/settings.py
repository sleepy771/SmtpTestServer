"""Deffault app settings"""
from sqlalchemy.ext.declarative import declarative_base
from flask.ext.api import FlaskAPI
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# engine = ??

Session = sessionmaker(bind=engine)

app = FlaskAPI(__name__)
