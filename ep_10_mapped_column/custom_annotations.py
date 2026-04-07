# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=iwENqqgxm-g

"""Example #2

SQLAlchemy 2.0 Advanced Mapping: Custom Annotations & Global Type Maps

This module demonstrates how to centralize database column configurations 
using the 'type_annotation_map'. This pattern enforces consistency across 
all models and significantly reduces boilerplate code.

Key Concepts:
1. type_annotation_map:
   A dictionary defined on the DeclarativeBase that links Python types 
   (or custom TypeAliases) to specific SQLAlchemy Type objects. 
   Whenever the ORM sees a specific type in a Mapped[] hint, it automatically 
   applies the mapped SQL configuration.

2. Domain-Driven Design (DDD):
   By using custom types like 'str_20' or 'int_big', you define the 
   business rules of your data (e.g., "all names are 100 characters max") 
   in one central location.

3. Reusability:
   Changes made to the 'type_annotation_map' reflect across every table 
   in the system, making large-scale schema refactoring much safer.
"""

from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from utils import int_big, str_20, str_100

engine = create_engine('sqlite:///ep_10_custom_annotations.db', echo=True)


class Base(DeclarativeBase):
    """
    The Central Registry with Global Type Mapping.
    
    Attributes:
        type_annotation_map (dict): Overrides default SQLAlchemy behavior. 
            Here, we've told the ORM that whenever a standard Python 'int' 
            is used in a Mapped hint, it should default to 'int_big' 
            (BigInteger) instead of the standard Integer.
    """
    type_annotation_map = {
        int: int_big,
    }


class User(Base):
    """
    Represents the 'users' table using custom type hints.
    
    Class Attributes:
        id (Mapped[int]): Because of the Base.type_annotation_map, this 
            'int' automatically becomes a BigInteger in the database.
            
        first_name (Mapped[Optional[str_20]]): Uses a custom string type 
            imported from utils. The ORM automatically treats this as 
            VARCHAR(20) and allows NULLs.
            
        last_name (Mapped[Optional[str_100]]): Uses a custom string type 
            mapping to VARCHAR(100).
    """
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)

    # These columns are fully defined by their type hints alone!
    first_name: Mapped[Optional[str_20]]
    last_name: Mapped[Optional[str_100]]


# Create the database tables
Base.metadata.create_all(engine)
