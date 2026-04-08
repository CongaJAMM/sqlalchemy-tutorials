"""Example #7

SQLAlchemy Relationship Cascades: The 'expunge' Strategy

This module demonstrates how to manage object detachment across a relationship. 
Expunging is the act of 'evicting' an object from the Session's identity map, 
meaning the Session will no longer track changes to that object or its children.

Key Concepts:
1. Session Detachment:
   When 'session.expunge(parent)' is called, the parent is no longer 
   associated with that database transaction. It becomes a 'detached' 
   POJO (Plain Old JSON Object).

2. The Expunge Cascade:
   Without this cascade, expunging a parent would leave the children 
   'persistent' in the session. With 'cascade=expunge', the entire 
   object graph is detached simultaneously.

3. DetachedInstanceError:
   A common side effect of expunging. If you try to access a lazy-loaded 
   attribute (like 'parent.children') on a detached object, SQLAlchemy 
   will raise a 'DetachedInstanceError' because it no longer has a 
   database connection to fetch that data.

Use Cases:
- Sending objects to a background task or a different thread where the 
  original session is closed.
- Caching objects in memory (e.g., Redis) where you want to ensure the 
  Session isn't holding onto a reference that could cause memory leaks.
"""

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)
from sqlalchemy import create_engine, ForeignKey


class Base(DeclarativeBase):
    """Base class for ORM models."""
    id: Mapped[int] = mapped_column(primary_key=True)


class Parent(Base):
    """
    A model that manages the session lifecycle of its children.
    
    Attributes:
        children (Mapped[list[Child]]): Configured with 'expunge'. 
            If this parent instance is removed from the Session 
            using 'session.expunge()', every associated child 
            will also be detached from the Session.
    """
    __tablename__ = 'parents'

    children: Mapped[list['Child']] = relationship(
        back_populates='parent',
        cascade='save-update, expunge'
    )

    def __repr__(self):
        return f'<Parent id: {self.id} children: {self.children}>'


class Child(Base):
    """
    A dependent model that mirrors the session state of its parent.
    
    The 'expunge' cascade on the 'parent' relationship ensures that 
    the detachment works bidirectionally; expunging a child can 
    optionally detach the parent if configured.
    """
    __tablename__ = 'children'
    parent_id: Mapped[int] = mapped_column(ForeignKey('parents.id'), nullable=True)
    parent: Mapped['Parent'] = relationship(
        back_populates='children', cascade='expunge'
    )

    def __repr__(self):
        return f'<Child - parent_id: {self.parent_id}>'


engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

session = SessionLocal()

parent = Parent(children=[Child()])
session.add(parent)
session.commit()

session.expunge(parent)

assert parent not in session
# try:
print(parent.children[0])
# except DetachedInstanceError:
#     print('parent.children are not in the session')
