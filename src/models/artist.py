from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, JSON
from typing import Optional, Dict
from .base import Base

class Artist(Base):
    __tablename__ = "artists"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    prompt: Mapped[Dict] = mapped_column(JSON)
    channel_orig: Mapped[Optional[int]] = mapped_column(nullable=True)
    channel_eng: Mapped[Optional[int]] = mapped_column(nullable=True)
    channel_zh_tw: Mapped[Optional[int]] = mapped_column(nullable=True)
