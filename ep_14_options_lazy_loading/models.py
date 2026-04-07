# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=2fwdjkL0jqw

"""
Database Models and Schema Configuration

This module defines the SQLAlchemy ORM models for a User-centric system 
featuring Posts, Preferences, and Post Details. 

Key Architecture Features:
1. Declarative Mapping: Uses 'Mapped' and 'mapped_column' for type-safe 
   definitions (SQLAlchemy 2.0 style).
2. Relationship Loading:
   - User.posts: Uses 'select' (lazy) loading. Posts are only fetched from 
     the DB when 'user.posts' is accessed in Python.
   - User.preference: Uses 'joined' (eager) loading. Preferences are 
     fetched in the same SQL query as the User via a LEFT OUTER JOIN.
3. Foreign Key Constraints: Establishes one-to-one and one-to-many 
   relationships to ensure data integrity.
"""

from sqlalchemy import Column, ForeignKey, Integer, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)
from datetime import datetime

db_url = 'sqlite:///ep_14_options_lazy_load.db'

engine = create_engine(db_url, echo=True)

Session = sessionmaker(bind=engine)
session = Session()


class Base(DeclarativeBase):
    """
    Common Base for all models.
    
    Provides a shared primary key 'id' to all inheriting classes to 
    reduce boilerplate code across the schema.
    """
    id = Column(Integer, primary_key=True)


class User(Base):
    """
    The central entity representing a registered user.
    
    Attributes:
        name (Mapped[str]): The user's displayed name.
        status (Mapped[str | None]): Optional status message.
        posts (Mapped[list[Post]]): One-to-Many relationship. Loaded lazily 
            (N+1 risk) unless joined in the query.
        preference (Mapped[Preference]): One-to-One relationship. Loaded 
            eagerly via JOIN whenever a User is queried.
    """
    __tablename__ = 'users'
    name: Mapped[str]
    status: Mapped[str | None]
    posts: Mapped[list['Post']] = relationship(
        backref='user',
        lazy='select',
    )
    preference: Mapped['Preference'] = relationship(
        backref='user',
        lazy='joined',
    )

    def __repr__(self):
        return f'<User {self.name} >'

class Preference(Base):
    """
    User-specific application settings.
    
    Connected to the User via 'user_id' foreign key. Handles UI and 
    behavioral defaults like dark mode and playback speed.
    """
    __tablename__ = 'preferences'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    dark_mode: Mapped[bool] = mapped_column(default=False)
    speed: Mapped[float] = mapped_column(default=1.0)

    def __repr__(self):
        return f'<Preferences {self.id} >'

class Post(Base):
    """
    Content created by a User.
    
    Attributes:
        active (Mapped[bool]): Visibility toggle for the post.
        date (Mapped[datetime]): Publication timestamp.
        user_id (Mapped[int]): Reference to the owner (User).
        detail (Mapped[Detail]): One-to-One link to the post's text content.
    """
    __tablename__ = 'posts'
    active: Mapped[bool] = mapped_column(default=True)
    date: Mapped[datetime] = mapped_column(default=None, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    detail: Mapped['Detail'] = relationship(backref='post', lazy='select')

    def __repr__(self):
        return f'<Post {self.id} >'


class Detail(Base):
    """
    The heavy-text storage for a specific Post.
    
    Separated from the Post table to allow for 'thin' queries of post 
    metadata without loading large string contents into memory 
    unless explicitly requested.
    """
    __tablename__ = 'details'
    content: Mapped[str]
    post_id: Mapped[int] = mapped_column(ForeignKey('posts.id'))

    def __repr__(self):
        return f'<Detail {self.id} - content: {self.content}>'


# Create the database tables
Base.metadata.create_all(engine)

if __name__ == '__main__':

    if session.query(User).count() < 1:
        user_1 = User(name='Zeq', preference=Preference(dark_mode=True, speed=2.5))
        user_1.posts = [
            Post(detail=Detail(content='This is an example post detail')),
            Post(detail=Detail(content='Subscribe to Zeq Tech!'), active=True),
        ]

        user_2 = User(name='Bill', preference=Preference())
        user_2.posts = [
            Post(detail=Detail(content='This is another example of some post details')),
            Post(detail=Detail(content='Yes!')),
        ]

        session.add_all([user_1, user_2])
        session.commit()
