# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=3N9JqtpkFJI

"""Example #4

User-Post One-to-Many Relationship Module (SQLAlchemy ORM)

This module demonstrates a foundational 'Content Management' schema where 
users can create and own multiple content entries (Posts). 

Key Concepts:
1. One-to-Many Mapping: 
   A single 'User' entity can be associated with an infinite number of 'Post' 
   entities. This is the most common relationship in web applications.

2. Bidirectional Navigation (back_populates):
   By using `back_populates`, the ORM keeps both sides of the relationship 
   synchronized in Python's memory. Updating `post.user` automatically 
   updates the `user.posts` collection.

3. Foreign Key Persistence:
   The 'posts' table stores a `user_id` to maintain a physical link to the 
   owner in the 'users' table.

Usage:
    - Run the script to initialize a SQLite database.
    - Demonstrates object creation, relationship appending, and session committing.
"""

from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

db_url = 'sqlite:///ep_06_user_post_database.db'

engine = create_engine(db_url)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class BaseModel(Base):
    """
    Abstract Base Class for Schema Consistency.
    
    Attributes:
        id: Standard Integer Primary Key assigned to every child model.
    
    Note:
        Using `__abstract__ = True` tells SQLAlchemy not to create a 'basemodel' 
        table in the database.
    """
    __abstract__ = True
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)


class Post(BaseModel):
    """
    ORM Model for the 'posts' table.
    
    Represents individual pieces of content created by a user. This class 
    functions as the 'Many' side of the relationship.

    SQLAlchemy Attributes:
        user_id: The Foreign Key column used by the database to identify the owner.
        user: The Python relationship used to access the parent User object 
              (e.g., my_post.user.name).
    """
    __tablename__ = 'posts'

    title = Column(String)
    content = Column(String)
    likes = Column(Integer)
    dislikes = Column(Integer)

    user_id = Column(ForeignKey('users.id'))
    user = relationship('User', back_populates='posts')

    def __repr__(self):
        return f"<Post (id={self.id}, title='{self.title}')>"


class User(BaseModel):
    """
    ORM Model for the 'users' table.
    
    Represents the content creator. This class functions as the 'One' side 
    of the relationship.

    SQLAlchemy Attributes:
        posts: A virtual collection (list) of Post objects. SQLAlchemy 
               automatically fetches these by matching the User's ID to 
               the 'user_id' in the posts table.
    """
    __tablename__ = 'users'

    name = Column(String)
    age = Column(Integer)
    posts = relationship(Post)

    def __repr__(self):
        return f"<User(id={self.id}, age='{self.age}')>"


Base.metadata.create_all(engine)

session = Session()

# If there is data in the database, don't add more data
if session.query(User).count() < 1:
    # Creating user
    user = User(name='Zeq Tech', age=999)

    # Creating addresses
    post = Post(
        title='Subscribe', content='Subscribe to Zeq Tech!', likes=999, dislikes=0
    )

    # Associating addresses with users
    user.posts.append(post)

    # Adding users and addresses to the session and committing changes to the database
    session.add(user)
    session.commit()

post = session.query(Post).first()
user = session.query(User).first()

print(f'{post.user = }')
print(f'{user.posts = }')
