# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# https://www.youtube.com/watch?v=WsDVBEmTlaI

"""Example #3

SQLAlchemy Table-Level Index Configuration (__table_args__)

This module illustrates how to define database indexes and constraints at the 
table level. This is the preferred method when you need to move beyond 
simple column-level flags like 'index=True'.

Key Concepts:
1. __table_args__:
   A special attribute in Declarative models that accepts a tuple of 
   table-level constructs (Indexes, Constraints, etc.). 

2. Named Indexes:
   By using the 'Index' object inside '__table_args__', you can explicitly 
   name your index (e.g., 'ix_users_name'). This is critical for database 
   migrations where consistent naming is required across different environments.

3. String vs. Object References:
   Indexes in '__table_args__' can reference columns by their string name 
   ('name') or by the attribute object itself (User.name). String names 
   are often safer when dealing with complex circular dependencies.
"""

# When you run this code, you can see the line in the output:
# sqlalchemy.engine.Engine CREATE UNIQUE INDEX ix_users_email ON users (email)


from sqlalchemy import create_engine, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

engine = create_engine('sqlite:///:memory:', echo=True)


class Base(DeclarativeBase):
    """
    Standard Declarative Base for modern SQLAlchemy mapping.
    """
    id: Mapped[int] = mapped_column(primary_key=True)


class User(Base):
    """
    Represents the 'users' table with multiple index strategies.
    
    Class Attributes:
        id (Mapped[int]): The primary key. Databases automatically create 
            a unique index for primary keys to ensure identity.
            
        email (Mapped[str]): Uses the 'unique=True' shorthand. This 
            generates a UNIQUE INDEX behind the scenes.
            
        name (Mapped[str]): A standard string column. It is indexed via 
            the '__table_args__' tuple below.

    Table Arguments:
        __table_args__: Defines 'ix_users_name'. This ensures that 
            searches by user name are optimized (O(log N)) rather than 
            linear (O(N)).
    """
    __tablename__ = 'users'

    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)  # Add the index here

    __table_args__ = (
        # The first argument is the index name and the second argument is the column name we want to use
        # here we just put the string representation of the column name
        # Be sure to add a comma to make the __table_args__ a tuple
        Index('ix_users_name', 'name'),
    )


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# ============================================================

for name, table in Base.metadata.tables.items():
    print(f"\nTable: {name}")
    indexes = list(table.indexes)
    if len(indexes) < 1:
        print("- No Indexes")
    for index in indexes:
        print(f"- Index Name: {index.name}")
        print(f"- Columns: {', '.join([column.name for column in index.columns])}")
