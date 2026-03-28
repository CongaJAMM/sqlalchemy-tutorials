from datetime import date

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import create_engine
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

engine = create_engine('sqlite:///:memory:', echo=False)


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    birth_year: Mapped[int]

    def __repr__(self) -> str:
        return f'<User first_name={self.first_name} last_name={self.last_name}>'

    # Regular property that works in Python but not in SQL filters
    # @property
    # def full_name(self):
    #     return f'{self.first_name} {self.last_name}'

    @hybrid_property
    def full_name(self) -> str:
        # return self.first_name + " " + self.last_name
        # or
        return f'{self.first_name} {self.last_name}'

    @full_name.expression
    def full_name(cls):
        return cls.first_name + ' ' + cls.last_name

    @hybrid_method
    def older_than(self, years: int) -> bool:
        # Imagine we have a birth_year column and we want to compare it to the current year
        # return (2024 - self.birth_year) > age
        return (date.today().year - self.birth_year) > years
