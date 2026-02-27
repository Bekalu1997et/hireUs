"""
Database base configuration.
Declares the declarative base class for SQLAlchemy models.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Declarative base class for all SQLAlchemy models.
    All models should inherit from this class.
    """
    pass

