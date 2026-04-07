# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=_cHSW_ehjtY

"""Example #2

SQLAlchemy Event Listeners: Mapper Lifecycle Hooks

This module demonstrates how to intercept ORM events—specifically the 
'before_update' event—to perform data auditing. Events allow you to 
decouple side-effect logic (like logging changes) from your main 
business logic.

Key Concepts:
1. The @event.listens_for Decorator:
   The most common way to register a listener. It attaches a function 
   to a specific 'target' (like a Class or Engine) and an 'identifier' 
   (the specific event name).

2. Mapper Events:
   Events like 'before_insert', 'before_update', and 'after_delete' are 
   triggered by the Mapper as it flushes changes to the database.

3. The Connection Object:
   Listeners often provide a 'Connection' object. This allows you to 
   execute raw SQL to check the *current* state of the database before 
   the new changes are committed, which is essential for "old vs new" 
   value comparisons.

4. Decoupling:
   By using events, your 'User' model doesn't need to know about 
   auditing logic. The audit happens automatically whenever a User 
   record is updated anywhere in the application.
"""

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, mapped_column, Mapped, DeclarativeBase, Mapper
from sqlalchemy.engine import Connection

engine = create_engine('sqlite:///:memory:')


class Base(DeclarativeBase):
    """Declarative Base for ORM models."""
    id: Mapped[int] = mapped_column(primary_key=True)


class User(Base):
    """
    Represents the 'users' table.
    
    The audit listener defined below will watch this class for any 
    updates to its attributes.
    """
    __tablename__ = 'users'
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)


# Add an event through a decorator
@event.listens_for(User, 'before_update')
def audit_user_update(mapper: Mapper, connection: Connection, target: User):
    """
    Listener that intercepts User updates to log email changes.

    Arguments:
        mapper (Mapper): The Mapper object managing the User class.
        connection (Connection): The active database connection being used 
            for the flush. Used here to query the "pre-update" data.
        target (User): The actual instance of the User being updated.
    """

    # 1. Fetch the 'old' value directly from the DB using the connection
    stmt = text('SELECT email FROM users WHERE id = :user_id')  # Using raw SQL string
    old_email = connection.scalar(stmt, {'user_id': target.id})

    # 2. Access the 'new' value from the Python object
    new_email = target.email
    if new_email != old_email:
        print(f'Email changed for user {target.id}: {old_email} -> {new_email}')



Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

if not event.contains(User, 'before_update', audit_user_update):
    event.listen(User, 'before_update', audit_user_update)
    print("Listener Added")
else:
    print("Listener already exists")

# Remove event listener
# event.remove(User, 'before_update', audit_user_update)

user = User(name='User 1', email='user_1@example.com')
session.add(user)
session.commit()

user = session.query(User).filter_by(name='User 1').first()
user.email = 'user_updated@example.com'
session.commit()
