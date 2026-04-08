# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=ftbYlej2xQY

"""
SQLAlchemy Data Models and Database Initialization

This module defines the structural blueprint of the database. It handles 
the creation of the SQLAlchemy Engine, the declaration of the ORM Base, 
and the mapping of Python classes to database tables.

Separation of Concerns: The database structure (Models) is separate from the business logic (CRUD operations). This prevents the main script from becoming a "spaghetti code" mess.

Circular Dependency Prevention: As the project grows to include dozens of tables, having a central models file helps prevent Python import errors.

Key Architecture Features:
1. Programmatic URL Generation: Uses 'sqlalchemy.URL' to construct a 
   dialect-specific connection string for SQLite.
2. Engine Configuration: Initializes the core interface between Python 
   and the database file ('ep_02_database.db').
3. Declarative Schema: Implements the 'declarative_base' pattern to 
   track model metadata, enabling automated DDL (Data Definition Language) 
   commands like 'create_all()'.
4. Object Representation: Includes customized '__repr__' methods to 
   facilitate cleaner debugging and logging of database records.
"""

from sqlalchemy import URL, Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base

url_object = URL.create(
    'sqlite',
    database='ep_05_database.db',
)
# or
# engine = create_engine("sqlite:///ep_05_database.db.db")

# Create an engine for a SQLite database
engine = create_engine(url_object)

# Create a base class for our models
Base = declarative_base()


# Define a model for the "users" table
class User(Base):
    """
    ORM Model representing the 'users' table.
    
    This class maps Python attributes to SQL columns, allowing the 
    application to interact with user data as native Python objects.
    
    Attributes:
        id (Column): The Primary Key; an integer that uniquely identifies 
            each user and auto-increments by default.
        name (Column): A string representing the user's full name.
        age (Column): An integer representing the user's age.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)

    def __repr__(self) -> str:
        """
        Provides a formatted string representation of the User instance.
        
        The padding formatting (e.g., ':>3', ':<13') ensures that when printing 
        lists of users, the columns align vertically in the console.
        """
        return f'<User id: {self.id:>3}: name: {self.name:<13}, age: {self.age:>3}>'


# create the database tables
Base.metadata.create_all(engine)
