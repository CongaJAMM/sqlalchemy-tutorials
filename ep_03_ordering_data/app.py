# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=HY2GSa9aP_U

"""
SQLAlchemy Query Ordering: Sorting Data with order_by

This module demonstrates how to control the sequence of records returned 
from the database. Sorting is a critical aspect of data retrieval, 
ensuring that results are presented in a logical and readable order.

Key Architecture Features:
1. Dynamic Data Population: Uses the 'random' module to generate a 
   diverse dataset, providing a practical environment for testing 
   sorting algorithms.
2. Directional Sorting:
   - ASC (Default): Arranges data from smallest to largest (e.g., 20 -> 60).
   - DESC: Arranges data from largest to smallest (e.g., 60 -> 20).
3. Multi-Level Ordering:
   Demonstrates how to chain columns in 'order_by' to handle "ties." 
   For example, if multiple users are 25 years old, they can be further 
   sorted alphabetically by name.
4. Python Object mapping: Shows that 'order_by' returns a list of 
   fully-hydrated User objects in the requested sequence.
"""

import random  # NEW
from models import User, engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

names = ['Andrew Pip', 'Iron Man', 'John Doe', 'Jane Doe']
ages = [20, 21, 22, 23, 25, 27, 30, 35, 60]


# If there is data in the database, don't add more data
if session.query(User).count() < 1:
    # Create random Users
    for x in range(20):
        user = User(name=random.choice(names), age=random.choice(ages))
        session.add(user)

    session.commit()  # SAVE to the Database


# Query all users ordered by age (ascending)
users_1 = session.query(User).order_by(User.age).all()
# this is the same as:
# users_1 = session.query(User).order_by(User.age.asc()).all()

print('\nAll Users Ordered by age (ASCENDING)')
for user in users_1:
    print(user)

# Query all users ordered by age (descending)
users_2 = session.query(User).order_by(User.age.desc()).all()
print('\nAll Users Ordered by age (DESCENDING)')
for user in users_2:
    print(user)

# Order first by age and then name
users = session.query(User).order_by(User.age, User.name).all()
print('\nAll Users Ordered by age (ASCENDING) and then name (ASCENDING)')
for user in users:
    print(user)
