# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=3N9JqtpkFJI

"""Example #1

SQLAlchemy ORM Relationships: One-to-Many (Example #1)

This module introduces the fundamental concept of Object-Relational Mapping (ORM)
relationships.In a relational database, data is spread across different tables. 
Relationships allow us to link these tables together.

Key Concepts Introduced:

1. One-to-Many Relationship:
   The most common relationship type. One parent (User) can own multiple 
   children (Addresses).

2. Foreign Key (The Physical Link):
   A column in the 'Many' table (Address) that stores the ID of a record in 
   the 'One' table (User). This is the database's "source of truth."

3. Relationship (The Virtual Link):
   A Python property provided by SQLAlchemy that allows you to "walk" between 
   related objects. 
   - User.addresses: Returns a list of Address objects.
   - Address.user: Returns the specific User object the address belongs to.

4. Back-Populates (Synchronization):
   A configuration that ensures if you update one side of the relationship 
   in Python (e.g., assigning a user to an address), the other side updates 
   instantly in memory.


"""

from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

db_url = 'sqlite:///ep_06_user_address_database.db'

engine = create_engine(db_url)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


# === DATABASE CLASSES ===

class BaseModel(Base):
    """
    An abstract base class for all database models.
    
    Attributes:
        id (int): The primary key for every table, ensuring unique identification 
                 of each row.
    
    Note:
        Using `__abstract__ = True` tells SQLAlchemy not to create a 'basemodel' 
        table in the database.
    """
    __abstract__ = True
    __allow_unmapped__ = True       # Enables this non-mapped method

    id = Column(Integer, primary_key=True)


class Address(BaseModel):
    """
    Represents the 'addresses' table in the database (ORM Model).
    
    This class handles the 'Many' side of a One-to-Many relationship with Users.
    Each record contains geographic data and a foreign key pointing to its owner.

    SQLAlchemy ORM Attributes:

        user_id (ForeignKey): The physical database column that links this row 
                              to a specific record in the 'users' table.

        user (relationship): The Python-level object link. Allows access to the 
                             parent User object (e.g., my_address.user.name).
    """
    __tablename__ = 'addresses'

    city = Column(String)
    state = Column(String)
    zip_code = Column(Integer)
    street = Column(String)

    #  FOREIGN KEY
    user_id = Column(ForeignKey('users.id'))    #Creates the physical link between the 2 tables


    user = relationship(
        'User',     # Enables Python tools provided by SQLAlchemy to make your life easier and Connect Objects; Allows my_address.user
        back_populates='addresses'  # Ensures that if you change the user on an address, the user's list of addresses updates instantly in Python's memory
    )

    def __repr__(self):
        return f"<Address (id={self.id}, city='{self.city}')>"


class User(BaseModel):
    """
    Represents the 'users' table in the database (ORM Model).
    
    This class handles the 'One' side of a One-to-Many relationship.
    
    A single user can be associated with multiple Address objects.

    SQLAlchemy ORM Attributes:

        addresses (relationship): A virtual collection of Address objects. 
            SQLAlchemy populates this list by querying the 'addresses' table for matching user_ids.
    """
    __tablename__ = 'users'

    name = Column(String)
    age = Column(Integer)

    addresses = relationship(Address, back_populates='user')  # Create the relationship; Allows my_user.addresses

    def __repr__(self):
        return f"<User(id={self.id}, age='{self.age}')>"


Base.metadata.create_all(engine)
session = Session()


# === CREATE THE DATA, IF NOT ALREADY CREATED ===
# If there is data in the database, don't add more data
if session.query(User).count() < 1:
    # Creating users
    user1 = User(name='John Doe', age=52)
    user2 = User(name='Jane Smith', age=34)

    # Creating addresses
    address1 = Address(
        street='123 Main St', city='New York', state='NY', zip_code='10001'
    )
    address2 = Address(
        street='456 Oak Ave', city='Los Angeles', state='CA', zip_code='90001'
    )
    address3 = Address(
        street='789 Pine Rd', city='Chicago', state='IL', zip_code='60601'
    )

    # Associating addresses with users
    user1.addresses.extend([address1, address2])
    user2.addresses.append(address3)

    # Adding users and addresses to the session and committing changes to the database
    session.add(user1)
    session.add(user2)
    session.commit()


address1 = session.query(Address).order_by(Address.id).first()
user1, user2 = session.query(User).limit(2).all()


print(f'address1: {address1.user = }')
print(f'user1:    {user1.addresses = }')
print(f'user2:    {user2.addresses = }')
