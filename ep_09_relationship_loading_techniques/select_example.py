# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=KNxVG4OcboY


"""Example #1

SQLAlchemy Relationship Loading: Lazy Loading ('select')

This module demonstrates the default lazy-loading relationship strategy in SQLAlchemy: 'select'.
It highlights how the ORM balances initial query speed against potential 
downstream performance bottlenecks.

Core Concept: Lazy Loading (lazy='select')
    - When you query for Users, SQLAlchemy ONLY fetches the user data.
    - The 'posts' attribute is replaced with a "lazy loader" object.
    - A new SQL query is triggered for a specific user's posts ONLY when 
      that attribute is accessed in Python.

The N+1 Problem (The Major Disadvantage):
    - If you have 1,000 users (1 query to get them all), and you loop through 
      them to access their posts, SQLAlchemy will fire 1,000 ADDITIONAL 
      queries (N).
    - Total Queries = 1 (Initial) + 1,000 (Individual fetches) = 1,001 queries.

Advantages:
    - Lightweight Initial Load: Fast if you only need the Parent (User) data.
    - Memory Efficient: Avoids loading thousands of related objects into 
      RAM if they are never used.

When to Use:
    - Accessing related objects is rare or optional.
    - The "Many" side of the relationship is extremely large (e.g., millions 
      of logs), making an eager load impossible.
"""


from time import perf_counter

from sqlalchemy import Column, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

db_url = 'sqlite:///ep_09_database.db'

engine = create_engine(db_url, echo=True)  # important

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class User(Base):
    """
    Represents the 'users' table.
    
    ORM Attributes:
        posts (relationship): Configured with lazy='select' (default).
            Accessing 'user.posts' triggers a separate SELECT statement 
            filtered by the user's ID.
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    # lazy='select' is the default behavior
    posts = relationship('Post', lazy='select', backref='user')

    def __repr__(self):
        return f'<User {self.name} >'


class Post(Base):
    """
    Represents the 'posts' table.
    
    Attributes:
        content (Text): The body of the post.
        user_id (FK): Physical link to the owner.
    """
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    content = Column(Text)

    # Typically declared in the "Child" table
    user_id = Column(Integer, ForeignKey('users.id'))

    def __repr__(self):
        return f'<Post {self.id} >'


Base.metadata.create_all(engine)

# If there is data in the database, don't add more data
if session.query(User).count() < 1:
    session.add_all(
        [
            User(
                name=f'User {y}',
                posts=[
                    Post(content=f'This is the content for {y * 5 + x}')
                    for x in range(5)
                ],
            )
            for y in range(1_000)
        ]
    )
    session.commit()

print('\n\n')

users = session.query(User).all()

print('\n Accessing Posts specifically')
start = perf_counter()

for user in users:
    user.posts      # Accessing the attribute triggers a lazy-load SELECT query 
                        # because the relationship is configured with lazy='select'.

print(f'Done in: {perf_counter() - start}')
