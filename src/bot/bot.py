import discord
from discord import app_commands
from ..config.config import Config
# from ..translation.translator import Translator
from ..database.session import db
from ..models.artist import Artist
from ..models.message import Message, RawMessage
from .commands import Commands
from .message_handler import handle_message
from datetime import datetime, timedelta
import asyncio
from uuid import uuid4

class TranslatorBot(discord.Client):

    def __init__(self):
        intents = discord.Intents.all()
        intents.message_content = True
        super().__init__(intents=intents)
        
        self.config = Config()
        # self.translator = Translator(self.config.openai_api_key)
        self.tree = app_commands.CommandTree(self)
        self.commands = Commands(self)

    async def setup_hook(self):
        """Set up command handlers and sync commands"""
        await self.commands.setup(self.tree)
        await self.tree.sync()
        
        # Create database tables
        db.create_tables()

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')

    async def process_message(self, messages: list[Message], artist: Artist, session):
        pass

    async def get_previous_messages(self, artist: Artist, max_messages: int = 10, max_hours: int = 24) -> list[Message]:
        with db.get_session() as session:
            messages = session.query(Message).filter(
                Message.artist_id == artist.id,
                Message.is_fan_message == False,
                Message.status == 'pending',
                Message.created_at > datetime.now() - timedelta(hours=max_hours)
            ).order_by(Message.created_at.desc()).limit(max_messages).all()
            return messages

    async def on_message(self, discord_message: discord.Message):
        """Handle messages in mirror channels"""
        if discord_message.author == self.user:
            return

        with db.get_session() as session:
            # Check if message is in an original channel
            artist = session.query(Artist).filter(
                Artist.channel_orig == discord_message.channel.id
            ).first()
            
            if not artist:
                return

            raw_messages: RawMessage = handle_message(content=discord_message.content, user_name="showay")
            
            messages = await self.get_previous_messages(artist)

            responsing_message_uuid = None
            for raw_message in raw_messages:
                if raw_message.fan_message:
                    responsing_message_uuid = str(uuid4().int >> 64)
                    message = Message(
                        uuid=responsing_message_uuid,
                        artist_id=artist.id,
                        message_orig=raw_message.fan_message,
                        message_orig_discord_id=discord_message.id,
                        is_fan_message=True,
                        status='pending'
                    )
                    messages.append(message)
                    session.add(message)
                    session.commit()
                message = Message(
                    artist_id=artist.id,
                    message_orig=raw_message.artist_message,
                    message_orig_discord_id=discord_message.id,
                    is_fan_message=False,
                    response_to_fan_message_uuid=responsing_message_uuid,
                    status='pending'
                )
                messages.append(message)
                session.add(message)
                session.commit()
                responsing_message_uuid = None
            
            # Process the message
            asyncio.create_task(self.process_message(messages, artist, session))

def main():
    bot = TranslatorBot()
    bot.run(bot.config.discord_token)
