# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=xRfupYowU-I

"""Example #1

SQLAlchemy One-to-One (1:1) Relationship Module

This module demonstrates how to constrain a relationship so that one parent 
row is associated with exactly one child row. This is commonly used for 
separating sensitive data (like User vs. Profile/Credentials) or 
organizing optional extended attributes.

Key Concepts:
1. 'uselist=False': 
   The defining feature of a 1:1 relationship in SQLAlchemy. By setting this 
   on the 'One' side (User), SQLAlchemy converts the collection from a list 
   to a single scalar object.

2. Bidirectional Mapping: 
   Using `back_populates` on both sides ensures that if you set `user.address`, 
   the `address.user` is updated instantly in memory.

3. Foreign Key Placement:
   In a 1:1 relationship, the Foreign Key typically sits on the "Child" 
   table (Address), which points back to the "Parent" (User).
"""

from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

engine = create_engine('sqlite:///ep_07_one_to_one_relationships.db')
Base = declarative_base()


class User(Base):
    """
    Represents the 'users' table (The Parent).
    
    In this 1:1 schema, each user is restricted to a single associated address.

    ORM Attributes:
        address (relationship): A scalar (single) object link to an Address. 
            Because 'uselist=False' is set, calling 'user.address' returns 
            ONE object instead of a list.
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    # 'uselist=False' turns this from One-to-Many into One-to-One
    address = relationship('Address', back_populates='user', uselist=False)


class Address(Base):
    """
    Represents the 'addresses' table (The Child).
    
    Stores extended information for a specific User.

    SQLAlchemy Attributes:
        user_id (ForeignKey): The physical link to the 'users' table.
        user (relationship): The Python link back to the owner.
    """
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)

    # Typically declared in the "Child" table
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='address')


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# If there is data in the database, don't add more data
if session.query(User).count() < 1:
    new_user = User(name='John Doe')
    new_address = Address(email='john@example.com', user=new_user)
    session.add(new_user)
    session.add(new_address)
    session.commit()

user = session.query(User).filter_by(name='John Doe').first()
print(f'User: {user.name}, Address: {user.address.email}')
