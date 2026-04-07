"""
SQLAlchemy Hybrid Attributes and Methods

This module illustrates the implementation of Hybrid Properties and Hybrid 
Methods. These tools allow developers to define Python-level logic that 
SQLAlchemy can automatically translate into SQL expressions for use in 
'where' clauses and 'order_by' statements.

Key Concepts:
1. The @hybrid_property Decorator:
   Defines a property that can be accessed on an instance (e.g., user.full_name) 
   but also used as a class-level attribute in queries 
   (e.g., session.query(User).filter(User.full_name == 'John Doe')).

2. The .expression Modifier:
   Explicitly defines the SQL translation for a hybrid property. While simple 
   logic is often auto-translated, the .expression block is used for 
   complex string concatenations or math that varies between Python and SQL.

3. The @hybrid_method Decorator:
   Similar to the property, but allows for arguments. It enables 
   parameterized logic (like age calculations) to be used both in 
   Python logic and as part of a database-side filter.
"""

from datetime import date

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import create_engine
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

engine = create_engine('sqlite:///:memory:', echo=False)


class Base(DeclarativeBase):
    """
    Standard Declarative Base for ORM mapping.
    """
    id: Mapped[int] = mapped_column(primary_key=True)


class User(Base):
    """
    Represents a system User with calculated attributes.
    
    Attributes:
        first_name (Mapped[str]): User's given name.
        last_name (Mapped[str]): User's family name.
        birth_year (Mapped[int]): Four-digit year of birth.
        
    Hybrid Members:
        full_name (hybrid_property): Combines names into a single string. 
            In SQL, this is translated to a concatenation expression 
            (e.g., first_name || ' ' || last_name).
            
        older_than (hybrid_method): Calculates if a user exceeds a specific 
            age based on the current system year.
    """
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    birth_year: Mapped[int]

    def __repr__(self) -> str:
        return f'<User first_name={self.first_name} last_name={self.last_name}>'

    # Regular property that works in Python but NOT in SQL filters
    # @property
    # def full_name(self):
    #     return f'{self.first_name} {self.last_name}'

    @hybrid_property  # Enables a Hybrid property approach
    def full_name(self) -> str:
        """Python-side implementation of full name."""
        # return self.first_name + " " + self.last_name
        # or
        return f'{self.first_name} {self.last_name}'

    @full_name.expression
    def full_name(cls):
        """SQL-side implementation for use in database queries."""
        # # Uses SQL '+' or '||' depending on the DB driver
        return cls.first_name + ' ' + cls.last_name  # Predominently in this syntax; Behaves differently than setting up as an f-string property

    @hybrid_method
    def older_than(self, years: int) -> bool:
        """
        Works in Python: user.older_than(25)
        Works in SQL: session.query(User).filter(User.older_than(25))
        """
        # In a hybrid context, 'date.today().year' becomes a constant in the SQL statement
        return (date.today().year - self.birth_year) > years
