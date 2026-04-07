# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=_cHSW_ehjtY

"""Example #1

SQLAlchemy Event Listeners: Imperative Registration & Insertion Hooks

This module demonstrates how to register event listeners using the 
'event.listen()' function rather than the decorator syntax. This approach 
is highly flexible for library development or complex application setups.

Key Concepts:
1. Imperative Registration (event.listen):
   Allows you to attach a listener function to a target after the target 
   class has already been defined. This is useful for keeping your model 
   files clean of side-effect logic.

2. The 'before_insert' Event:
   This event triggers after the Session has received a new object and 
   decided it needs to be persisted, but BEFORE the SQL 'INSERT' statement 
   is actually sent to the database.

3. Bulk Operations:
   When adding multiple objects to a session, the 'before_insert' event 
   will fire individually for every single instance during the flush 
   process, allowing for per-record validation or transformation.

4. Use Cases:
   - Generating UUIDs or slugs before saving.
   - Setting default timestamps (created_at).
   - Logging/Auditing new record creation.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, mapped_column, Mapped, DeclarativeBase, Mapper
from sqlalchemy.engine import Connection

engine = create_engine('sqlite:///:memory:')


class Base(DeclarativeBase):
    """Standard Declarative Base."""
    id: Mapped[int] = mapped_column(primary_key=True)


class User(Base):
    """
    Represents the 'users' table.
    
    The 'insert_user_listener' is attached to this class to monitor 
    the creation of new user records.
    """
    __tablename__ = 'users'
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


def insert_user_listener(mapper: Mapper, connection: Connection, target: User):
    """
    A standalone function designed to handle 'before_insert' logic.
    
    Arguments:
        target (User): The specific User instance currently being flushed.
    """
    print(f'[EVENT: before_insert ] Inserting user: {target.name}')


# Imperative Registration
# This links the function to the event without modifying the User class code.
event.listen(User, 'before_insert', insert_user_listener)

for x in range(1, 10):
    user = User(name=f'User {x}', email=f'user_{x}@email.com')
    session.add(user)

session.commit()
