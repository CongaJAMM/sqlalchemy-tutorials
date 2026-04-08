# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# https://www.youtube.com/watch?v=WsDVBEmTlaI

""" Example #2

SQLAlchemy Inline Column Indexing

This module demonstrates the most common and concise method for defining 
indexes: using the 'index=True' and 'unique=True' parameters directly 
within the 'mapped_column' definition.

When to ADD an index:
    - Frequent Searches
    - Joins on Columns
    - Filtering and Sorting
    - Uniqueness Constraints
    - Range Queries

When to AVOID indexing:
    - Small Tables
    - Columns with few unique values
    - Heavy Write Operations
    - Frequent Batch Operations

Key Concepts:
1. Declarative Shorthand:
   By adding 'index=True' to a column, SQLAlchemy automatically generates 
   a CREATE INDEX statement during table creation. 

2. Uniqueness vs. Indexing:
   - 'unique=True': Ensures no two rows have the same value (e.g., Email). 
     Most databases create an index automatically to enforce this.
   - 'index=True': Explicitly requests a search optimization structure. 
   - Using both: Redundant in some SQL dialects but ensures that the 
     index is created and named clearly in others.

3. Automatic Naming:
   When using the inline method, SQLAlchemy generates the index name 
   automatically based on the table and column (e.g., 'ix_users_email').
"""

# When you run this code, you can see the line in the output:

# sqlalchemy.engine.Engine CREATE UNIQUE INDEX ix_users_email ON users (email)


from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

engine = create_engine('sqlite:///:memory:', echo=True)


class Base(DeclarativeBase):
    """
    Base class for all models.
    """
    id: Mapped[int] = mapped_column(primary_key=True)


class User(Base):
    """
    Represents the 'users' table using inline indexing.

    ORM Attributes:
        name (Mapped[str]): A standard column without an index. Searches 
            by name will result in a full table scan.
            
        email (Mapped[str]): Configured with both 'unique' and 'index' 
            constraints. This ensures data integrity (no duplicate emails) 
            and high-speed retrieval (indexed lookups).
    """
    __tablename__ = 'users'

    name: Mapped[str]

    # Inline indexing and uniqueness
    email: Mapped[str] = mapped_column(unique=True, index=True)  # Add the index here


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.reflect(bind=engine)

# ============================================================

for name, table in Base.metadata.tables.items():
    print(f"\nTable: {name}")
    indexes = list(table.indexes)
    if len(indexes) < 1:
        print("- No Indexes")
    for index in indexes:
        print(f"- Index Name: {index.name}")
        print(f"- Columns: {', '.join([column.name for column in index.columns])}")