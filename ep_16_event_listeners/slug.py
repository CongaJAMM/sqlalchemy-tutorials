# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=_cHSW_ehjtY

"""Example #3

SQLAlchemy Event Listeners: Automated Data Transformation (Slug Generation)

This module demonstrates how to use Mapper-level events to automatically 
transform data before it is persisted to the database. This is a common 
pattern for maintaining SEO slugs, hashing passwords, or normalizing strings.

Key Concepts:
1. Reusable Logic:
   The 'generate_slug' function is defined once and attached to both 
   insertion and update events. This ensures that the 'slug' column is 
   always in sync with the 'title' column.

2. Data Normalization:
   By using Regular Expressions (re) inside the listener, we can transform 
   human-readable titles (e.g., 'Hello World!') into URL-safe strings 
   (e.g., 'hello-world').

3. Hybrid Registration:
   This module showcases that you can mix registration styles:
   - @event.listens_for: Used for the initial 'before_insert' logic.
   - event.listen(): Used to attach the same logic to 'before_update' 
     after the function has been defined.

4. Efficiency:
   The transformation happens in-memory just before the SQL is emitted. 
   This prevents the need for a secondary UPDATE statement after a record 
   is created.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, mapped_column, Mapped, DeclarativeBase, Mapper
from sqlalchemy.engine import Connection
import re

engine = create_engine('sqlite:///:memory:')


class Base(DeclarativeBase):
    """Base class for ORM models."""
    id: Mapped[int] = mapped_column(primary_key=True)


class BlogPost(Base):
    """
    Represents the 'blog_posts' table.
    
    Attributes:
        title (Mapped[str]): The human-readable title of the post.
        slug (Mapped[str]): A URL-friendly version of the title, 
            maintained automatically by event listeners.
    """
    __tablename__ = 'blog_posts'
    title: Mapped[str]
    slug: Mapped[str] = mapped_column(unique=True)


# Add an event through a decorator
@event.listens_for(BlogPost, 'before_insert')
def generate_slug(mapper: Mapper, connection: Connection, target: BlogPost):
    """
    Listener that converts a title into a URL-friendly slug.
    Example: "SQLAlchemy is Great!" -> "sqlalchemy-is-great"
    """
    if target.title:
        slug = re.sub(r'[^\w]+', '-', target.title.lower())
        target.slug = slug


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Add an event through a function call
event.listen(BlogPost, 'before_update', generate_slug)

post = BlogPost(title='Decorators are super cool')
session.add(post)
session.commit()

print(post.slug)

post.title = 'Subscribe to Zeq Tech'
session.commit()
print(post.slug)
