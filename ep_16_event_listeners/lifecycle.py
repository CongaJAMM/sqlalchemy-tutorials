# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=_cHSW_ehjtY

"""Example #4

SQLAlchemy Event Lifecycle: Deep Dive & Execution Order

This module serves as a diagnostic tool to visualize the exact sequence of 
events triggered during standard ORM operations. It covers three distinct 
layers of the SQLAlchemy ecosystem:


    Event #1 Flush w/ Commit
        session.flush()
            before_flush -> before_insert/before_update/before_delete -> before_execute -> 
                after_execute -> after_insert/after_update/after_delete -> after_flush ->
                after_flush_postexec

        session.commit()   
                -> before_commit -> after_commit

        session.rollback()
            after_rollback

    Event #2 Commit Only
        session.commit()
            before_commit -> before_flush -> before_insert/before_update/before_delete -> 
                before_execute -> after_execute -> after_insert/after_update/after_delete ->
                after_flush -> after_flush_postexec -> after_commit
                
        session.rollback()
            after_rollback

    Event #3 Query on the Database w/out Inserting, Updating, or Deleting
        session.query()/session.execute()/session.scalar()
            before_execute -> after_execute
        session.rollback()
            after_rollback

            
1. Engine Events (The Bottom Layer):
   Intercepts raw SQL execution. These events ('before_execute', 'after_execute') 
   fire whenever the database driver is asked to perform a task.

2. Session Events (The Middle Layer):
   Manages the transaction lifecycle. These hooks ('before_flush', 'after_commit', 
   'after_rollback') are critical for managing external side-effects like 
   clearing caches or sending emails once a transaction is finalized.

3. Mapper/Object Events (The Top Layer):
   Hooks into the specific life of an object. These ('before_insert', 'after_update') 
   fire as the Session translates Python objects into SQL rows.

Key Learning Objective:
By observing the print output, you can see how a single 'session.commit()' 
actually triggers a cascade of events:
Flush -> Before/After Insert -> Engine Execute -> Postexec -> Before/After Commit.
"""

from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import sessionmaker, mapped_column, Mapped, DeclarativeBase

engine = create_engine('sqlite:///:memory:')


class Base(DeclarativeBase):
    """Base model providing primary key structure."""
    id: Mapped[int] = mapped_column(primary_key=True)


# Define a simple User model
class User(Base):
    """
    Represents the 'users' table. Used as the target for Mapper events.
    """
    __tablename__ = 'users'
    name: Mapped[str] = mapped_column(unique=True)


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


# Event Listener Functions
def log_event(name):
    """
    A decorator factory that creates a listener function for any event.
    
    Args:
        name (str): The name of the event to be printed when triggered.
    """
    def wrapper(*args, **kwargs):
        print(f'🔹 {name} triggered!')

    return wrapper


# Session Lifecycle Events
event.listen(Session, 'before_flush', log_event('before_flush'))
event.listen(Session, 'after_flush', log_event('after_flush'))
event.listen(Session, 'after_flush_postexec', log_event('after_flush_postexec'))
event.listen(Session, 'before_commit', log_event('before_commit'))
event.listen(Session, 'after_commit', log_event('after_commit'))
event.listen(Session, 'after_rollback', log_event('after_rollback'))

#  Object Lifecycle (Mapper) Events
event.listen(User, 'before_insert', log_event('before_insert'))
event.listen(User, 'after_insert', log_event('after_insert'))
event.listen(User, 'before_update', log_event('before_update'))
event.listen(User, 'after_update', log_event('after_update'))
event.listen(User, 'before_delete', log_event('before_delete'))
event.listen(User, 'after_delete', log_event('after_delete'))

# Execution Events
event.listen(engine, 'before_execute', log_event('before_execute'))
event.listen(engine, 'after_execute', log_event('after_execute'))

# Transaction Test Cases
try:
    print('\nINSERT OPERATION')
    user = User(name='Zeq')
    session.add(user)
    session.flush()
    session.commit()

    print('\nQuery OPERATION')
    u = session.query(User).all()
    print('\nQuery OPERATION')
    u = session.execute(select(User)).all()
    print('\nQuery OPERATION')
    u = session.scalar(select(User))

    print('\nUPDATE OPERATION')
    user.name = 'Zeq Updated'
    session.flush()
    session.commit()

    print('\nUPDATE OPERATION')
    user.name = 'Zeq Updated'
    session.flush()

    print('\nDELETE OPERATION')
    session.delete(user)
    session.flush()
    session.commit()

    print('\nROLLBACK OPERATION')
    user1 = User(name='Zeq')
    session.add(user1)

    user2 = User(name='Zeq')  # 🚨 Violates UNIQUE constraint
    session.add(user2)
    session.commit()  # This will fail!

except Exception as e:
    print(f'❌ Error: {e}')
    session.rollback()
