# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# https://www.youtube.com/watch?v=WsDVBEmTlaI


"""Example #1

SQLAlchemy Programmatic Index Management

This module demonstrates how to manage database indexes outside of the 
initial table creation. This approach provides fine-grained control over 
the database schema lifecycle.

Key Concepts:
1. Declarative vs. Imperative:
   - Declarative: 'unique=True' or 'index=True' inside mapped_column. 
     These are handled automatically by 'Base.metadata.create_all()'.
   - Imperative: Creating an 'Index()' object manually. This allows you 
     to CREATE or DROP indexes at any point during your application's 
     execution.

2. Explicit Index Lifecycle:
   - .create(): Sends a 'CREATE INDEX' command to the database immediately.
   - .drop(): Sends a 'DROP INDEX' command.
   - checkfirst=True: A safety flag that prevents errors if you try to 
     drop an index that doesn't exist (or create one that already does).

3. Use Cases:
   - Temporary Indexes: Speeding up a specific bulk update or report 
     and then removing the index to restore write performance.
   - Maintenance Scripts: Managing indexes dynamically without altering 
     the core model definitions.
"""

# When you run this code, you can see the line in the output:

# sqlalchemy.engine.Engine CREATE INDEX ix_users_name ON users (name)
# ...
# DROP INDEX ix_users_name


from sqlalchemy import create_engine, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

engine = create_engine('sqlite:///:memory:', echo=True)  # Create the database in-memory


class Base(DeclarativeBase):
    """
    Standard Declarative Base for 2.0 Style Mapping.
    """
    id: Mapped[int] = mapped_column(primary_key=True)


class User(Base):
    """
    Represents the 'users' table.
    
    Attributes:
        name (Mapped[str]): A standard column. In this script, an index 
            is added to this column programmatically after table creation.
        email (Mapped[str]): A column with a declarative 'unique=True' 
            constraint. This automatically creates a unique index in the 
            database during 'create_all()'.
    """
    __tablename__ = 'users'

    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)


Base.metadata.create_all(engine)

# Add an index programmatically here
user_name_index = Index('ix_users_name', User.name)
user_name_index.create(bind=engine)      # Create the index, if it does not exists
user_name_index.drop(bind=engine, checkfirst=True)      # Drop the index, if it still exists

for name, table in Base.metadata.tables.items():
    print(f"\nTable: {name}")
    indexes = list(table.indexes)
    if len(indexes) < 1:
        print("- No Indexes")
    for index in indexes:
        print(f"- Index Name: {index.name}")
        print(f"- Columns: {', '.join([column.name for column in index.columns])}")
