# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=2fwdjkL0jqw

"""
SQLAlchemy Query Options: Lazy, Restrictive, and Attribute-Level Loading

This module demonstrates how to control the "Lazy" side of the SQLAlchemy ORM. 
These options are used to explicitly define what should happen when a 
relationship is NOT eagerly loaded, or to limit the columns returned for 
performance tuning.

--- LOADING STRATEGIES ---

1. Lazy Loading (The "Maybe" Load):
    - lazyload(): The default behavior. Data is fetched only when the attribute 
      is accessed. Best for attributes rarely needed in the current context. Same as having "select" as the lazy parameter in the relationship.
    - noload(): Completely disables loading for a relationship. Accessing the 
      attribute returns an empty collection/None without hitting the database.
    - raiseload(): A "safety switch" that raises an error if the attribute is 
      accessed. Prevents hidden N+1 query issues during development.

2. Attribute-Level Control:
    - load_only(): Restricts the initial SELECT statement to only specific 
      columns of a model, effectively deferring all other columns.

3. Chained & Mixed Loading:
    - You can mix eager and lazy strategies in a single query (e.g., eager load 
      top-level posts but lazy load their nested details).
    - .options() can be chained to apply different strategies at different 
      depths of the object graph.


--- KEY USE CASES ---

- Use raiseload() in production-critical paths to ensure you haven't 
  missed an eager load, avoiding accidental database performance degradation.
- Use noload() for complex objects where you want to explicitly hide 
  sensitive or heavy relationships from certain views.
- Use load_only() for "thin" queries where you only need a specific field 
  (like a status flag or ID) from a table with many columns.
"""

from sqlalchemy import select
from sqlalchemy.orm import (
    contains_eager,
    joinedload,
    lazyload,
    load_only,
    noload,
    raiseload,
)

from models import Detail, Post, User, session


# =============================================================================================
# Lazy Loading

print('=' * 40)
print('\nLoading with the: `noload` function')
query = session.query(User).options(noload(User.posts))
print(query)
print(query.all())


print('=' * 40)
print('\nLoading with the: `lazyload` function')
query = session.query(User).options(lazyload(User.posts))
print(query)
print(query.all())


# raiseload()
print('=' * 40)
print('\nLoading with the: `raiseload` function')
query = session.query(User).options(raiseload(User.posts))
print(query)
print(query.all())

# Similar to above
# '*': Applies loading techniques to all related entities in the query.
query = session.query(User).options(raiseload('*'))
print(query)
print(query.all())

# =============================================================================================
# Calling .options() allows to add more query options to relationship data that are nested
print('=' * 40)
print('\nMore `.options()` loading')
print('\nApply `load_only()` to only load selected columns')
query = (
    session.query(User)
    .outerjoin(Post)
    .options(
        contains_eager(User.posts).options(joinedload(Post.detail), load_only(Post.id))
    )
)
print(query)

print('=' * 40)
print('\nMore `.options()` loading with chaining')
query = session.query(User).options(
    joinedload(User.posts).options(joinedload(Post.detail), load_only(Post.id))
)
print(query)

# Calling .options() allows to add more query options to relationship data
print('=' * 40)
print('\nLoad only the Post id for all Posts for a User')
query = session.query(User).options(joinedload(User.posts).load_only(Post.id))
print(query)

print('=' * 40)
print("\nLoad all Posts for User and only the Detail's content for each post")
query = session.query(User).options(
    joinedload(User.posts).joinedload(Post.detail).load_only(Detail.content)
)
print(query)

# =============================================================================================
# load_only()
print('=' * 40)
print('\nUsing the: `load_only` function in options')
print('\nApply `load_only()` to only load selected columns')
query = select(User).options(joinedload(User.posts).options(load_only(Post.active, Post.date)))  # Can add raiseload to deffer other Post columns
print(query)


# NOTE: Need to add unique() when adding a joinedload or
# contains_eager when using `select()` loading relationship
print(session.scalars(query).unique().all())

# =============================================================================================
# Multiple Loading

print('=' * 40)
print('\nJoin load the posts, lazily load the preferences')
query = (
    session.query(User)
    .options(
        joinedload(User.posts),
        lazyload(User.preference)
    )
)
print(query)
print(query.all())

# =============================================================================================
# Chained Loading

print('=' * 40)
print('\nApply Chained loading')
query = (
    session.query(User)
    .options(
        joinedload(User.posts)
        .lazyload(Post.detail)
    )
)
print(query)
print(query.all())
