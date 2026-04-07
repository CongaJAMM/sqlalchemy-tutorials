"""Example #2

SQLAlchemy Relationship Cascades: The 'save-update' Minimalist Strategy

This module demonstrates the most basic form of relationship cascading. In 
SQLAlchemy, 'save-update' is the default behavior, acting as a "magnet" 
that pulls associated objects into the same Session as their parent.

Key Concepts:
1. Automatic Discovery:
   When you call 'session.add(parent)', the ORM traverses the 'children' 
   relationship. Any Child objects found there are automatically added to 
   the session, even if you never called 'session.add(child)' explicitly.

2. Pending State:
   This cascade applies to 'transient' objects (new objects not yet in the DB) 
   and 'detached' objects (objects from a closed session being re-added).

3. Passive Deletion:
   Because 'delete' and 'delete-orphan' are absent, this setup is extremely 
   safe. Deleting a parent will not delete children; it will only attempt to 
   nullify the foreign key (if the database allows) or raise a ConstraintError 
   if the foreign key is 'NOT NULL'.

Use Cases:
- Large, complex object graphs where manual session management for every 
  leaf node would be tedious.
- Scenarios where you want the ORM to help with 'INSERT' and 'UPDATE' 
  coordination but want to handle 'DELETE' logic manually for safety.
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
    The 'Root' model of a relationship graph.
    
    Attributes:
        children (Mapped[list[Child]]): Configured with 'save-update'. 
            This is the standard 'Discovery' hook. It ensures that any 
            Child assigned to this parent is automatically persisted 
            when the Parent is saved.
    """
    __tablename__ = 'parents'
    children: Mapped[list['Child']] = relationship(
        back_populates='parent', cascade='save-update'
    )

    def __repr__(self):
        return f'<Parent id: {self.id} children: {self.children}>'


class Child(Base):
    """
    The 'Leaf' model.
    
    In this minimalist configuration, the Child relies on the Parent 
    to be 'discovered' by the Session, but its physical existence in 
    the database is not strictly tied to the Parent's lifecycle.
    """
    __tablename__ = 'children'
    parent_id: Mapped[int] = mapped_column(ForeignKey('parents.id'))
    parent: Mapped['Parent'] = relationship(back_populates='children')

    def __repr__(self):
        return f'<Child - parent_id: {self.parent_id}>'


engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)


session = SessionLocal()

parent = Parent()
child = Child()
parent.children.append(child)

# Only add the parent to session
session.add(parent)

# Child is automatically added
assert child in session

print('Before committing')
print(parent)
print(child)
session.commit()

print('\nAfter committing')
print(parent)
print(child)
