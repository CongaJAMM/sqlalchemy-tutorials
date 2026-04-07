# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=iosh_DWnliE

"""Example #2

Many-to-Many Relationship Module (Association Class Pattern)

This module demonstrates a Many-to-Many relationship where the bridge between 
two tables (Student and Course) is defined as a full ORM Class rather than 
a simple Table variable.

Key Concepts:
1. Association Class: 
   'StudentCourse' is a complete SQLAlchemy model with its own Primary Key. 
   This is the preferred setup if you anticipate needing to add extra 
   fields to the relationship (like 'enrollment_date' or 'grade') later.

2. String-Based 'secondary' Reference:
   Instead of passing a table variable, we pass the string name of the 
   association table ('student_course'). SQLAlchemy resolves this string 
   to the StudentCourse.__tablename__ at runtime.

3. Direct Collection Access:
   Despite having a class in the middle, the 'secondary' configuration allows 
   you to skip the middle-man in code. Calling 'student.courses' returns a 
   list of Course objects, not StudentCourse objects.
"""

from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

db_url = 'sqlite:///ep_08_table_class.db'

engine = create_engine(db_url)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


# Association table
class StudentCourse(Base):
    """
    The Association Class acting as the bridge between Students and Courses.
    
    Attributes:
        id: Unique identifier for the enrollment record.
        student_id: Foreign Key pointing to the student.
        course_id: Foreign Key pointing to the course.
    """
    __tablename__ = 'student_course'
    id = Column(Integer, primary_key=True)
    student_id = Column('student_id', Integer, ForeignKey('students.id'))
    course_id = Column('course_id', Integer, ForeignKey('courses.id'))


class Student(Base):
    """
    Represents the 'students' table.
    
    ORM Attributes:
        courses (relationship): A direct list of Course objects. The 'secondary' 
            parameter tells SQLAlchemy to look through the 'student_course' 
            table to find the associated records.
    """
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    courses = relationship(
        'Course', secondary='student_course', back_populates='students'
    )


class Course(Base):
    """
    Represents the 'courses' table.
    
    ORM Attributes:
        students (relationship): A direct list of Student objects enrolled 
            in this specific course.
    """
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    
    students = relationship(
        'Student', secondary='student_course', back_populates='courses'
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
