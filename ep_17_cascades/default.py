"""Example #1

Cascading controls how changes affect relating objects.

SQLAlchemy Relationship Cascades: The 'save-update, merge' Strategy

This module demonstrates the baseline behavior for managing related objects. 
This strategy is "Additive" rather than "Destructive," making it ideal for 
relationships where children might exist independently or should not be 
automatically deleted.

Key Concepts:
1. save-update:
   The most common cascade (and part of the default). If a Parent is added 
   to a session via 'session.add(parent)', all objects in the 'children' 
   collection are also added to that session automatically.

2. merge:
   When using 'session.merge(parent)', this cascade ensures that the state 
   of the children is also merged. This is vital when working with 
   detached objects (e.g., objects passed between different web requests).

3. The Absence of 'delete':
   Because 'delete' and 'delete-orphan' are omitted, deleting a Parent 
   will NOT delete its children. Instead, the children will become 
   "orphans" in the database (their parent_id will simply be set to NULL).

Use Cases:
- Many-to-Many "Tagging" systems where deleting a Post shouldn't delete the Tags.
- Situations where you want full manual control over the deletion of related data.
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
    The 'Owner' with a non-destructive relationship.
    
    Attributes:
        children (Mapped[list[Child]]): Configured for 'save-update, merge'. 
            This allows for easy bulk-saving of a parent and its children, 
            but provides a safety net against accidental mass-deletion.
    """
    __tablename__ = 'parents'

    children: Mapped[list['Child']] = relationship(
        back_populates='parent', cascade="save-update, merge"  # Reveals the default cascade option
    )

    def __repr__(self):
        return f'<Parent id: {self.id} children: {self.children}>'


class Child(Base):
    """
    The 'Dependent' record.
    
    In this configuration, children are resilient. If their parent is 
    removed, the child record persists, though it loses its association.
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

