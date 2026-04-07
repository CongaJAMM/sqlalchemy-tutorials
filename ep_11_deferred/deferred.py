# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=WKbJ1txwmeQ

"""Example #1

SQLAlchemy Deferred Column Loading Module

This module demonstrates how to exclude specific columns from the default 
SELECT statement of a model. This is a critical optimization for tables 
containing "heavy" data (e.g., BLOBs, long Text fields, or XML) that is 
rarely needed during bulk queries.

Key Concepts:
1. Column Deferral:
   A deferred column is not loaded when the object is first queried. 
   SQLAlchemy only emits a second SELECT to fetch the specific column's 
   value when it is accessed (e.g., 'print(user.first_name)').

2. Multiple Syntax Options:
   SQLAlchemy 2.0 provides three ways to defer columns:
   - Wrapping mapped_column() in deferred().
   - Using the 'deferred=True' argument within mapped_column().
   - Wrapping the legacy Column() object in deferred().

3. The 'undefer' Option:
   Even if a column is marked as deferred in the model, you can force it 
   to load immediately during a specific query using the 'undefer' 
   query option.
"""

from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    deferred,
    mapped_column,
    sessionmaker,
    undefer,
)

engine = create_engine('sqlite:///ep_11_deferred.db', echo=True)
session = sessionmaker(bind=engine)()


class Base(DeclarativeBase):
    """
    The Declarative Base for modern mapping.
    
    Attributes:
        id (Mapped[int]): Defined at the Base level to ensure every 
            inheriting model has a primary key automatically.
    """
    id: Mapped[int] = mapped_column(primary_key=True)


class User(Base):
    """
    Represents the 'users' table with various deferred loading configurations.
    
    This model demonstrates that you can selectively hide columns from 
    the initial query to save bandwidth and memory.

    ORM Attributes:
        nickname (Mapped[str]): A standard column. This is ALWAYS loaded 
            in the first query (e.g., SELECT id, nickname FROM users).
            
        first_name (Mapped[str]): Deferred via the deferred() function. 
            This will NOT be in the initial SELECT.
            
        last_name (Column): Deferred using the legacy Column syntax. 
            Functionally identical to first_name.
            
        other_value (Mapped[str]): Deferred using the 2.0 'deferred=True' 
            keyword argument. This is often considered the cleanest 
            syntax for modern 2.0 mapping.
    """
    __tablename__ = 'users'

    # Standard Eager Load: Always included in queries
    nickname: Mapped[str] = mapped_column(String)

    # Deferred Option 1: Wrapping mapped_column
    first_name: Mapped[str] = deferred(mapped_column(String))

    # Deferred Option 2: Legacy Column style (SQLAlchemy 1.x style)
    last_name = deferred(Column(String))

    # Deferred Option 3: Modern 2.0 keyword argument (Recommended)
    other_value: Mapped[str] = mapped_column(String, deferred=True)

    def __repr__(self) -> str:
        return f'< User: {self.id} - {self.nickname} >'


# Create the database tables
Base.metadata.create_all(engine)

# If there is data in the database, don't add more data
if session.query(User).count() < 1:
    user = User(
        nickname='ZT', first_name='Zeq', last_name='Tech', other_value='secret value'
    )
    session.add(user)
    session.commit()


# undefer nothing
print('\nUndefer Nothing')
user = session.query(User).first()
print(user)
print(user.first_name)
print(user.last_name)
print(user.other_value)

# close the session to show deferring
session.close()

print('\nUndefer One Column')
# undefer one column
user = session.query(User).options(undefer(User.first_name)).first()
print(user)
print(user.first_name)
print(user.last_name)
print(user.other_value)

# close the session to show deferring
session.close()

print('\nUndefer One Column')
user = session.query(User).options(undefer(User.last_name)).first()
print(user)
print(user.first_name)
print(user.last_name)
print(user.other_value)

# close the session to show deferring
session.close()

print('\nUndefer Multiple Column')
# undefer multiple columns
user = (
    session.query(User)
    .options(undefer(User.last_name), undefer(User.other_value))
    .first()
)
print(user)
print(user.first_name)
print(user.last_name)
print(user.other_value)
