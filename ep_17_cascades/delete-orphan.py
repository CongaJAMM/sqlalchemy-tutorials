"""Example #5

SQLAlchemy Relationship Cascades: The 'delete-orphan' in Action

This module demonstrates the physical cleanup of orphaned records. In 
SQLAlchemy, 'orphaning' occurs when a child object is removed from its 
parent's collection or has its parent attribute set to None.

Key Concepts:
1. Severing the Link:
   When 'parent.children.clear()' or 'parent.children.remove(child)' is 
   called, the ORM detects that the child no longer has an owner.

2. The Delete-Orphan Rule:
   Despite the database column 'parent_id' being nullable (allowing 
   orphans at the SQL level), the 'delete-orphan' cascade tells the ORM 
   to emit a DELETE statement instead of an UPDATE (to NULL).

3. Persistence vs. Memory:
   This module shows the state of the database before and after the 
   clearing of the collection, proving that the child records are 
   permanently removed from the 'children' table.

Use Cases:
- Line items on an invoice (if removed from the invoice, they should cease to exist).
- Profile settings that belong strictly to one specific user.
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
    The Controller of the relationship.
    
    The 'delete-orphan' flag ensures that the 'children' collection is 
    the exclusive owner of its items. Removing an item from the list 
    triggers a database DELETE.
    """
    __tablename__ = 'parents'
    children: Mapped[list['Child']] = relationship(
        back_populates='parent',
        cascade='all, delete-orphan'  # Indicates child will follow along with the cascade case and proceed with the deletion
    )

    def __repr__(self):
        return f'<Parent id: {self.id} children: {self.children}>'


class Child(Base):
    """
    A dependent entity.
    
    Note: 'nullable=True' on parent_id allows the DB to store a NULL, 
    but the ORM's 'delete-orphan' cascade prevents this state from 
    ever occurring through standard ORM operations.
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

parent = Parent(children=[Child()])  # Setup a parent with a child 
session.add(parent) # Add the parent and child to the database
session.commit()    # Save changes to the database

print("\nThe created child:")
print(session.query(Child).all())   # Should show the created child

parent.children.clear()     # Deletes the parent's link to the child
session.commit()


print("\nIs child still here?")
print(session.query(Child).all())   # Should reflect that the created child is gone
