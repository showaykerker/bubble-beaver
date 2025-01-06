import pytest
from src.database.session import DatabaseSession
from src.models.artist import Artist
from src.models.message import Message
from pathlib import Path
import tempfile
import os

def test_database_initialization():
    # Create a temporary database file
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        # Initialize database
        db = DatabaseSession(db_path)
        
        # Create a test session
        session = db.get_session()
        
        # Create a test artist
        artist = Artist(
            name="IU",
            prompt={"prompt": "IU is a Korean singer known for her sweet voice."}
        )
        session.add(artist)
        session.commit()
        
        # Create a test message
        message = Message(
            artist_id=artist.id,
            message_orig="안녕하세요!",
            message_eng="Hello!",
            message_zh_tw="你好！",
            status="completed"
        )
        session.add(message)
        session.commit()
        
        # Query the database
        queried_artist = session.query(Artist).filter_by(name="IU").first()
        assert queried_artist is not None
        assert queried_artist.name == "IU"
        
        queried_message = session.query(Message).filter_by(artist_id=artist.id).first()
        assert queried_message is not None
        assert queried_message.message_orig == "안녕하세요!"
        assert queried_message.message_eng == "Hello!"
        
    finally:
        # Clean up
        session.close()
        os.unlink(db_path)

if __name__ == "__main__":
    test_database_initialization()
