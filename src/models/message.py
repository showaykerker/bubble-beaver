from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Integer, ForeignKey, Boolean
from typing import Optional, List
from .base import Base

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    artist_id: Mapped[int] = mapped_column(ForeignKey("artists.id"))
    message_orig: Mapped[str] = mapped_column(Text)
    message_eng: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    message_zh_tw: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    message_discord_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, processing, completed, failed
    error_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    context_order: Mapped[int] = mapped_column(Integer, default=0)
    is_context_root: Mapped[bool] = mapped_column(Boolean, default=False)

    # Define relationships
    contexts: Mapped[List["MessageContext"]] = relationship(
        "MessageContext",
        back_populates="message",
        foreign_keys="MessageContext.message_id",
        cascade="all, delete-orphan"
    )
    parent_contexts: Mapped[List["MessageContext"]] = relationship(
        "MessageContext",
        back_populates="parent_message",
        foreign_keys="MessageContext.parent_message_id",
        cascade="all, delete-orphan"
    )

class MessageContext(Base):
    __tablename__ = "message_contexts"

    id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id"))
    context_group: Mapped[str] = mapped_column(String(100))
    parent_message_id: Mapped[Optional[int]] = mapped_column(ForeignKey("messages.id"), nullable=True)

    # Define relationships
    message: Mapped[Message] = relationship(
        Message,
        back_populates="contexts",
        foreign_keys=[message_id]
    )
    parent_message: Mapped[Optional[Message]] = relationship(
        Message,
        back_populates="parent_contexts",
        foreign_keys=[parent_message_id]
    )
