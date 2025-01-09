import discord
from discord import app_commands
from discord.message import Message as DCMessage
from ..config.config import Config
from ..translation.translator import Translator
from ..database.session import db
from ..models.artist import Artist, FormattedArtist
from ..models.message import Message, RawMessage, FormattedMessage
from ..prompts.base import TranslationResponse
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
        self.translator = Translator(self.config.openai_api_key)
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

    async def process_message(self, messages: list[FormattedMessage], artist: FormattedArtist):
        response: TranslationResponse = await self.translator.translate(artist, messages)

        with db.get_session() as session:
            for translation_of_sentence in response.translations:
                uuid = translation_of_sentence.uuid
                translation_to_language = translation_of_sentence.translations
                translation_dict = dict((ttl.lang, ttl.content) for ttl in translation_to_language)
                english_translation = translation_dict.get('English', None)
                zh_tw_translation = translation_dict.get('#zh-TW', None)
                
                # send message to artist.channel_eng and artist.channel_zh_tw
                english_channel = self.get_channel(artist.channel_eng)
                zh_tw_channel = self.get_channel(artist.channel_zh_tw)
                ##### Should handle if update of translation is needed #####
                message = session.query(Message).filter(Message.uuid == uuid).first()
                is_from_fan_message = message.is_fan_message
                dc_msg_eng: DCMessage = await english_channel.send("> " + english_translation if is_from_fan_message else english_translation)
                dc_msg_zh_tw: DCMessage = await zh_tw_channel.send("> " + zh_tw_translation if is_from_fan_message else zh_tw_translation)

                # Update the message
                if message:
                    message.message_eng = english_translation
                    message.message_zh_tw = zh_tw_translation
                    message.message_eng_discord_id = dc_msg_eng.id
                    message.message_zh_tw_discord_id = dc_msg_zh_tw.id
                    metadata = translation_of_sentence.metadata
                    if metadata:
                        message.confidence = metadata.confidence
                        message.mentioned_artists = str(metadata.mentioned_artists)
                        message.cultural_notes = str(metadata.cultural_notes)
                        message.korean_specific_terms = str(metadata.korean_specific_terms)
                    message.status = 'finished'
                    session.commit()


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
                    uuid=str(uuid4().int >> 64),
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
            
            # First format the messages
            formatted_messages = [FormattedMessage(
                uuid=m.uuid,
                message_orig=m.message_orig,
                is_fan_message=m.is_fan_message,
                response_to_fan_message_uuid=m.response_to_fan_message_uuid,
                status=m.status,
                current_translation={
                    "eng": m.message_eng,
                    "zh_tw": m.message_zh_tw
                }
            ).format() for m in messages]

            formatted_artist = FormattedArtist(
                name=artist.name,
                prompt=artist.prompt,
                channel_eng=artist.channel_eng,
                channel_zh_tw=artist.channel_zh_tw
            )

            # Process the message
            asyncio.create_task(self.process_message(formatted_messages, formatted_artist))

def main():
    bot = TranslatorBot()
    bot.run(bot.config.discord_token)
