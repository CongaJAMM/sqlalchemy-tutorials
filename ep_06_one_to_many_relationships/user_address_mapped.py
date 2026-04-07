# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=3N9JqtpkFJI

"""Example #2

Database Models Module (SQLAlchemy 2.0 ORM)

This module defines the schema for the PostgreSQL database using SQLAlchemy's 2.0
Declarative Mapping system. It serves as the "Source of Truth" for both the 
physical database tables and the Python objects.

Key Concepts:
1. Object-Relational Mapping (ORM): 
   Each class represents a table (e.g., User -> 'users'). Each instance of a 
   class represents a single row in that table.

2. Mapped & mapped_column (Type Safety):
   Using `Mapped[type]` allows IDEs and static type checkers (like Mypy) to 
   validate data types before the code even runs. It bridges the gap between 
   Python's dynamic typing and SQL's strict typing.

3. Relationships & Foreign Keys:
   - Foreign Keys (e.g., user_id) are the physical constraints in the database 
     ensuring referential integrity.
   - Relationships (e.g., user, addresses) are 'virtual' properties that 
     allow for high-level navigation between related objects without 
     writing manual JOIN queries.

Relationships Overview:
    User (One) <---> (Many) Address
    - A User can have multiple Addresses.
    - Each Address belongs to exactly one User.

"""

from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import (
    Mapped,
    declarative_base,
    mapped_column,
    relationship,
    sessionmaker,
)       # UPDATED

db_url = 'sqlite:///ep_06_user_address_database.db'

engine = create_engine(db_url)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


# === DATABASE CLASSES ===

class BaseModel(Base):
    """
    An abstract base class providing common functionality for all models.
    
    Attributes:
        id: The Primary Key. In SQLAlchemy 2.0, this remains a 'Column' or 
            can be converted to 'mapped_column(Integer, primary_key=True)'.
    
    Note:
        '__abstract__ = True' prevents SQLAlchemy from creating a physical 
        table for this class.
    """
    __abstract__ = True
    # REMOVED '__allow_unmapped__ = True'
    id = mapped_column(Integer, primary_key=True)  # UPDATED


class Address(BaseModel):
    """
    ORM Model for the 'addresses' table.
    
    This class represents the 'Many' side of the relationship. Using Mapped 
    types ensures that Python's type checker understands the data structures.

    Attributes:
        user_id: A Mapped integer column containing the Foreign Key. This is the 
                physical database link to 'users.id'.
        user: A Mapped relationship that holds a single 'User' object. 
              SQLAlchemy populates this by 'joining' to the users table.
    """
    __tablename__ = 'addresses'

    city = Column(String)
    state = Column(String)
    zip_code = Column(Integer)
    street = Column(String)

    #  FOREIGN KEY
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))       # UPDATED


    user: Mapped['User'] = relationship(back_populates='addresses')    # UPDATED

    def __repr__(self):
        return f"<Address (id={self.id}, city='{self.city}')>"


class User(BaseModel):
    """
    ORM Model for the 'users' table.
    
    This class represents the 'One' side of the relationship. It uses 
    Python type hinting (Mapped[list[...]]) to define the collection.

    Attributes:
        addresses: A Mapped collection containing a list of 'Address' objects.
                   This is a 'virtual' attribute used by the ORM to fetch 
                   related rows without writing manual JOIN queries.
    """
    __tablename__ = 'users'

    name = Column(String)
    age = Column(Integer)

    addresses: Mapped[list['Address']] = relationship(back_populates='user')  # UPDATED

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

address1 = session.query(Address).first()
user1, user2 = session.query(User).limit(2).all()

print(f'address1: {address1.user = }')
print(f'user1:    {user1.addresses = }')
print(f'user2:    {user2.addresses = }')
