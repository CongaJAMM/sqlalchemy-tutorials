# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=iosh_DWnliE

"""Example #3

Doctor-Patient Many-to-Many Relationship Module (Association MODEL Pattern)

This module demonstrates a Many-to-Many relationship implemented via an 
explicit Association Class. This pattern is used when the relationship 
between two entities (Doctor and Patient) carries its own attributes.

Key Concepts:
1. Association Object Pattern: 
   Instead of a simple link table, 'Appointment' acts as a middle-man 
   containing Foreign Keys to both 'Doctor' and 'Patient'.

2. Relationship with Extra Data: 
   The 'appointments' table stores more than just IDs; it stores 
   'appointment_date' and 'notes', which belong specifically to the 
   interaction between a doctor and a patient.

3. backref vs back_populates: 
   This module uses 'backref', which is a shortcut that automatically 
   declares the relationship on the related class (Doctor and Patient) 
   without having to write it manually in those classes.
"""

from datetime import datetime

from sqlalchemy import Column, Date, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

db_url = 'sqlite:///ep_08_doctor_patient.db'

engine = create_engine(db_url)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class Appointment(Base):
    """
    The Association MODEL representing the link between Doctors and Patients.
    
    This class functions as the 'Center' of the Many-to-Many relationship.
    
    Attributes:
        doctor_id (FK): Links to the specific Doctor.
        patient_id (FK): Links to the specific Patient.
        appointment_date (Date): The specific time the interaction occurs.
        notes (String): Medical or administrative notes for this specific visit.

    ORM Attributes:
        doctor (relationship): Accesses the Doctor object. Creates an 
                               '.appointments' list on the Doctor class via backref.
        patient (relationship): Accesses the Patient object. Creates an 
                                '.appointments' list on the Patient class via backref.
    """
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True)
    doctor_id = Column(Integer, ForeignKey('doctors.id'))
    patient_id = Column(Integer, ForeignKey('patients.id'))
    appointment_date = Column(Date, default=datetime.now)
    notes = Column(String)

    doctor = relationship('Doctor', backref='appointments')
    patient = relationship('Patient', backref='appointments')

    def __repr__(self):
        return f'<Appointment on {self.appointment_date}>'


class Doctor(Base):
    """
    Represents the 'doctors' table.
    
    Through the Appointment backref, this class dynamically gains an 
    '.appointments' attribute which returns a list of Appointment objects.
    """
    __tablename__ = 'doctors'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    specialty = Column(String)


class Patient(Base):
    """
    Represents the 'patients' table.
    
    Through the Appointment backref, this class dynamically gains an 
    '.appointments' attribute which returns a list of Appointment objects.
    """
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    dob = Column(Date)


Base.metadata.create_all(engine)

# If there is data in the database, don't add more data
if session.query(Appointment).count() < 1:
    dr_smith = Doctor(name='Dr. Smith', specialty='Cardiology')
    john_doe = Patient(name='John Doe', dob=datetime(1990, 1, 1))
    appointment = Appointment(
        doctor=dr_smith, patient=john_doe, notes='Routine check-up'
    )

    session.add_all([dr_smith, john_doe, appointment])
    session.commit()

# Find all appointments for Dr. Smith
appointments_for_dr_smith = (
    session.query(Appointment).filter(Appointment.doctor.has(name='Dr. Smith')).all()
)
print("Dr. Smith's appointments")
print(appointments_for_dr_smith)

# Find all appointments for John Doe
appointments_for_john_doe = (
    session.query(Appointment).filter(Appointment.patient.has(name='John Doe')).all()
)

print("John Doe's appointments")
print(appointments_for_john_doe)
