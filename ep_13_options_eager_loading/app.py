# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=FI91w7z-CsI

"""
SQLAlchemy Query Options: Eager, Lazy, and Filtered Loading

This module demonstrates how to use the 'sqlalchemy.orm' loading options to 
control how related data is fetched. These options allow you to be 
performant by batching requests or using SQL joins instead of multiple queries.

--- CORE LOADING OPTIONS ---

1. Eager Loading (Fetches data immediately):
    - joinedload(): Uses a SQL JOIN (usually LEFT OUTER) to fetch related data 
      in the same result set as the parent. BEST FOR 1:1 or N:1.
    - selectinload(): Emits a second SELECT statement using an 'IN' clause 
      containing the parent IDs. BEST FOR 1:N collections.
    - subqueryload(): Emits a second SELECT using the original query as a 
      subquery. (Legacy alternative to selectinload).
    - immediateload(): Emits individual SELECT statements for every parent 
      immediately. Useful for self-referential trees with a set 'depth'.

2. Modification & Logic Options:
    - defaultload(): Keeps the model's default loading behavior but allows you to 
      chain further .options() onto the relationship's children.
    - contains_eager(): Used when you manually write a .join() or .outerjoin(). 
      It tells SQLAlchemy that the related data is already in the columns 
      being fetched, allowing you to filter the parent based on the child.
    - load_only(): A "column-level" optimization. It fetches only specific 
      columns, deferring all others.

--- KEY TAKEAWAYS ---
- Used to overwrite the default loading behavior.
- Use joinedload() for single-object relationships (User -> Profile).
- Use selectinload() for list-based relationships (User -> Posts).
- Use contains_eager() when you need to FILTER the parent results based 
  on a child attribute (e.g., "Users who have a Post with ID 1").
- Nesting: You can chain .options() to go deeper into the hierarchy, 
  such as User -> Posts -> Details.
"""

from sqlalchemy import select
from sqlalchemy.orm import (
    contains_eager,
    defaultload,
    immediateload,
    joinedload,
    load_only,
    selectinload,
    subqueryload,
)

from models import Detail, Post, User, session



# =============================================================================================
# Default Loading
print('=' * 40)
print('\nLoading from class structure')
query = session.query(User)
print(query)


# Same as Above
print('=' * 40)
print('\nLoading with the: `defaultload` function')
query = session.query(User).options(defaultload(User.posts))
print(query)

# =============================================================================================
# Eager Loading

print('=' * 40)
print('\nLoading with the: `joinedload` function')
query = session.query(User).options(joinedload(User.posts))
print(query)
print(query.all())

print('=' * 40)
print('\nLoading with the: `subqueryload` function')
query = session.query(User).options(subqueryload(User.posts))
print(query)
print(query.all())

print('=' * 40)
print('\nLoading with the: `immediateload` function')
query = session.query(User).options(immediateload(User.posts))
print(query)
print(query.all())

print('=' * 40)
print('\nLoading with the: `selectinload` function')
query = session.query(User).options(selectinload(User.posts))
print(query)
print(query.all())

# =============================================================================================
# Select use of joinedload and contains_eager
print('=' * 40)
print('\nLoading with the: `joinedload` function')
query = (
    select(User).options(joinedload(User.posts)).filter(Post.detail.has(Detail.id == 1))
)
print(query)
print(session.execute(query).unique().all())

print('=' * 40)
print('\nLoading with the: `contains_eager` function')
query = (
    select(User)
    .outerjoin(Post)
    .options(contains_eager(User.posts))
    .filter(Post.detail.has(Detail.id == 1))
)
print(query)
print(session.execute(query).unique().all())

# Query use of joinedload and contains_eager
print('=' * 40)
print('\nLoading with the: `joinedload` function')
query = (
    session.query(User)
    .options(joinedload(User.posts))
    .filter(Post.detail.has(Detail.id == 1))
)
print(query)
print(query.all())

# contains eager requires us to specify a join condition,
# but also allows us to filter onthe joined data
print('=' * 40)
print('\nLoading with the: `contains_eager` function')
query = (
    session.query(User)
    .outerjoin(Post)
    .options(contains_eager(User.posts))
    .filter(Post.detail.has(Detail.id == 1))
)
print(query)
print(query.all())

# =============================================================================================
# Calling .options() allows to add more query options to relationship data
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
print('\nMore `.options()` loading')
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
# Multiple loadings
print('=' * 40)
print('\nSub Relationship loading')
query = session.query(User).options(selectinload(User.posts).options(joinedload(Post.detail)))
print(query)
print(query.all())

print('=' * 40)
print('\nMultiple relationship loading')
query = session.query(User).options(
    selectinload(User.posts),
    # joinedload(User.<some other relationship on the user table>)
)
print(query)
print(query.all())
