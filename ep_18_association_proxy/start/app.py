# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=jmjuaSVRWPY

"""
SQLAlchemy Many-to-Many Relationships and Association Proxies

This module illustrates the standard navigation of a many-to-many relationship 
between Users and Articles. 

--- THE ROLE OF ASSOCIATION PROXY ---

An 'association_proxy' is a powerful tool from 'sqlalchemy.ext.associationproxy' 
that provides a read/write view of a specific attribute across a relationship.

How it would help this module:
1. Syntax Simplification:
   Instead of writing:
   [article.title for article in zeq.articles]
   
   You could define an association proxy 'article_titles' and simply call:
   zeq.article_titles

2. Direct Manipulation:
   You could add an article to a user just by appending a string to the proxy:
   zeq.article_titles.append("New SQLAlchemy Guide")
   SQLAlchemy would automatically handle the creation of the Article object 
   and the link in the association table.

3. Cleaner Data Access:
   It effectively "flattens" the object graph, making the model behave more 
   like a standard Python dictionary or list of primitives rather than a 
   complex collection of ORM objects.

Key Concepts:
- Relationship Navigation: Accessing related objects (zeq.articles).
- Collection Manipulation: Using .append() and .extend() to manage links.
- Flattening: Reducing nested object access (article.title) into direct 
  attribute access via proxying.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Base, User, Article

engine = create_engine('sqlite:///:memory:', echo=False)
Base.metadata.create_all(engine)

with Session(engine) as session:
    zeq = User(name='Zeq Tech')
    mark = User(name='Mark')
    art1 = Article(title='Intro to SQLAlchemy')
    art2 = Article(title='Advanced Python Tips')

    zeq.articles.extend([art1, art2])
    mark.articles.append(art1)

    session.add_all([zeq, mark])
    session.commit()

    # Print article titles for each user
    print([article.title for article in zeq.articles])
    print([article.title for article in mark.articles])

    # Print user names for each article
    print([user.name for user in art1.users])
    print([user.name for user in art2.users])
