# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=Z2zD3EdjpNo

"""
SQLAlchemy Basics: Connection Engines and Declarative Schema

This module demonstrates the foundational steps required to bootstrap a 
SQLAlchemy application. It covers database connection strings, the 
creation of the Engine, and the definition of database tables using 
the Declarative system.

Key Architecture Features:
1. URL Management:
   Utilizes 'sqlalchemy.URL.create' to programmatically build a connection 
   string, ensuring the correct dialect and driver are specified for the 
   underlying database (SQLite in this instance).

2. The Engine:
   Initializes the 'create_engine' object, which acts as the primary source 
   of connectivity and the interface between the Python application and 
   the database driver.

3. Declarative Base:
   Establishes a 'Base' class using 'declarative_base()'. All ORM models 
   inherit from this class to participate in the 'metadata' collection, 
   which tracks the schema definitions for automated table creation.

4. Schema Definition:
   Defines a 'User' model that maps directly to a 'users' table in SQL, 
   showcasing basic column types (Integer, String) and primary key setup.
"""

from sqlalchemy import URL, create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base

url_object = URL.create(
    'sqlite',
    database='ep_01_database.db',
) 
# FORMAT:
# "<dialect>+<driver>://<username>:<password>@<host>:<port>/<databasename>"

# For an in-memory database:
# url = "sqlite://:memory:"

# For an database file:
# url = "sqlite:///path/to/database.db"

# Create an engine for a SQLite database
engine = create_engine(url_object)
# or
# engine = create_engine("sqlite:///ep_01_database.db.db")

# Create a base class for our models; old style
Base = declarative_base()


# Define a model for the "users" table
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)


# Create the database tables
Base.metadata.create_all(engine)
