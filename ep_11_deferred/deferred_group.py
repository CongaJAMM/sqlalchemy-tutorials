# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=WKbJ1txwmeQ

"""Example #2

SQLAlchemy Deferred Group Loading Module

This module demonstrates how to categorize deferred columns into logical 'groups'.
Grouping is a powerful optimization for scenarios where certain columns are 
frequently used together but rarely used at all.

Key Concepts:
1. Group Loading:
   When one column in a group is accessed (e.g., 'user.first_name'), SQLAlchemy 
   emits a single SELECT statement to fetch every column belonging to that 
   group (e.g., both 'first_name' and 'last_name').

2. Efficiency:
   This prevents "fragmented" queries. Instead of one query for the first name 
   and a second query later for the last name, you get both in one trip 
   to the database.

3. The 'undefer_group' Option:
   Similar to 'undefer', this query option allows you to force-load an 
   entire group of columns during the initial query.
"""

from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    deferred,
    mapped_column,
    sessionmaker,
    undefer_group,  # NEW
)

engine = create_engine('sqlite:///ep_11_deferred_group.db', echo=True)
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
    Represents the 'users' table with grouped deferred loading.
    
    This model organizes deferred attributes into 'name' and 'other' clusters.

    ORM Attributes:
        nickname (Mapped[str]): Standard column, always loaded initially.
            
        first_name (Mapped[str]): Part of the 'name' group. Accessing this 
            triggers the loading of 'last_name' as well.
            
        last_name (Column): Also part of the 'name' group.
            
        other_value (Mapped[str]): Part of the 'other' group. Accessing 
            this will NOT trigger the loading of the 'name' group.
    """
    __tablename__ = 'users'

    # Always loaded
    nickname: Mapped[str] = mapped_column(String)
    
    # Deferred Group 'name': Accessing either will fetch both
    first_name: Mapped[str] = deferred(mapped_column(String), group='name')
    last_name = deferred(Column(String), group='name')
    
    # Deferred Group 'other': Isolated from the 'name' group
    other_value: Mapped[str] = mapped_column(
        String, deferred=True, deferred_group='other'
    )

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
user = session.query(User).first()
print(user)
print(user.first_name)
print(user.last_name)
print(user.other_value)

# close the session to show deferring
session.close()

# undefer one group
user = session.query(User).options(undefer_group('name')).first()
print(user)
print(user.first_name)
print(user.last_name)
print(user.other_value)

session.close()
user = session.query(User).options(undefer_group('other')).first()
print(user)
print(user.first_name)
print(user.last_name)
print(user.other_value)

session.close()
# undefer multiple groups
user = (
    session.query(User).options(undefer_group('name'), undefer_group('other')).first()
)
print(user)
print(user.first_name)
print(user.last_name)
print(user.other_value)
