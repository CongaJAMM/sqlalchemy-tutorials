# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=KNxVG4OcboY

"""Example #4

SQLAlchemy Relationship Loading Strategy: lazy='subquery'

Overview:
---------
The 'subquery' loading strategy eagerly loads related objects by issuing
a second SQL query that uses a subquery of the parent results.

Instead of loading related objects per parent (like lazy='select'),
or using a JOIN (like joinedload), it builds a subquery of parent IDs
and fetches all related rows in one additional query.

This results in efficient bulk loading while avoiding row duplication.

---------------------------------------------------------------------

'subquery' Default Behavior:
----------------------------
- Executes the primary query (e.g., Users)
- Then runs a SECOND query using a subquery of those results
- Loads all related objects (e.g., Posts) in one go
- Automatically associates them with their parent objects

Example:
    users = session.query(User).all()

    Accessing:
        user.posts

    Does NOT trigger additional queries per user.

---------------------------------------------------------------------

Generated SQL Pattern:
----------------------
1) Load parent rows:

    SELECT * FROM users;

2) Load related rows using a subquery:

    SELECT posts.*
    FROM posts
    JOIN (
        SELECT users.id FROM users
    ) AS anon_1
    ON posts.user_id = anon_1.id;

---------------------------------------------------------------------

'subquery' - DISADVANTAGES:
---------------------------
- More complex SQL (uses subqueries)
- Can be slower than `selectinload` for large datasets
- Harder for the database optimizer to handle in some cases
- Considered somewhat legacy compared to `selectinload`

---------------------------------------------------------------------

'subquery' - ADVANTAGES:
------------------------
- Avoids N+1 query problem
- Loads all related data in bulk
- Prevents row duplication (unlike joinedload)
- Works well for MODERATE dataset sizes

---------------------------------------------------------------------

When to Use:
------------
- When you want eager loading without JOIN duplication
- When working with moderate-sized datasets
- When `selectinload` is not available or not preferred

---------------------------------------------------------------------

Modern Recommendation:
----------------------
In most modern SQLAlchemy applications, prefer:

    selectinload()

It produces simpler SQL using:

    WHERE ... IN (...)

and is generally more efficient and flexible.

---------------------------------------------------------------------

Key Takeaway:
-------------
lazy='subquery' eagerly loads relationships using a subquery-based
second query, avoiding N+1 issues but typically being less efficient
than selectinload in modern applications.
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

db_url = 'sqlite:///ep_09_subquery_database.db'

engine = create_engine(db_url, echo=True)  # important

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class User(Base):
    """
    Represents the 'users' table.
    
    ORM Attributes:
        posts (relationship): Configured with lazy='subquery'. 
            SQLAlchemy will emit a second query that uses the original 
            User query as a subquery to fetch all related posts at once.
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    # Eagerly loads all posts using a subquery-based batch
    posts = relationship('Post', backref='user', lazy='subquery')

    def __repr__(self):
        return f'<User {self.name} >'


class Post(Base):
    """
    Represents the 'posts' table.
    
    The 'Many' side of the relationship. When User is queried, these 
    are fetched by joining the 'posts' table against the 'User' subquery.
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
    session.add_all(
        [
            User(
                name=f'User {y}',
                posts=[
                    Post(content=f'This is the content for {y * 5 + x}')
                    for x in range(5)
                ],
            )
            for y in range(100)
        ]
    )
    session.commit()

users = session.query(User).all()
for user in users:
    print(user.name)
    for (
        post
    ) in user.posts:  # Efficiently loads posts for all queried users using a subquery
        print(post.content)
