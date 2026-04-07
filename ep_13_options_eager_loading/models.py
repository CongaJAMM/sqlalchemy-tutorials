# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================

"""
SQLAlchemy Model Definitions: Eager Loading Strategy Demonstration

This module defines a multi-tiered relational schema used to demonstrate 
the transition from 'Lazy Loading' to 'Eager Loading' using Query Options.

Core Concepts:
1. Default Lazy Loading (lazy='select'):
   Relationships are configured to load only when accessed in Python. This 
   is the safest default but can lead to the N+1 problem in loops.

2. Relationship Hierarchy:
   - User (Parent): Contains a collection of Posts.
   - Post (Child/Parent): Links to a User and contains a single Detail record.
   - Detail (Child): The leaf node containing specific post metadata.

3. Query-Time Overrides:
   Although 'lazy=select' is set in the models, these can be overridden at 
   runtime using:
   - joinedload(): For Many-to-One or One-to-One (SQL JOIN).
   - selectinload(): For One-to-Many collections (separate IN-based query).


"""

from sqlalchemy import Column, ForeignKey, Integer, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)

db_url = 'sqlite:///ep_13_options_eager_loading.db'

engine = create_engine(db_url)

Session = sessionmaker(bind=engine)
session = Session()


class Base(DeclarativeBase):
    """
    Abstract Base Class for all models.
    
    Attributes:
        id (Integer): Primary key defined at the base level to ensure consistency 
            across 'users', 'posts', and 'details'.
    """
    id = Column(Integer, primary_key=True)


class User(Base):
    """
    Represents the 'users' table.
    
    ORM Attributes:
        posts (Mapped[list['Post']]): A One-to-Many relationship. 
            By default, posts are NOT fetched when a User is queried. Accessing 
            'user.posts' will trigger a secondary SELECT statement.
    """
    __tablename__ = 'users'
    name: Mapped[str]

    # Defaults to Lazy Loading
    posts: Mapped[list['Post']] = relationship(
        backref='user',
        lazy='select',
    )

    def __repr__(self):
        return f'<User {self.name} >'


class Post(Base):
    """
    Represents the 'posts' table.
    
    Attributes:
        active (Mapped[bool]): Boolean flag for filtering active content.
        user_id (Mapped[int]): Foreign Key linking to the parent User.
        detail (Mapped['Detail']): A One-to-One relationship to specific metadata. 
            Like the parent relationship, this is lazy-loaded by default.
    """
    __tablename__ = 'posts'
    active: Mapped[bool] = mapped_column(default=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    
    detail: Mapped['Detail'] = relationship(backref='post', lazy='select')

    @classmethod
    def is_active(cls):
        """Helper method to check for active post status."""
        return cls.active is True

    def __repr__(self):
        return f'<Post {self.id} >'


class Detail(Base):
    """
    Represents the 'details' table.
    
    The most granular level of the hierarchy, holding the actual 
    text content for a Post.
    """
    __tablename__ = 'details'
    content: Mapped[str]
    post_id: Mapped[int] = mapped_column(ForeignKey('posts.id'))

    def __repr__(self):
        return f'<Detail {self.id} - content: {self.content}>'


# Create the database tables
Base.metadata.create_all(engine)

if __name__ == '__main__':

    # Add data to the Dataset

    user_1 = User(name='Zeq')
    user_1.posts = [
        Post(detail=Detail(content='This is an example post detail')),
        Post(detail=Detail(content='Subscribe to Zeq Tech!'), active=True),
    ]

    user_2 = User(name='Bill')
    user_2.posts = [
        Post(detail=Detail(content='This is another example of some post details')),
        Post(detail=Detail(content='Yes!')),
    ]

    session.add_all([user_1, user_2])
    session.commit()
