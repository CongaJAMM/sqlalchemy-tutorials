# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=ftbYlej2xQY

"""
SQLAlchemy Aggregation: Grouping, Functions, and Dynamic Chaining

This module demonstrates how to perform server-side data summaries using 
SQL 'GROUP BY' and 'func' aggregates. It also highlights the power of 
incremental query building for highly dynamic application logic.

Key Architecture Features:
1. SQL Aggregates (sqlalchemy.func):
   Utilizes 'func.count' to perform calculations directly within the 
   database engine, reducing the amount of data transferred to Python.
2. The 'group_by' Clause:
   Collapses multiple rows with the same value into single summary rows, 
   allowing for statistical analysis (e.g., "How many users are age 25?").
3. Method Chaining:
   Shows how '.filter()', '.group_by()', and '.order_by()' can be 
   interleaved. The order of these methods in Python creates a 
   predictable and robust SQL execution plan.
4. Conditional Query Building:
   Demonstrates the 'Lazy Builder' pattern, where the final SQL query 
   is assembled piece-by-piece using 'if' statements before the 
   terminal '.all()' call is ever made.
"""

from models import User, engine
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

# If there is data in the database, don't add more data
if session.query(User).count() < 1:
    session.add(User(name='Iron Man', age=23))
    session.add(User(name='Coding Man', age=33))
    session.add(User(name='Banana Man', age=78))
    session.add(User(name='Zeq', age=99))

    session.commit()


# ========================================================================================
print('\nGROUP BY (AGE,)')
users_count_by_age = session.query(User.age).group_by(User.age).all()
print(users_count_by_age)


# ========================================================================================
print('\nGROUP BY ADDITIONAL CRITERIA (AGE, COUNT)')
# count the number of users by age
users_count_by_age = (
    session.query(User.age, func.count(User.id)).group_by(User.age).all()
)
print(users_count_by_age)


# ========================================================================================
print('\nCHAINING METHODS')
"""SQLAlchemy is smart enough to reorganize these into a valid SQL structure:

FROM the table

WHERE filters are applied

GROUP BY the buckets

ORDER BY the results
"""
users = session.query(User).filter(User.age > 24).filter(User.age < 50).all()

for user in users:
    print(f'{user.age = }')

# or like this
users_tuple = (
    session.query(User.age, func.count(User.id))
    .filter(User.age > 24)
    .order_by(User.age)
    .filter(User.age < 50)
    .group_by(User.age)
    .all()
)
for age, count in users_tuple:
    print(f'Age: {age} - Users: {count}')


# ========================================================================================
print('\nDELAY .all()')
only_iron_man = True
group_by_age = True

users = session.query(User)
if only_iron_man:
    users = users.filter(User.name == 'Iron Man')
if group_by_age:
    users = users.group_by(User.age)
users = users.all()
for user in users:
    print(f'User age: {user.age}, name: {user.name}')
