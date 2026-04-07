# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=KNxVG4OcboY

"""Example #5

SQLAlchemy Relationship Loading: Write-Only ('write_only')

This module demonstrates the 'Write-Only' strategy, a strict access control 
mechanism that allows appending data to a relationship while completely 
disabling ORM-based reads.

Core Concept: 
    - The relationship is "blind" to existing data in the database.
    - user.logs.add(new_log) works perfectly to insert new records.
    - user.logs (reading the attribute) will raise an AttributeError or 
      similar exception depending on the SQLAlchemy version.

Advantages:
    - Maximum Performance: No data is ever "hydrated" (converted to Python objects) 
      when you interact with the parent.
    - High-Volume Writing: Ideal for tables with millions of rows (like logs) 
      where you only ever want to append new entries.
    - Strict Security: Prevents accidental loading of massive datasets into memory.

When to Use:
    - Audit trails and Activity Logs.
    - Event sourcing (where you only append new events).
    - High-write scenarios where reads are handled by a separate reporting service.
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

db_url = 'sqlite:///ep_09_write_only_database.db'

engine = create_engine(db_url, echo=True)  # important

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class User(Base):
    """
    Represents the 'users' table.
    
    ORM Attributes:
        logs (relationship): Configured with lazy='write_only'.
            This attribute acts as a write-only sink. You can use 'user.logs.add()' 
            to link new Log entries, but 'user.logs' cannot be iterated or 
            queried directly through this attribute.
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    # The Drop-Box: Only accepts new data; does not reveal old data.
    logs = relationship('Log', backref='user', lazy='write_only')

    def __repr__(self):
        return f'<User {self.name} >'


class Log(Base):
    """
    Represents the 'logs' table.
    
    This is typically a high-volume table where individual records are 
    inserted frequently but rarely read back through the User object.
    """
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    message = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id'))

    def __repr__(self):
        return f'<Log{self.id} >'


Base.metadata.create_all(engine)

# If there is data in the database, don't add more data
if session.query(User).count() < 1:
    session.add_all(
        [
            User(
                name=f'User {y}',
                logs=[Log(message=f'User did this thing') for x in range(3)],
            )
            for y in range(10)
        ]
    )
    session.commit()

users = session.query(User).all()

# ==== INVALID METHOD ===
for user in users:
    print(f"Accessing User: '{user.name}'")

    try:
        for log in user.logs:  # ❌ Will raise: write_only prevents reading the relationship
            print(log.message)
    except Exception as e:
        print(e)


# ==== VALID METHOD ===
for user in users:
    print(f"Accessing User: '{user.name}'")

    # if you actually need to see the logs, you must query the Log table directly.
    logs = session.query(Log).filter(Log.user_id == user.id).all()
    try:
        for log in logs:
            print(log.message)
    except Exception as e:
        print(e)
