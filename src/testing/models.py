"""
Test helper models that don't require database initialization.
"""

from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class TestArtist:
    """Simple artist class for testing without database dependencies."""
    name: str
    prompt: Dict
    channel_orig: Optional[int] = None
    channel_eng: Optional[int] = None
    channel_zh_tw: Optional[int] = None
