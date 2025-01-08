from uuid import uuid4
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, Integer, ForeignKey
from .base import Base

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    artist_id: Mapped[int] = mapped_column(ForeignKey("artists.id"))

    message_orig: Mapped[str] = mapped_column(Text)
    message_eng: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    message_zh_tw: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    message_orig_discord_id: Mapped[str] = mapped_column(String(100))
    message_eng_discord_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    message_zh_tw_discord_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    is_fan_message: Mapped[bool] = mapped_column(default=False)
    response_to_fan_message_uuid: Mapped[Optional[str]] = mapped_column(ForeignKey("messages.uuid"), nullable=True)

    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, processing, completed, failed
    error_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
            


class RawMessage(BaseModel):
    artist_message: str = ""
    fan_message: Optional[str] = None

    def __repr__(self):
        return str(self)

    def __str__(self):
        if self.fan_message:
            return f">{self.fan_message}\n{self.artist_message}"
        else:
            return f"{self.artist_message}"