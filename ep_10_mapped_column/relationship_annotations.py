# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=iwENqqgxm-g

"""Example #4

SQLAlchemy 2.0 Relationship Mapping (Annotation-Driven)

This module demonstrates how modern SQLAlchemy uses Python Type Annotations 
(Mapped[T]) to automatically configure Relationship cardinality (1:1 vs 1:N).

Key Concepts:
1. Type-Inferred Cardinality:
   - Mapped[list['Post']] -> SQLAlchemy detects 'list' and configures a 
     One-to-Many (1:N) relationship.
   - Mapped['Content'] -> SQLAlchemy detects a single class and configures 
     a One-to-One (1:1) or Many-to-One (N:1) relationship.

2. String Forward References:
   By using quotes around class names (e.g., 'Post'), we avoid 'NameError' 
   issues when classes are defined later in the file or reference each other 
   circularly.

3. Simplified relationship() calls:
   In many cases, the relationship() function no longer needs explicit 
   arguments like 'uselist' because the Mapped annotation provides 
   that metadata.
"""

from typing import Optional

from sqlalchemy import ForeignKey, create_engine, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)

engine = create_engine('sqlite:///ep_10_relationships.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()


class Base(DeclarativeBase):
    """Abstract base for 2.0 Style Declarative Models."""
    pass


class User(Base):
    """
    Represents the 'users' table.
    
    ORM Attributes:
        posts (Mapped[list['Post']]): A One-to-Many relationship. 
            Because the annotation is a 'list', SQLAlchemy knows this 
            user can have multiple associated post objects.
    """
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]]

    # One to Many relationship with Annotation
    posts: Mapped[list['Post']] = relationship()


class Post(Base):
    """
    Represents the 'posts' table.
    
    ORM Attributes:
        user_id: Foreign key linking back to the User.
        content (Mapped['Content']): A One-to-One relationship. 
            Because there is no 'list' wrapper, SQLAlchemy treats this 
            as a single scalar object.
    """
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    # One to One relationship with Annotation
    # The lack of list[] hint tells SQLAlchemy this is a single object (1:1)
    content: Mapped['Content'] = relationship()


class Content(Base):
    """
    Represents the 'contents' table.
    
    This acts as the child in a 1:1 relationship with the Post table.
    """
    __tablename__ = 'contents'

    id: Mapped[int] = mapped_column(primary_key=True)

    # Typically declared in the "Child" table
    post_id: Mapped[int] = mapped_column(ForeignKey('posts.id'))
    data: Mapped[str]


# Create the database tables
Base.metadata.create_all(engine)

# If there is data in the database, don't add more data
if session.query(User).count() < 1:
    user = User(
        name='Zeq Tech', posts=[Post(content=Content(data='This is some content'))]
    )
    session.add(user)
    session.commit()

user = session.scalar(select(User))
print(f'\nUser {user.id}: {user.name} - {user.posts[0].content.data} \n')

user = session.query(User).first()
print(f'\nUser {user.id}: {user.name} - {user.posts[0].content.data} \n')
