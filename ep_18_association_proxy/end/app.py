# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=jmjuaSVRWPY

"""
SQLAlchemy Association Proxy: Many-to-Many Shortcut Pattern

This module demonstrates the use of 'association_proxy' to flatten many-to-many 
relationships. It allows for a more Pythonic interface where collections 
of related objects appear as simple lists of strings.

Key Concepts:
1. Attribute Proxying:
   The 'association_proxy' creates a read/write view of a specific attribute 
   across a relationship. In this case, jumping from a 'User' through 
   the 'articles' relationship directly to the 'title' field.

2. Transparent Navigation:
   Instead of list comprehensions like '[a.title for a in user.articles]', 
   the proxy provides 'user.article_titles' as a direct property.

3. Bi-directional Proxying:
   The pattern is applied to both sides of the relationship, allowing 
   Articles to list 'users_name' just as easily as Users list 'article_titles'.

4. Relationship Maintenance:
   The proxy remains in sync with the underlying relationship. Appending 
   a new Article object to 'user.articles' automatically updates the 
   'user.article_titles' proxy view.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Base, User, Article

engine = create_engine('sqlite://', echo=False)
Base.metadata.create_all(engine)

with Session(engine) as session:
    zeq = User(name='Zeq Tech')
    mark = User(name='Mark')
    art1 = Article(title='Intro to SQLAlchemy')
    art2 = Article(title='Advanced Python Tips')

    zeq.articles.extend([art1, art2])
    mark.articles.append(art1)

    session.add_all([zeq, mark, art1, art2])
    session.commit()

    # Print article titles for each user
    print(zeq.article_titles)    # OUTPUT = ['Intro to SQLAlchemy', 'Advanced Python Tips']
    print(mark.article_titles)    # OUTPUT = ['Intro to SQLAlchemy']

    # Print user names for each article
    print(art1.users_name)    # OUTPUT = ['Zeq Tech', 'Mark']
    print(art2.users_name)    # OUTPUT = ['Zeq Tech']
