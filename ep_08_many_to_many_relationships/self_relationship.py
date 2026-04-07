# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=iosh_DWnliE

"""Example #4

Self-Referential Many-to-Many Relationship Module (Social Graph Pattern)

This module demonstrates how a single entity (User) can relate to other 
instances of itself through an association table. This is the standard 
architecture for "Following/Follower" systems.

Key Concepts:
1. Self-Referential Many-to-Many: 
   Unlike a one-to-one linked list, this allows one user to follow many 
   others, and be followed by many others simultaneously.

2. Junction Table (Association Class): 
   'UserAssociation' stores pairs of IDs. Because both IDs point to the 
   same 'users' table, we must explicitly define which ID represents 
   the "Subject" and which represents the "Object."

3. primaryjoin & secondaryjoin: 
   These are required to tell SQLAlchemy how to navigate the association 
   table. 
   - Primary: Links the current User to the 'follower_id'.
   - Secondary: Links the 'following_id' to the target User.

4. backref: 
   Automatically creates the 'followers' attribute on the User class, 
   mirroring the 'following' relationship in reverse.
"""

from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

db_url = 'sqlite:///ep_08_self_relationship.db'

engine = create_engine(db_url)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class UserAssociation(Base):
    """
    The Association Class for the self-referential many-to-many relationship.
    
    This table acts as the "Link" between two users.
    
    Attributes:
        follower_id: The ID of the User who is performing the "follow" action.
        following_id: The ID of the User who is being followed.
    """
    __tablename__ = 'user_associations'
    id = Column(Integer, primary_key=True)

    follower_id = Column(Integer, ForeignKey('users.id'))
    following_id = Column(Integer, ForeignKey('users.id'))


class User(Base):
    """
    Represents the 'users' table in a social graph.
    
    ORM Attributes:
        following (relationship): A list of User objects that this user follows.
        followers (backref): A list of User objects that follow this user.
                             (Created automatically by the 'backref' argument).
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    # Navigation logic for the social graph
    following = relationship(
        'User',
        secondary='user_associations',
        primaryjoin='UserAssociation.follower_id==User.id',       # Links the current User to the Association Table
        secondaryjoin='UserAssociation.following_id==User.id',       # Links the follower User to the Association Table
        backref='followers',
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.name}')>"


Base.metadata.create_all(engine)

# If there is data in the database, don't add more data
if session.query(User).count() < 1:
    user_1 = User(name='John')
    user_2 = User(name='Rob')
    user_3 = User(name='Kyle')

    user_1.following.append(user_2)
    user_2.following.append(user_1)
    user_3.following.append(user_1)

    session.add_all([user_1, user_2, user_3])
    session.commit()

user_1 = session.query(User).first()

print(f'{user_1} is following: {user_1.following}')
print(f'{user_1} is being followed by: {user_1.followers}')
