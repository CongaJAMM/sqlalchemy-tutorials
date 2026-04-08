# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=TWYurzVQCwg

"""
SQLAlchemy Query Filtering: Advanced Logical Predicates

This module demonstrates the various methods used to narrow down database 
results. It highlights the differences between legacy 'filter' methods and 
modern 'where' clauses, while implementing complex Boolean logic.

Key Architecture Features:
1. filter() vs. filter_by():
   - filter(): Flexible, allows Pythonic expressions (e.g., User.age >= 25).
   - filter_by(): Simple, keyword-based equality only (e.g., age=30).
2. Modern 'where' Syntax: Utilizes the SQLAlchemy 2.0 style 'where' method, 
   which is functionally equivalent to 'filter' but aligns with standard 
   SQL terminology.
3. Logical Operators:
   - and_ / or_ / not_: Function-based wrappers for Boolean logic.
   - Bitwise Operators: Shows the use of '|' (OR), '&' (AND), and '~' (NOT) 
     as shorthand for logical expressions.
4. Composite Filtering: Demonstrates nesting logical operators to build 
   highly specific queries (e.g., NOT this OR (this AND that)).
"""

from models import User, engine
from sqlalchemy import and_, not_, or_
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

# If there is data in the database, don't add more data
if session.query(User).count() < 1:
    session.add(User(name='Iron Man', age=23))
    session.add(User(name='Coding Man', age=56))
    session.add(User(name='Banana Man', age=78))
    session.add(User(name='Zeq', age=99))

    session.commit()

# query all users
users_all = session.query(User).all()
print('All Users:', len(users_all))


# ========================================================================================
print('\nFILTER')
# query all users with age greater than or equal to 25
users_filtered = session.query(User).filter(User.age >= 25).all()
print('Filtered Users:', len(users_filtered))


# ========================================================================================
print('\nFILTER BY')
# query all users with age is equal to 30
# NO CONDITIONALS ALLOWED!!!
users = session.query(User).filter_by(age=30).all()

for user in users:
    print(f'User age: {user.age}')


# ========================================================================================
print('\nWHERE')
# query all users with age is greater than or equal to 30
users = session.query(User).where(User.age >= 30).all()

for user in users:
    print(f'User age: {user.age}')


# ========================================================================================
print('\nOR')
# query all users with age is greater than or equal to 30 OR name is 'Iron Man'
users = session.query(User).where(or_(User.age >= 30, User.name == 'Iron Man')).all()
print(f'Users: {len(users)}')

users = session.query(User).where((User.age >= 30) | (User.name == 'Iron Man')).all()
print(f'Users: {len(users)}')


# ========================================================================================
print('\nAND')
# query all users with age is greater than or equal to 30 and name is 'Iron Man'
users = session.query(User).where(and_(User.age >= 30, User.name == 'Iron Man')).all()

print(f'Users: {len(users)}')


# ========================================================================================
print('\nNOT')
# query all users where the name is not 'Iron Man'
users = session.query(User).where(not_(User.name == 'Iron Man')).all()

print(f'Users: {len(users)}')


# ========================================================================================
print('\nCOMBINE OPTIONS')
users = session.query(User).filter(
    or_(not_(User.name == 'Iron Man'), and_(User.age > 35, User.age < 60))
)

for user in users.all():
    print(f'{user.age} - {user.name}')
