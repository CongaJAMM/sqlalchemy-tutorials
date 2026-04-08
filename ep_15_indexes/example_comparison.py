# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# https://www.youtube.com/watch?v=WsDVBEmTlaI

"""Example #4

SQLAlchemy Performance Benchmarking: The Impact of Database Indexing

This module compares two identical tables—one with a B-Tree index and one 
without—to measure the real-world performance delta between them. 

Key Concepts:
1. Retrieval Speed (The Gain):
   Without an index, the database must perform a 'Full Table Scan' (O(N)), 
   checking every single row. With an index, the database uses a 
   highly optimized search structure (O(log N)), allowing it to find 
   specific records almost instantly.

2. Insertion Overhead (The Cost):
   Every time a row is added to an indexed table, the database must 
   also update the index tree. This requires additional CPU cycles and 
   Disk I/O, making bulk inserts measurably slower.

3. Optimization Balance:
   Indexing should be applied strategically to columns frequently used 
   in WHERE clauses, JOINs, or ORDER BY statements, but avoided on 
   write-heavy tables where read performance is not a priority.

Benchmarking Workflow:
- Bulk insert 500,000 rows into both tables.
- Measure and compare the time taken for 'insert_data'.
- Query a specific record from both tables.
- Measure and compare the time taken for 'fetch_data'.
"""

from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy import create_engine, String, Sequence
import time

# Set up the SQLite database
engine = create_engine('sqlite:///example.db', echo=False)

# Optional set to memory instead of a file
# engine = create_engine('sqlite:///:memory:', echo=False)


class Base(DeclarativeBase):
    """
    Standard Declarative Base for SQLAlchemy 2.0.
    
    Attributes:
        id (Mapped[int]): A primary key using a Sequence for ID generation. 
            Primary keys are indexed by default in almost all SQL engines.
    """
    id: Mapped[int] = mapped_column(Sequence('id_seq'), primary_key=True)


class WithoutIndex(Base):
    """
    Represents a table with no optimizations on the 'data' column.
    
    This model serves as the 'Control' group. Any query filtering by 
    the 'data' column will require the database to scan the table 
    from top to bottom until the record is found.
    """
    __tablename__ = 'without_index'
    data: Mapped[str] = mapped_column(String(50))


class WithIndex(Base):
    """
    Represents a table with an explicit B-Tree index on the 'data' column.
    
    This model serves as the 'Experimental' group. Setting index=True 
    tells the database to maintain a separate search structure for 
    this column, optimizing lookups at the expense of slower writes.
    """
    __tablename__ = 'with_index'
    data: Mapped[str] = mapped_column(String(50), index=True)


# Database connection
engine = create_engine('sqlite:///example.db')
Base.metadata.create_all(engine)

# Create session
s = sessionmaker(bind=engine)
session: Session = s()


# Function to insert data into a table
def insert_data(session: Session, model: WithoutIndex | WithIndex, num_rows: int):
    start_time = time.perf_counter()
    models = []
    for i in range(num_rows):
        if i % 10_000 == 0:
            print(f'\r{i:>10,} / {num_rows:,}', end='\r')
            session.bulk_save_objects(models)
            models = []

        models.append(model(data=f'data_{i}'))

    session.bulk_save_objects(models)
    session.commit()
    end_time = time.perf_counter()
    return round(end_time - start_time, 4)


def fetch_data(session: Session, model: WithoutIndex | WithIndex):
    start_time = time.perf_counter()
    _ = session.query(model).filter(model.data == 'data_5343').first()
    end_time = time.perf_counter()
    return round(end_time - start_time, 4)


def calc_time(start, end):
    value = round((end - start) / start, 2) * 100
    return abs(value)


# =============================================================
#                       INSERTING DATA
# =============================================================
# Insert data into table without index
num_rows = 500_000
print(f'Writing Data - {num_rows:,} rows without an index')
time_without_index = insert_data(session, WithoutIndex, num_rows)
print(
    f'Time to insert {num_rows:,} rows without index: {time_without_index:,} seconds\n'
)

# Insert data into table with index
print(f'Writing Data - {num_rows:,} rows with an index')
time_with_index = insert_data(session, WithIndex, num_rows)
print(f'Time to insert {num_rows:,} rows with index: {time_with_index:,} seconds\n')

diff = calc_time(time_without_index, time_with_index)
print(f'Adding index increased inserting data time by: {diff:.2f}% 😱😱\n\n')


# =============================================================
#                       QUERYING DATA
# =============================================================
print('Reading Data')
num_rows = session.query(WithoutIndex).count()
time_without_index = fetch_data(session, WithoutIndex)
print(f'Time to query {num_rows:,} rows without index: {time_without_index:,} seconds')

num_rows = session.query(WithIndex).count()
time_with_index = fetch_data(session, WithIndex)
print(f'Time to query {num_rows:,} rows with index: {time_with_index:,} seconds')

diff = calc_time(time_without_index, time_with_index)
print(f'Adding index sped up query by: {diff:.2f}% 🎉🎉\n\n')


# =============================================================
#                       CLEAN UP SESSION
# =============================================================
session.close()
