# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=YSFODnf_eoA

from sqlalchemy.orm import Session
from models import User, engine, Base

Base.metadata.create_all(engine)

with Session(engine) as session:
    session.add_all(
        [
            User(first_name='Zeq', last_name='Tech', birth_year=1995),
            User(first_name='Alan', last_name='Walker', birth_year=1997),
        ]
    )
    session.commit()

    zeq = session.query(User).first()

    # ✅ Works in Python
    print(zeq.full_name)

    # ✅ Also works in SQL filters
    print(session.query(User).filter(User.full_name == 'Zeq Tech').all())
    print(session.query(User).filter(User.full_name.like('Zeq%')).all())
    # The % is a wildcard character in SQL, matching any
    # sequence of characters after 'Zeq'

    # Hybrid method example in Python
    print(zeq.older_than(25))

    # Hybrid method example in SQL filters
    print(session.query(User).filter(User.older_than(25)).all())
