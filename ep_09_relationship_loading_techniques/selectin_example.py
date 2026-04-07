# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=KNxVG4OcboY


"""Example #2

SQLAlchemy Relationship Loading: Select-IN Loading ('selectin')

This module demonstrates 'Eager Loading' via a separate SELECT statement. 
It is the primary solution for preventing the N+1 performance bottleneck 
while keeping the initial query clean.

Core Concept: Select-IN Loading (lazy='selectin')
    - Query 1: Fetches all requested 'User' records.
    - Query 2: Immediately fetches all 'Post' records that belong to the 
      Users found in Query 1 using an 'IN' clause (e.g., WHERE user_id IN (1, 2, 3...)).
    - Result: Only 2 queries are ever executed, regardless of how many 
      users are in the list.

Advantages:
    - Avoids the N+1 Problem: Prevents 1,000+ tiny queries to the database.
    - Performance: Dramatically faster than lazy loading when you know 
      you will need the related objects.
    - Clean Joins: Unlike 'joined' loading, it doesn't create a massive 
      Cartesian product in a single result set.

Disadvantages:
    - Memory Usage: All related 'Post' objects are loaded into Python 
      memory immediately, even if they aren't used.
    - Large IN Clauses: If you fetch 50,000 users, the second query's 
      'IN' clause might become too large for some database drivers.

When to Use:
    - The "Gold Standard" for One-to-Many relationships.
    - When you are certain you will need the child objects (e.g., displaying 
      a list of Users with their Posts).
"""


from time import perf_counter

from sqlalchemy import Column, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

db_url = 'sqlite:///ep_09_selectin_database.db'

engine = create_engine(db_url, echo=True)  # important

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class User(Base):
    """
    Represents the 'users' table.
    
    ORM Attributes:
        posts (relationship): Configured with lazy='selectin'. 
            SQLAlchemy will emit a separate SELECT ... IN query to 
            batch-load all posts for all retrieved users at once.
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    # lazy='selectin' triggers the second batch-query immediately
    posts = relationship('Post', lazy='selectin', backref='user')

    def __repr__(self):
        return f'<User {self.name} >'


class Post(Base):
    """
    Represents the 'posts' table.
    
    The 'Many' side of the relationship. These rows are batch-loaded 
    using the User primary keys.
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
    user.posts

print(f'Done in: {perf_counter() - start}')
