# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=3N9JqtpkFJI

"""Example #3

Self-Referential Many-to-Many Relationship Module (SQLAlchemy ORM - Social Graph Pattern)

This module demonstrates a 'social graph' architecture where a single entity 
(User) relates to other instances of itself through an association table.

Key Concepts:

1. Self-Referential Mapping: 
   A relationship where the 'parent' and 'child' tables are the same. In this 
   case, a User is both the one following and the one being followed.

2. Association Table (Link Table):
   'follower_association' acts as the bridge. It contains two foreign keys 
   pointing back to the 'users' table to resolve the Many-to-Many logic.

3. Primary and Secondary Joins:
   Because the relationship is ambiguous (it points to 'User' twice), we 
   explicitly define 'primaryjoin' to identify the User, and 'secondaryjoin' 
   to identify that User's followers.
"""

from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

db_url = 'sqlite:///ep_06_user_self_database.db'

engine = create_engine(db_url)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class BaseModel(Base):
    """
    Abstract Base Class.
    
    Provides a consistent primary key (ID) for all models in the schema.

    Note:
        Using `__abstract__ = True` tells SQLAlchemy not to create a 'basemodel' 
        table in the database.
    """
    __abstract__ = True
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)


class FollowerAssociation(BaseModel):
    """
    The 'Association Table' for the Many-to-Many relationship.
    
    This table stores the physical links between users. Each row represents 
    one 'follow' action.
    
    Attributes:
        user_id: The ID of the User being followed.
        follower_id: The ID of the User who is doing the following.
    """
    __tablename__ = 'follower_association'

    user_id = Column(Integer, ForeignKey('users.id'))
    follower_id = Column(Integer, ForeignKey('users.id'))


class User(BaseModel):
    """
    Represents the 'users' table and the social relationship logic.
    
    This model uses a 'Secondary' relationship through FollowerAssociation 
    to enable a User to have a list of other Users as 'followers'.

    ORM Attributes:
        followers (relationship): A collection of User objects. This is 
            populated by joining the 'users' table to the 'follower_association' 
            table twice to differentiate between the user and their followers.
    """
    __tablename__ = 'users'

    username = Column(String)
    followers = relationship(
        'User',
        secondary='follower_association',
        primaryjoin=('FollowerAssociation.user_id==User.id'),       # Links the current User to the Association Table
        secondaryjoin=('FollowerAssociation.follower_id==User.id'),       # Links the follower User to the Association Table
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


Base.metadata.create_all(engine)

# If there is data in the database, don't add more data
if session.query(User).count() < 1:
    # Creating users
    user1 = User(username='Zeq Tech 1')
    user2 = User(username='Zeq Tech 2')
    user3 = User(username='Zeq Tech 3')

    # Creating relationships
    user1.followers.append(user2)
    user1.followers.append(user3)
    user2.followers.append(user3)
    user3.followers.append(user1)

    # Adding users to the session and committing changes to the database
    session.add_all([user1, user2, user3])
    session.commit()

user1, user2, user3 = session.query(User).limit(3).all()

print(f'{user1.followers = }')
print(f'{user2.followers = }')
print(f'{user3.followers = }')
