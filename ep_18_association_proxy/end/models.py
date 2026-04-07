# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=jmjuaSVRWPY

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.associationproxy import association_proxy


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)


class UserArticle(Base):
    """
    Association Table (Middle-man).
    
    This model serves as the join table connecting Users and Articles. 
    It holds the foreign keys required to maintain the Many-to-Many link.
    """
    __tablename__ = 'user_article'

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    article_id: Mapped[int] = mapped_column(ForeignKey('article.id'))


class User(Base):
    """
    Represents a User with proxied access to Article data.
    
    Attributes:
        articles (Mapped[list[Article]]): The standard M2M relationship.
        article_titles (AssociationProxy): A proxied view that returns 
            a list of strings representing the titles of all related articles.
    """
    __tablename__ = 'user'

    name: Mapped[str] = mapped_column(String(50))
    articles: Mapped[list['Article']] = relationship(
        back_populates='users',
        secondary='user_article'
    )

    # This was added
    # Association proxy: jump straight to article titles
    article_titles: Mapped[list[str]] = association_proxy('articles', 'title')


class Article(Base):
    """
    Represents an Article with proxied access to User data.
    
    Attributes:
        title (Mapped[str]): The title of the article.
        users (Mapped[list[User]]): The standard M2M relationship.
        users_name (AssociationProxy): A proxied view that returns 
            a list of strings representing the names of all authors.
    """
    __tablename__ = 'article'

    title: Mapped[str] = mapped_column(String(100))
    users: Mapped[list[User]] = relationship(
        back_populates='articles',
        secondary='user_article'
    )

    # Association proxy: jump straight to user names
    users_name: Mapped[list[str]] = association_proxy('users', 'name')
