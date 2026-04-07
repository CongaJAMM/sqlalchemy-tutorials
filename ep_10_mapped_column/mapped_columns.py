# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=iwENqqgxm-g

"""Example #1

SQLAlchemy 2.0 Modern Mapping Module (Mapped & mapped_column)

This module demonstrates the Declarative Mapping style introduced in SQLAlchemy 2.0. 
It leverages Python type hints to define database columns, making the models 
compatible with static analysis tools (Mypy) and IDE autocompletion.

Key Concepts:
1. DeclarativeBase:
   The modern alternative to 'declarative_base()'. Subclassing this provides 
   a consistent starting point for all models and registry management.

2. Mapped[T]:
   A generic type hint that tells SQLAlchemy this attribute is a database-mapped 
   column. The type 'T' (e.g., int, str) defines the Python type of the attribute.

3. mapped_column():
   The 2.0 successor to 'Column()'. It is used to provide specific database 
   directives (primary_key, nullable, server_default) while allowing the 
   SQL type to be inferred from the Mapped[] annotation.

4. Optionality & Nullability:
   - Mapped[str] is 'NOT NULL' by default.
   - Mapped[Optional[str]] (or str | None) is 'NULL' by default.
"""

from typing import Optional

from sqlalchemy import Integer, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

engine = create_engine('sqlite:///ep_10_mapped_columns.db', echo=True)


class Base(DeclarativeBase):
    """
    The abstract base class for all models.
    
    In SQLAlchemy 2.0, this replaces the old Base = declarative_base() 
    and acts as the registry for the application's metadata.
    """
    pass


class User(Base):
    """
    Represents the 'users' table using modern type-annotated mapping.
    
    Class Attributes:
        id (mapped_column): Explicitly defined with Integer. Even without 
            a Mapped[] hint here, SQLAlchemy uses the function to create 
            the primary key.
            
        name (Mapped[Optional[str]]): An implicit mapping. No mapped_column() 
            is needed because SQLAlchemy inspects the type hint. Since it 
            uses 'Optional', the database column is created as VARCHAR/TEXT 
            with NULL allowed.
            
        age (Mapped[int]): An explicit mapping where the type is inferred 
            from the hint (int -> INTEGER), but specific behavior (nullable=True) 
            is forced via mapped_column.
    """
    __tablename__ = 'users'

    # column type from the mapped_column function, cannot be null
    id = mapped_column(Integer, primary_key=True)

    # implicit 'mapped_column' creation based off annotation, can be null
    name: Mapped[Optional[str]]

    # column type inferred from the Mapped Annotation, can be null
    age: Mapped[int] = mapped_column(nullable=True)


# Create the database tables
Base.metadata.create_all(engine)
