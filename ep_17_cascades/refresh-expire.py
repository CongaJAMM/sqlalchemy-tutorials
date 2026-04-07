"""Example #6

SQLAlchemy Relationship Cascades: The 'refresh-expire' Configuration

This module demonstrates how to synchronize the lifecycle states of related 
objects. This strategy ensures that when a Parent's data is reloaded or 
invalidated, its associated Children undergo the same process.

Key Concepts:
1. expire (The Invalidation):
   When 'session.expire(parent)' is called, the Parent's attributes are 
   erased from memory. The next time you access an attribute, SQLAlchemy 
   issues a new SELECT. With this cascade, the Children are also expired 
   automatically.

2. refresh (The Reload):
   When 'session.refresh(parent)' is called, SQLAlchemy immediately 
   re-queries the database for the Parent's current data. This cascade 
   ensures that the Children's data is also refreshed or expired to 
   maintain data integrity across the relationship.

3. Consistency:
   This prevents "Stale Data" issues where a Parent might have fresh 
   database values but its Children are still holding onto old values 
   from a previous query.

Use Cases:
- Applications where database triggers or external processes might 
  modify related records simultaneously.
- Complex transactions where you need to ensure the entire object graph 
  reflects the most recent database COMMIT.
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
    The 'Primary' model in a synchronized relationship.
    
    Attributes:
        children (Mapped[list[Child]]): Configured with 'refresh-expire'. 
            This allows for coordinated state management. If the Parent 
            is marked as 'expired' (e.g., after a commit or manual call), 
            the Children are also marked as expired, forcing a fresh 
            database hit upon the next access.
    """
    __tablename__ = 'parents'
    children: Mapped[list['Child']] = relationship(
        back_populates='parent',
        cascade='save-update, refresh-expire'  # Keep the child informed
    )

    def __repr__(self):
        return f'<Parent id: {self.id} children: {self.children}>'


class Child(Base):
    """
    The 'Dependent' model whose state mirrors the Parent.
    
    In this configuration, the Child does not dictate the lifecycle 
    of the Parent, but it relies on the Parent to trigger its own 
    state refreshes through the relationship cascade.
    """
    __tablename__ = 'children'
    parent_id: Mapped[int] = mapped_column(ForeignKey('parents.id'), nullable=True)
    
    parent: Mapped['Parent'] = relationship(back_populates='children')

    def __repr__(self):
        return f'<Child - parent_id: {self.parent_id}>'


engine = create_engine('sqlite:///:memory:', echo=True)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

session = SessionLocal()

parent = Parent(children=[Child()])
session.add(parent)
session.commit()

print("\nBefore Expire:")
print(parent.children) 
print(parent.children) 
session.expire(parent)
# session.expire_all([parent])

# Re-fetches from DB if accessed
print("\nAfter Expire:")
print(parent.children) 
