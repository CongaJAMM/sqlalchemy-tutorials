"""
SQLAlchemy Relationship Cascades: The 'all, delete-orphan' Strategy

This module introduces Relationship Cascades, which automate the lifecycle 
management of related objects. By defining a cascade, you ensure that 
changes to a Parent are reflected in its Children without manual intervention.

Key Concepts:
1. The 'all' Cascade:
   A shorthand for several individual cascades: save-update, merge, 
   refresh-expire, and delete. Most importantly, it means that if you 
   'session.add(Parent)', all its children are added automatically.

2. The 'delete-orphan' Cascade:
   This is the "strict" ownership rule. If a Child is removed from the 
   Parent's collection (e.g., 'parent.children.remove(child_a)'), 
   SQLAlchemy will mark 'child_a' for deletion in the database because 
   it no longer has a parent.

3. Unidirectional vs. Bidirectional:
   Cascades are defined on the 'relationship()' function of the Parent. 
   They control how actions flow from Parent -> Child.

Use Cases:
- Parent-Child relationships where the child cannot exist without the parent 
  (e.g., an Order and its OrderItems).
- Ensuring database cleanliness by preventing "orphan" rows that point 
  to non-existent parents.
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
    The 'Owner' in the relationship.
    
    Attributes:
        children (Mapped[list[Child]]): Managed by 'all, delete-orphan'.
            Any child added to this list is saved automatically. Any child 
            removed from this list is deleted from the database.
    """
    __tablename__ = 'parents'
    
    children: Mapped[list['Child']] = relationship(
        back_populates='parent',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Parent id: {self.id} children: {self.children}>'


class Child(Base):
    """
    The 'Dependent' in the relationship.
    
    Attributes:
        parent_id: Foreign key to the Parent.
        parent: The back-reference to the owner.
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
