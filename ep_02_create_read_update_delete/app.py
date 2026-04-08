# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=f0-kEG37GE0

"""
SQLAlchemy ORM Operations: The CRUD Lifecycle and Session Management

This module demonstrates how to interact with database records using the 
SQLAlchemy Session. It covers the fundamental persistence operations and 
provides a deep dive into how Query objects behave before execution.

Key Architecture Features:
1. Session Factory (sessionmaker):
   Establishes a 'Session' factory bound to the engine. The Session acts 
   as a "Unit of Work," tracking changes to objects and managing 
   database transactions.

2. CRUD Operations:
   - Create: Using 'session.add()' and 'session.add_all()' to move transient 
     objects into the session.
   - Read: Using 'session.query()' to retrieve data with various filters.
   - Update: Modifying Python object attributes; the Session detects these 
     changes automatically (Dirty Tracking).
   - Delete: Using 'session.delete()' to mark records for removal.

3. Transaction Control:
   Demonstrates the importance of 'session.commit()' to persist changes 
   permanently to the disk, and implicit flushing of data.

4. The Query Object & Lazy Execution:
   Explains that 'session.query(User)' creates a SQL builder (Query object) 
   rather than executing a command immediately. SQL is only emitted when 
   a 'terminal method' (like .all(), .first(), or .count()) is called.
"""

from models import User, engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)  # Create the Session Factory
session = Session()  # Use the Factory to create a SQLAlchemy ORM Session


# ===================================================================================
# CREATE

# If there is data in the database, don't add more data
if session.query(User).count() < 1:
    # Create one new User
    user = User(name='John Doe 1', age=30)
    session.add(user)
    session.commit()

    # Create multiple Users
    user_1 = User(name='John Doe 2', age=30)
    user_2 = User(name='Andrew Pip', age=25)
    user_3 = User(name='Iron Man', age=57)
    user_4 = User(name='Richard Rodriguez', age=25)

    session.add(user_1)
    session.add(user_2)
    session.add_all([user_3, user_4])
    session.commit()  # Saves to the Database


# ===================================================================================
# READ
# query all users
users = session.query(User).all()
print(users)

# Get the first User info
user = users[0]
print(user)
print(user.id)
print(user.name)
print(user.age)

user = session.query(User).filter_by(id=1).one_or_none()
print(user)

# Loop over each User
for user in users:
    print(f'User id: {user.id}, name: {user.name}, age: {user.age}')

# Get first user from the data
user_first = session.query(User).first()
print('First User: ', user_first)


# ===================================================================================
# UPDATE
# update a user's name
user = users[0]
user.name = 'Jane Doe'
session.commit()


# ===================================================================================
# DELETE
# delete a user record
user = users[0]
session.delete(user)
session.commit()



# ===================================================================================
# QUERY OBJECT
print("\n\nUnderstanding the QUERY OBJECT:")
users = session.query(User)   # This does NOT query/hit the database yet.
    # It returns a Query object (a lazy SQL builder).

print(f"This is the return type: {type(users)}")

# Can chain operations to build the query

users = users.order_by(User.id.desc())      # Still no SQL executed yet!!
users = users.limit(5)                      # Still no SQL executed yet!!


# The database is only hit WHEN YOU CALL A TERMINAL METHOD:
"""
users.all()      # → returns list[User]
users.first()    # → returns one User or None
users.one()      # → exactly one or raises error
users.count()    # → returns integer
users.scalar()   # → returns single value
"""

result = users.all()        # NOW SQL EXECUTES THE QUERY
print(f"Result of the query chain: \n{result}")
