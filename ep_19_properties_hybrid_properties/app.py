# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=YSFODnf_eoA

"""
SQLAlchemy Hybrid Attributes and Methods Module

This module demonstrates the use of the 'hybrid' extension to create attributes 
and methods that behave differently depending on the context:
1. Instance Context: When accessed on a Python object (e.g., user.full_name).
2. Class/Query Context: When used in an ORM query (e.g., session.query(User).filter(...)).

Key Concepts:
- hybrid_property:
  Allows a method to be treated as an attribute. In Python, it executes 
  standard logic. In SQL, it generates a column-level expression (like 
  concatenation) for the database to execute.

- hybrid_method:
  Similar to a property but accepts arguments. It allows you to build 
  complex filtering logic (like age calculations) that works both in 
  memory and in the WHERE clause of a SQL statement.

- Performance:
  Hybrids keep your "Source of Truth" in the model. You don't have to 
  manually rewrite SQL strings that match your Python logic; SQLAlchemy 
  handles the translation automatically.
"""

from sqlalchemy.orm import Session
from models import User, engine, Base

Base.metadata.create_all(engine)

with Session(engine) as session:
    if session.query(User).count() < 1:
      session.add_all(
          [
              User(first_name='Zeq', last_name='Tech', birth_year=1995),
              User(first_name='Alan', last_name='Walker', birth_year=1997),
          ]
      )
      session.commit()

    zeq = session.query(User).first()

    # ✅ Works in Python
    print(zeq.full_name)

    # ✅ Using Hybrid Properties to work in SQL filters
    print(session.query(User).filter(User.full_name == 'Zeq Tech').all())
    print(session.query(User).filter(User.full_name.like('Zeq%')).all())
    # The % is a wildcard character in SQL, matching any
    # sequence of characters after 'Zeq'

    # Hybrid method example in Python
    print(zeq.older_than(25))

    # Hybrid method example in SQL filters
    print(session.query(User).filter(User.older_than(25)).all())
