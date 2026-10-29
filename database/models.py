from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base


class PublicationUser(Base):
    __tablename__ = "publication_users"

    user_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    publications = relationship(
        "Publication",
        back_populates="creator",
    )

    likes = relationship(
        "PublicationLike",
        back_populates="user",
    )


class Publication(Base):
    __tablename__ = "publications"

    publication_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    publication_element: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    publication_content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    publication_is_numeric: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    publication_layer: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    publication_filtering: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    publication_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="draft",
    )

    publication_image: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    publication_video: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    publication_created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    publication_formed_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    publication_creator_id: Mapped[int] = mapped_column(
        ForeignKey("publication_users.user_id"),
        nullable=False,
    )

    creator = relationship(
        "PublicationUser",
        back_populates="publications",
    )

    likes = relationship(
        "PublicationLike",
        back_populates="publication",
    )


class PublicationLike(Base):
    __tablename__ = "publication_likes"

    publication_like_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    publication_id: Mapped[int] = mapped_column(
        ForeignKey("publications.publication_id"),
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("publication_users.user_id"),
        nullable=False,
    )

    publication = relationship(
        "Publication",
        back_populates="likes",
    )

    user = relationship(
        "PublicationUser",
        back_populates="likes",
    )