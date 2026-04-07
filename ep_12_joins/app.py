# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=KgvXgstWz98

"""
SQLAlchemy Joins Module: The 4 Main Join Types

This module demonstrates how to combine data from 'User' and 'Address' tables 
using various SQL join strategies. In a relational database, 'joins' allow 
you to create a temporary result set that spans multiple tables.

1. INNER JOIN (The Filter)
   - Behavior: Returns rows ONLY when there is a match in BOTH tables.
   - Scenario: Finding users who have a registered address.
   - Result: Users without addresses and addresses without users are excluded.

2. LEFT OUTER JOIN (The "Keep Left")
   - Behavior: Returns all rows from the 'Left' table (User), plus matched 
     rows from the 'Right' table (Address). If no match exists, the right 
     side is NULL.
   - Scenario: Getting a list of all users and their addresses if they have one.
   - Result: Every user is shown at least once.

3. RIGHT OUTER JOIN (The "Keep Right")
   - Behavior: Returns all rows from the 'Right' table (Address), plus matched 
     rows from the 'Left' table (User). If no match exists, the left side is NULL.
   - Scenario: Finding all addresses in the system, even those not assigned to a user.
   - Result: Every address is shown at least once.

4. FULL OUTER JOIN (The "Keep Everything")
   - Behavior: Returns all rows from both tables. It fills in NULLs where 
     matches are missing on either side.
   - Scenario: An audit of all people and all locations, regardless of association.
   - Note: In SQLite, this is often emulated via a UNION of a Left and Right join.

5. ANTI-JOINS (The "Exclusion" Joins)
   - Behavior: Uses a Join combined with a NULL filter to find records that 
     DO NOT have a match.
   - Scenario: Finding 'orphaned' addresses or 'address-less' users.
"""

from typing import Optional

from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)

engine = create_engine('sqlite:///ep_12_joins.db')
session = sessionmaker(bind=engine)()


class Base(DeclarativeBase):
    """
    Common Base for all models.
    
    Includes a standardized ID primary key and a clean __repr__ 
    for readable terminal output during join debugging.
    """
    id: Mapped[int] = mapped_column(primary_key=True)

    def __repr__(self) -> str:
        return f'< {self.__class__.__name__} id: {self.id}>'


class Address(Base):
    """
    Represents the 'addresses' table.
    
    Attributes:
        user_id (Mapped[Optional[int]]): The foreign key. Because it is 
            Optional, we can have "orphaned" addresses that don't belong 
            to any specific user—ideal for testing Right Joins.
        data (Mapped[str]): The actual address text.
    """
    __tablename__ = 'addresses'

    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey('users.id'))
    data: Mapped[str]


class User(Base):
    """
    Represents the 'users' table.
    
    Attributes:
        first_name / last_name: Standard user identifying data.
        address (relationship): A One-to-One link to the Address model. 
            Because this is not a list, it represents a scalar relationship.
    """
    __tablename__ = 'users'

    first_name: Mapped[str]
    last_name: Mapped[str]
    address: Mapped[Address] = relationship()


# Create the database tables
Base.metadata.create_all(engine)

# If there is data in the database, don't add more data
if session.query(User).count() < 1:
    # This address IS used
    address_1 = Address(data='1234 Random Address')

    # These addresses are NOT used
    address_2 = Address(data='5678 Non-existant Address')
    address_3 = Address(data='9012 Extra Address')

    # User with an address
    user_1 = User(
        first_name='Zeq',
        last_name='Tech',
        address=address_1,
    )

    # User without an address
    user_2 = User(
        first_name='Banana',
        last_name='Man',
        address=None,
    )

    session.add_all([address_1, address_2, address_3, user_1, user_2])
    session.commit()


# ===== INNER JOIN =====
# Return all the users that have addresses
result = session.query(User).join(Address).all()
print('\nINNER JOIN')
print(result)

result = (
    session.query(User, Address).join(Address).all()
)  # What it returns: A list of Tuples. Each item in the list looks like: (<User id: 1>, <Address id: 10>).
# Just in case you need the Addresses at the same time.

# Same as:
# result = ( session.query(User, Address).join(Address).all())
print('\nINNER JOIN TUPLE')
print(result)


# ===== ANTI INNER JOIN - Inverse =====
# Return all the users that don't have addresses
# and all Addresses that don't have users
result = (
    session.query(User, Address)
    .join(Address, full=True)
    .filter(User.address is None, Address.user_id == None)
    .all()
)
print('\nANTI INNER JOIN - Inverse')
print(result)


# ===== LEFT OUTER JOIN AKA "LEFT JOIN" =====
# Return all users regardless if they have addresses or not
result = (
    session.query(User, Address).outerjoin(Address, User.id == Address.user_id).all()
)

# Same as
# result = session.query(User).join(Address, isouter=True).all()

print('\nLEFT OUTER JOIN')
print(result)


# ===== LEFT OUTER JOIN AKA  =====
# Return all users that do not have an address
result = session.query(User).outerjoin(Address).filter(User.address == None).all()

print('\nLEFT OUTER JOIN: Users without an Address')
print(result)

# Same as
# result = session.query(User).join(Address, isouter=True).all()

print('\nLEFT OUTER JOIN')
print(result)


# ===== ANTI LEFT OUTER JOIN - Inverse =====
# Return all users regardless if they have addresses or not
result = (
    session.query(User, Address).outerjoin(Address).filter(User.address == None).all()
)
print('\nANTI LEFT OUTER JOIN - Inverse')
print(result)


# ===== RIGHT OUTER JOIN =====
# Return all addresses regardless if they have users or not
# If a user is linked to it, put their full Name/Profile next to it. If no one lives there, leave the User side blank (NULL)."
result = session.query(Address, User).outerjoin(User).all()
print('\nRIGHT OUTER JOIN')
print(result)


# ===== ANTI RIGHT OUTER JOIN - Inverse =====
# Return all addresses regardless if they have users or not
result = (
    session.query(Address, User).outerjoin(User).filter(Address.user_id == None).all()
)
print('\nANTI RIGHT OUTER JOIN - Inverse')
print(result)


# ===== FULL OUTER JOIN AKA 'FULL JOIN' =====
# SQLAlchemy doesn't support Full Outer Join directly,
# but it can be achieved with UNION
left_join = session.query(User, Address).outerjoin(Address)  # Gets all Users
right_join = session.query(User, Address).outerjoin(User)  # Gets all Addresses
full_outer_join = left_join.union(right_join)  # Combines results
print('\nFULL JOIN')
print(full_outer_join.all())

# Cleaner Method
# This will return all rows, regardless if there is a user associated with the Address
# or regardless if there is an address associated with a user
result = session.query(User, Address).join(Address, isouter=True, full=True).all()
print('\nFULL JOIN')
print(result)
