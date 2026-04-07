# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=KNxVG4OcboY

"""
SQLAlchemy Relationship Loading Strategy: lazy='raise'

Overview:
---------
The 'raise' loading strategy prevents SQLAlchemy from automatically
loading a relationship when it is accessed.

Instead of silently issuing a SQL query (like lazy='select'),
it raises an exception unless the relationship was explicitly preloaded.

This forces developers to be intentional about when related data is fetched.

---------------------------------------------------------------------

'raise' Default Behavior:
-------------------------
- Accessing the relationship without preloading will raise an exception.
- No implicit SQL queries are executed.
- Helps detect accidental lazy-loading during development.

Example:
    user.sensitive_information  → ❌ Raises error if not preloaded

---------------------------------------------------------------------

'raise' - DISADVANTAGES:
------------------------
- Requires explicit loading every time (more verbose code)
- Can break existing code if not handled properly
- Not beginner-friendly (can feel restrictive)
- Not suitable for commonly accessing related objects

---------------------------------------------------------------------

'raise' - ADVANTAGES:
---------------------
- Prevents N+1 query problems
- Avoids hidden database queries
- Improves performance predictability
- Enforces explicit data loading patterns
- Ideal for protecting sensitive or large datasets

---------------------------------------------------------------------

When to Use:
------------
- Sensitive data (e.g., passwords, tokens, private info)
- Large relationships that should not be loaded accidentally
- Performance-critical applications
- APIs where you want strict control over returned data

---------------------------------------------------------------------

How to Use Correctly:
---------------------

You MUST explicitly load the relationship:

    from sqlalchemy.orm import selectinload

    users = session.query(User).options(
        selectinload(User.sensitive_information)
    ).all()

---------------------------------------------------------------------

Key Takeaway:
-------------
lazy='raise' is a defensive programming tool that ensures
you never accidentally trigger a database query.
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, selectinload

db_url = 'sqlite:///ep_09_raise_database.db'

engine = create_engine(db_url, echo=True)  # important

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class User(Base):
    """
    Represents the 'users' table.
    
    ORM Attributes:
        sensitive_information (relationship): Configured with lazy='raise'.
            Accessing this attribute triggers an immediate Exception unless 
            the relationship was eagerly loaded in the original session query.
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    # Relationship configured with lazy='raise'
    # This prevents accidental access without explicit loading
    sensitive_information = relationship('SensitiveInformation', backref='user', lazy='raise')

    def __repr__(self):
        return f'<User {self.name} >'


class SensitiveInformation(Base):
    """
    Represents the 'sensitive_informations' table.
    
    Contains data that should only be fetched with explicit intent.
    """
    __tablename__ = 'sensitive_informations'
    id = Column(Integer, primary_key=True)
    content = Column(Text)

    # Typically declared in the "Child" table
    user_id = Column(Integer, ForeignKey('users.id'))


Base.metadata.create_all(engine)

# If there is data in the database, don't add more data
if session.query(User).count() < 1:
    session.add_all(
        [
            User(
                name=f'User {y}',
                sensitive_information=[
                    SensitiveInformation(
                        content=f'This is sensitive information for {y * 2 + x}'
                    )
                    for x in range(2)
                ],
            )
            for y in range(10)
        ]
    )
    session.commit()

# IMPORTANT: Reset session so objects are NOT cached
session.close()
session = Session()


# === IMPROPER SENSITIVE_INFORMATION ACCESS ===
users = session.query(User).all()
for user in users:
    print(f"This should fail with {user.name}")
    try:
        for information in user.sensitive_information:  # This will raise an exception
            print(information.content)
    except Exception as e:
        print('Posts cannot be accessed directly:', e)



# === PROPER SENSITIVE_INFORMATION ACCESS ===
users = session.query(User).options(
    selectinload(User.sensitive_information)
).all()     # .options function will be explained in a further episode

for user in users:
    print(f"This should succeed with {user.name}")
    try:
        for info in user.sensitive_information:
            print(info.content)
    except Exception as e:
        print('Posts cannot be accessed directly:', e)
