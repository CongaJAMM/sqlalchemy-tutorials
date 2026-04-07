"""Example #3

SQLAlchemy Relationship Cascades: The 'save-update, merge' Configuration

This module demonstrates the standard, non-destructive approach to 
relationship management. This configuration focuses on data synchronization 
and session state rather than lifecycle destruction.

Key Concepts:
1. save-update (The Session Magnet):
   This is the default behavior for relationships. When a Parent is 
   added to a session via 'session.add()', all associated Children 
   automatically become part of that session. It removes the need to 
   manually add every object in a complex graph.

2. merge (The State Synchronizer):
   When 'session.merge()' is used on a Parent, this cascade ensures 
   that the state of the Children is also reconciled with the database. 
   This is critical when working with detached objects or multi-request 
   web workflows where objects are modified outside a session.

3. Persistence without Destruction:
   By omitting 'delete' and 'delete-orphan', this module ensures that 
   the Parent and Child are loosely coupled regarding their existence. 
   Deleting a Parent will only "orphan" the Children (setting parent_id 
   to NULL) rather than removing them from the database.

Use Cases:
- Many-to-Many associations where entities are shared.
- Soft-delete systems where records must persist even after association.
- Applications where you want explicit control over when data is deleted.
"""

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)
from sqlalchemy import create_engine, ForeignKey
from typing import List


class Base(DeclarativeBase):
    """Base class for ORM models."""
    pass


class Parent(Base):
    """
    The 'Owner' model in a non-destructive relationship.
    
    Attributes:
        id (Mapped[int]): Primary key identifier.
        children (Mapped[List[Child]]): Managed by 'save-update, merge'. 
            This allows a Parent and its children to be saved or merged 
            as a single unit, providing a "safe" workflow that prevents 
            accidental cascading deletions.
    """
    __tablename__ = 'parents'
    id: Mapped[int] = mapped_column(primary_key=True)
    children: Mapped[List['Child']] = relationship(
        back_populates='parent', cascade='save-update, merge'
    )

    def __repr__(self):
        return f'<Parent id: {self.id} children: {self.children}>'


class Child(Base):
    """
    The 'Dependent' model.
    
    Attributes:
        id (Mapped[int]): Primary key identifier.
        parent_id (Mapped[int]): Foreign key to the Parent. Set to 
            'nullable=True' to allow this child to exist as an "orphan" 
            if the Parent is deleted or if the child is removed from 
            the Parent's collection.
    """
    __tablename__ = 'children'
    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey('parents.id'), nullable=True)
    parent: Mapped['Parent'] = relationship(back_populates='children')

    def __repr__(self):
        return f'<Child id: {self.id} parent_id: {self.parent_id}>'


engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

# Create and commit parent and child
session = SessionLocal()
parent = Parent(children=[Child()])
session.add(parent)
session.commit()
print(f"Original committed parent: {parent}")
session.close()

# Since the session was closed, the parent is now detatched.
# Add a new child while detached; may throw an error in the process of adding the child
parent.children.append(Child())

# Merge back into a new session
session = SessionLocal()  # Create a new session
merged = session.merge(parent)  # Merges the updated object
print(f"Merged parent in session: {merged}")
session.commit()

# Query to confirm children were merged
fetched = session.query(Parent).first()
print(f"Fetched from DB: {fetched}")
session.close()
