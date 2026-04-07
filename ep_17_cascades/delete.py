"""Example #4

SQLAlchemy Relationship Cascades: The 'delete' Strategy

This module demonstrates the automated cleanup of child records when a 
parent is removed. The 'delete' cascade is a "top-down" destruction 
mechanism that ensures referential integrity at the ORM level.

Key Concepts:
1. Top-Down Deletion:
   When 'session.delete(parent)' is called, SQLAlchemy identifies all 
   objects in the 'children' collection and marks them for deletion 
   as well.

2. Difference from 'delete-orphan':
   - 'delete' triggers when the PARENT is deleted.
   - 'delete-orphan' triggers when a CHILD is removed from the list. Deletes the Parent with the Child

   In this module, if you deleted the parent, the children vanish. 
   However, if you just cleared the list (parent.children = []), the 
   children would stay in the database with NULL parent_ids because 
   'delete-orphan' is NOT specified.

3. Database vs. ORM Deletes:
   This 'delete' cascade happens in Python/SQLAlchemy. The ORM fetches 
   the children and issues individual DELETE statements for them. 
   (This is different from a 'FOREIGN KEY ON DELETE CASCADE' in raw SQL).

Use Cases:
- User accounts and their private profiles.
- Any "Strong Entity" and its "Weak Entity" dependents where the 
  dependent cannot logically exist without the owner.
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
    A model that "owns" its children's existence.
    
    Attributes:
        children (Mapped[list[Child]]): Configured with 'delete'. 
            Deleting an instance of this class will result in a 
            cascading delete of all associated Child records.
    """
    __tablename__ = 'parents'
    children: Mapped[list['Child']] = relationship(
        back_populates='parent', cascade='save-update, delete'
    )

    def __repr__(self):
        return f'<Parent id: {self.id} children: {self.children}>'


class Child(Base):
    """
    A dependent model.
    
    In this module, the Child is removed from the database if the 
    Parent is deleted, but it can survive "orphaning" (disassociation) 
    because 'delete-orphan' is missing.
    """
    __tablename__ = 'children'
    parent_id: Mapped[int] = mapped_column(ForeignKey('parents.id'), nullable=True)
    parent: Mapped['Parent'] = relationship(back_populates='children')

    def __repr__(self):
        return f'<Child - parent_id: {self.parent_id}>'


engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

session = SessionLocal()

parent = Parent(children=[Child()])
session.add(parent)
session.commit()

print(session.query(Child).all())  # Not Empty

session.delete(parent)
session.commit()

print(session.query(Child).all())  # Empty; no more data
