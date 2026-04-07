# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=WKbJ1txwmeQ

"""Example #3

SQLAlchemy Deferred Raiseload Module

This module demonstrates the 'strict' mode for deferred columns. It is the 
column-level equivalent of 'lazy=raise' for relationships. 

Key Concepts:
1. Hard Constraints:
   By setting 'raiseload=True', you prevent SQLAlchemy from ever emitting 
   a "hidden" secondary SELECT statement for a specific column.

2. Explicit Data Access:
   If you need a raiseload-deferred column, you MUST use the 'undefer()' 
   option in your query. If you forget, the application will crash 
   immediately upon attribute access.

3. Performance Auditing:
   This is the best tool for identifying exactly where your application 
   is relying on inefficient lazy loading. It forces developers to be 
   explicit about every byte of data requested from the database.
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

engine = create_engine('sqlite:///ep_11_deferred_raiseload.db', echo=True)
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
    Represents the 'users' table with 'Raise-on-Access' column deferral.
    
    This model acts as a security and performance gatekeeper, ensuring 
    heavy columns are never fetched by accident.

    ORM Attributes:
        nickname (Mapped[str]): Standard column, always available.
            
        first_name (Mapped[str]): Deferred with raiseload=True. 
            Accessing 'user.first_name' will raise a 
            'sqlalchemy.exc.InvalidRequestError' if not eagerly loaded.
            
        last_name (Column): Legacy syntax with raiseload=True.
            
        other_value (Mapped[str]): Modern keyword syntax 
            (deferred_raiseload=True). This is the cleanest 2.0 approach.

    Raises:
        (sqlalchemy.exc.InvalidRequestError): Raised if accessing 'user.first_name' without eagerly loading.
    """
    __tablename__ = 'users'

    # Always loaded
    nickname: Mapped[str] = mapped_column(String)
    
    # Raiseload Option 1: Wrapping mapped_column
    first_name: Mapped[str] = deferred(mapped_column(String), raiseload=True)
    
    # Raiseload Option 2: Legacy Column style
    last_name = deferred(Column(String), raiseload=True)
    
    # Raiseload Option 3: Modern keyword argument (Recommended)
    other_value: Mapped[str] = mapped_column(
        String, deferred=True, deferred_raiseload=True
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

try:
    # Will raise an error since there is lazy loading
    user = session.query(User).first()
    print(user)
    print(user.first_name)
    print(user.last_name)
    print(user.other_value)
except Exception as e:
    print('*' * 60)
    print('Raiseload error:')
    print(e)
    print('*' * 60)

try:
    # Will raise an error since there is lazy loading
    user = (
        session.query(User)
        .options(undefer(User.first_name), undefer(User.last_name))
        .first()
    )
    print(user)
    print(user.first_name)
    print(user.last_name)
    print(user.other_value)
except Exception as e:
    print('*' * 60)
    print('Raiseload error:')
    print(e)
    print('*' * 60)

# close the session to show deferring
session.close()

# Undefer all values so raiseload doesnt raise an error
user = (
    session.query(User)
    .options(
        undefer(User.first_name),
        undefer(User.last_name),
        undefer(User.other_value),
    )
    .first()
)
print(user)
print(user.first_name)
print(user.last_name)
print(user.other_value)
