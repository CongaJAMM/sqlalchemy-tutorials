# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=iwENqqgxm-g

"""Example #3

SQLAlchemy 2.0 Semantic Mapping: Annotated Types & Custom Registry

This module demonstrates the most sophisticated way to map Python types to 
database columns using 'typing.Annotated'. This pattern separates the 
"What" (the data type) from the "How" (the database constraints).

Key Concepts:
1. typing.Annotated:
   Allows you to attach metadata to a type. 'Annotated[str, 20]' tells 
   Python it's a string, but leaves a "note" (the number 20) that 
   SQLAlchemy can read to determine column length.

2. Custom Registry:
   By explicitly defining the 'registry' inside the Base class, you 
   gain granular control over how types are mapped. The 'type_annotation_map' 
   here links your specific Annotated aliases to actual SQLAlchemy 
   String objects.

3. Clean & DRY (Don't Repeat Yourself):
   You no longer need to write 'mapped_column(String(20))' across multiple 
   models. If the length of a "short name" changes from 20 to 30, you 
   update it in exactly one place.
"""

from typing import Optional

from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, registry
from typing_extensions import Annotated

engine = create_engine('sqlite:///ep_10_custom_registry.db', echo=True)


# Define Semantic Type Aliases
# These act as "blueprints" for your database columns.
str_20 = Annotated[str, 20]
str_100 = Annotated[str, 100]


class Base(DeclarativeBase):
    """
    The Declarative Base with a Custom Mapping Registry.
    
    Attributes:
        registry (Registry): An explicit registry object that maps our 
            Annotated Python types to concrete SQLAlchemy String objects.
            This is the "translation layer" between Python and SQL.
    """
    registry = registry(
        type_annotation_map={
            str_20: String(20),
            str_100: String(100),
        }
    )


class User(Base):
    """
    Represents the 'users' table using semantic type hints.
    
    Class Attributes:
        id (Mapped[int]): Standard primary key.
        
        first_name (Mapped[Optional[str_20]]): Resolves to a NULLABLE 
            VARCHAR(20) via the registry map.
            
        last_name (Mapped[Optional[str_100]]): Resolves to a NULLABLE 
            VARCHAR(100) via the registry map.
    """
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)

    # The Mapped[] hint does all the heavy lifting!
    first_name: Mapped[Optional[str_20]]
    last_name: Mapped[Optional[str_100]]


# Create the database tables
Base.metadata.create_all(engine)
