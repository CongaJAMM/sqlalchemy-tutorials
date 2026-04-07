# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=KNxVG4OcboY


"""Example #3

SQLAlchemy Relationship Loading: Joined Eager Loading ('joined')

This module demonstrates 'Eager Loading' via a SQL JOIN. This strategy pulls 
data from multiple tables into a single result set, ensuring the application 
has all necessary information after exactly one query.

Core Concept: Joined Loading (lazy='joined')
    - SQLAlchemy emits a single SELECT statement with a LEFT OUTER JOIN.
    - Result: The parent (User) and the child (Post) data arrive together 
      in one big table of results.
    - Deduplication: SQLAlchemy's ORM layer automatically handles the "row 
      duplication" that happens in SQL joins, giving you clean Python objects.

Advantages:
    - Single Query: Only 1 trip to the database. Perfect for high-latency 
      network connections.
    - Zero N+1 Problem: Related objects are ready the moment the parent 
      object is created.

Disadvantages:
    - Cartesian Product: If a User has 100 posts, the User's data (name, id) 
      is repeated 100 times in the raw SQL result, which can be a massive 
      WASTE of bandwidth.
    - Complexity: Large joins across many tables can be very slow for the 
      database engine to calculate.

When to Use:
    - One-to-One (1:1) or Many-to-One (N:1) relationships.
    - When you know you are fetching a small number of parent records.
    - When you always need the related object (e.g., a User and their Profile).
"""


from sqlalchemy import Column, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

db_url = 'sqlite:///ep_09_joined_database.db'

engine = create_engine(db_url, echo=True)   # Watch the LEFT OUTER JOIN in the logs!

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class User(Base):
    """
    Represents the 'users' table.
    
    ORM Attributes:
        latest_post (relationship): Configured with lazy='joined' and uselist=False.
            This creates a 1:1 relationship that is automatically fetched 
            using a SQL JOIN whenever a User is queried.
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    # Joined loading is ideal for 1:1 links like 'latest_post'
    latest_post = relationship('Post', uselist=False, lazy='joined')

    def __repr__(self):
        return f'<User {self.name} >'


class Post(Base):
    """
    Represents the 'posts' table.
    
    In this schema, it acts as the 'latest_post' for a user. Its columns 
    are merged into the User query result via the JOIN.
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
                name=f'User {x}',
                latest_post=Post(content=f'This is the content for {x}'),
            )
            for x in range(10)
        ]
    )
    session.commit()

users = session.query(User).all()
for user in users:
    print(user.name, user.latest_post.content)  # Accessing the latest post directly
