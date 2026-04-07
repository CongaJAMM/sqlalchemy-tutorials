# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=iosh_DWnliE

"""Example #1

Many-to-Many Relationship Module (Standard Association Table Pattern)

This module demonstrates how to link two entities where many records in one 
table relate to many records in another (e.g., a Student has many Courses, 
and a Course has many Students).

Use the Table Variable (as seen here) when you only care about the connection.

Example: "Is Student A in Course B?"
Use an Association Class (like the Appointment example) when the connection itself has data.

Example: "When did the student join the course? What was their final grade?"

Key Concepts:
1. Association Table (Table Variable):
   The 'student_course_link' is a Core SQLAlchemy Table object. It handles 
   the physical "join" logic in the database but does not have its own 
   ORM class because it doesn't store unique attributes of its own.

2. The 'secondary' Argument:
   In the relationship definition, 'secondary' points to the association 
   table. This tells SQLAlchemy to automatically look into that middle 
   table to find the related IDs whenever you access .courses or .students.

3. Clean Many-to-Many:
   Unlike the Association Object pattern, this allows you to skip the 
   middle-man in Python. You can go directly from student.courses without 
   seeing the link table in your code.
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Table, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

db_url = 'sqlite:///ep_08_table_var.db'

engine = create_engine(db_url)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


# --- ASSOCIATION TABLE ---
# This table exists only in the database to link IDs. 
# It is not a class because we don't need to create "Link" objects manually.
student_course_link = Table(
    'student_course',
    Base.metadata,
    Column('student_id', Integer, ForeignKey('students.id')),
    Column('course_id', Integer, ForeignKey('courses.id')),
)


class Student(Base):
    """
    Represents the 'students' table.
    
    A student can enroll in multiple courses.
    
    ORM Attributes:
        courses (relationship): A list of Course objects. SQLAlchemy uses the 
            'student_course_link' table to find all courses associated with 
            this student's ID.
    """
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    # Secondary points to the Table variable above
    # Usually, a relationship looks for a Foreign Key directly on the other table. By adding 'secondary=student_course_link', you are telling SQLAlchemy: "The Foreign Keys aren't in the other table; they are in this specific third table."
    courses = relationship(
        'Course', secondary=student_course_link, back_populates='students'
    )


class Course(Base):
    """
    Represents the 'courses' table.
    
    A single course can be attended by multiple students.
    
    ORM Attributes:
        students (relationship): A list of Student objects. SQLAlchemy 
            automatically queries the association table to populate this list.
    """
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    
    # Usually, a relationship looks for a Foreign Key directly on the other table. By adding 'secondary=student_course_link', you are telling SQLAlchemy: "The Foreign Keys aren't in the other table; they are in this specific third table."
    students = relationship(
        'Student', secondary=student_course_link, back_populates='courses'
    )


Base.metadata.create_all(engine)

# If there is data in the database, don't add more data
if session.query(Course).count() < 1:
    math = Course(title='Mathematics')
    physics = Course(title='Physics')
    bill = Student(name='Bill', courses=[math, physics])
    rob = Student(name='Rob', courses=[math])

    session.add_all([math, physics, bill, rob])
    session.commit()

rob = session.query(Student).filter_by(name='Rob').first()
courses = [course.title for course in rob.courses]
print(f"Rob's Courses: {', '.join(courses)}")

bill = session.query(Student).filter_by(name='Bill').first()
courses = [course.title for course in bill.courses]
print(f"Bill's Courses: {', '.join(courses)}")
