# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=KNxVG4OcboY

"""Example #6

SQLAlchemy Relationship Loading Strategy: lazy='dynamic'

Overview:
---------
The 'dynamic' loading strategy returns a QUERY OBJECT instead of a collection
when accessing a relationship.

Instead of immediately loading related objects into memory (like a list),
it allows you to build and execute queries on-demand.

This is especially useful when working with large datasets where you want
fine-grained control over filtering, ordering, and limiting results.

---------------------------------------------------------------------

'dynamic' Default Behavior:
---------------------------
- Accessing the relationship returns a QUERY OBJECT:
      user.posts   → ✅ Returns Query (not a list)

- No SQL is executed until the query is evaluated:
      user.posts.all()        → Executes query
      user.posts.filter(...)  → Builds query
      user.posts.limit(...)   → Builds query

- Supports chaining query methods:
      user.posts.order_by(...).limit(...).all()

---------------------------------------------------------------------

'dynamic' - DISADVANTAGES:
--------------------------
- Not a list → cannot iterate directly without calling .all()
- No automatic eager loading support (e.g., selectinload won't work)
- Slightly more complex API for beginners
- Can lead to multiple queries if used improperly - Potential performance overhead
- Can lead to unnecessary complexity

---------------------------------------------------------------------

'dynamic' - ADVANTAGES:
-----------------------
- Efficient for large collections (avoids loading everything into memory)
- Allows filtering at the database level
- Prevents unnecessary data transfer
- Provides full query flexibility per relationship
- Avoids N+1 issues when used intentionally

---------------------------------------------------------------------

When to Use:
------------
- Large one-to-many relationships (e.g., users → posts, logs, events)
- When you frequently need filtered subsets of related data
- When pagination or limiting results is required
- APIs where you want query-level control over related data

---------------------------------------------------------------------

How to Use Correctly:
---------------------

Access returns a QUERY OBJECT:

    posts_query = user.posts

Execute it explicitly:

    posts = user.posts.all()

Apply filters:

    recent_posts = user.posts.order_by(Post.id.desc()).limit(10).all()

---------------------------------------------------------------------

Key Takeaway:
-------------
lazy='dynamic' transforms a relationship into a query builder instead
of a preloaded collection, giving you precise control over how and when
data is fetched from the database.

It is ideal for large datasets and performance-sensitive applications.
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

db_url = 'sqlite:///ep_09_dynamic_database.db'

engine = create_engine(db_url, echo=True)  # important

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class User(Base):
    """
    Represents the 'users' table.
    
    ORM Attributes:
        posts (relationship): Configured with lazy='dynamic'. 
            Calling 'user.posts' returns a Query object, allowing for 
            statements like: user.posts.order_by(Post.id.desc()).limit(5).
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    posts = relationship('Post', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.name} >'


class Post(Base):
    """
    Represents the 'posts' table.
    
    The target of the dynamic query.
    """
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    content = Column(Text)

    user_id = Column(Integer, ForeignKey('users.id'))

    def __repr__(self):
        return f'<Post {self.id} >'


Base.metadata.create_all(engine)

# If there is data in the database, don't add more data
if session.query(User).count() < 1:
    session.add(
        User(name='Zeq', posts=[Post(content=f'Content {x}') for x in range(20)])
    )
    session.commit()


# ==== WHERE IT MAKES SENSE TO USE ====
user = session.query(User).filter_by(name='Zeq').first()

print(f"Showing all of the user's posts:\n {user.posts}")

recent_posts = user.posts.order_by(Post.id.desc()).limit(10).all()

for post in recent_posts:
    print(f"Post: {post.id} - {post.content}")




# ==== WHERE IT IS CONSIDERED UNNECESSARY ====
print(f"\n============================================================\n")
users = session.query(User).all()
for user in users:
    print(user.name)
    for post in user.posts.all():  # UNNECESSARY OVERHEAD for loading a few posts
        print(post.content)
