import discord
from discord import app_commands
from ..config.config import Config
from ..translation.translator import Translator
from ..database.session import db
from ..models.artist import Artist
from ..models.message import Message, MessageContext
from .commands import Commands
from datetime import datetime, timedelta
import asyncio

class TranslatorBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.all()
        intents.message_content = True
        super().__init__(intents=intents)
        
        self.config = Config()
        self.translator = Translator(self.config.openai_api_key)
        self.tree = app_commands.CommandTree(self)
        self.commands = Commands(self, self.translator)

    async def setup_hook(self):
        """Set up command handlers and sync commands"""
        await self.commands.setup(self.tree)
        await self.tree.sync()
        
        # Create database tables
        db.create_tables()

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')

    async def process_message(self, message: Message, artist: Artist, db_session):
        """Process a single message through the translation pipeline"""
        try:
            # First translation attempt
            translation_response = await self.translator.translate(
                message.message_orig, 
                artist,
                db_session
            )
            
            if translation_response.needs_context:
                # Get context messages and try again
                context_messages = await self.translator.get_context_messages(
                    message,
                    db_session,
                    translation_response.n_required_context or 3
                )
                
                translation_response = await self.translator.translate_with_context(
                    context_messages,
                    artist
                )
            
            # Safety check
            safety_results = await self.translator.safety_check(translation_response.translations)
            
            if not all(safety_results.values()):
                # Retry with more conservative prompts
                translation_response = await self.translator.translate(
                    message.message_orig,
                    artist,
                    db_session,
                    conservative=True
                )
            
            # Update message with translations
            message.message_eng = translation_response.translations.get('eng')
            message.message_zh_tw = translation_response.translations.get('zh-tw')
            message.status = 'completed'
            db_session.commit()
            
            # Send translations to respective channels
            for lang, channel_attr in [('eng', 'channel_eng'), ('zh-tw', 'channel_zh_tw')]:
                if channel_id := getattr(artist, channel_attr):
                    channel = self.get_channel(channel_id)
                    if channel:
                        sent_message = await channel.send(translation_response.translations[lang])
                        message.message_discord_id = str(sent_message.id)
                        db_session.commit()
            
        except Exception as e:
            message.retry_count += 1
            if message.retry_count >= 3:
                message.status = 'failed'
                message.error_reason = str(e)
            db_session.commit()

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

            # Create new message record
            message = Message(
                artist_id=artist.id,
                message_orig=discord_message.content,
                status='pending'
            )
            session.add(message)
            
            # Check for context
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            prev_message = session.query(Message).filter(
                Message.artist_id == artist.id,
                Message.created_at > cutoff_time
            ).order_by(Message.created_at.desc()).first()
            
            if prev_message:
                # Add to existing context group
                context = MessageContext(
                    message=message,
                    context_group=prev_message.contexts[0].context_group,
                    parent_message_id=prev_message.id
                )
            else:
                # Create new context group
                message.is_context_root = True
                context = MessageContext(
                    message=message,
                    context_group=f"group_{message.id}"
                )
            
            session.add(context)
            session.commit()
            
            # Process the message
            asyncio.create_task(self.process_message(message, artist, session))

def main():
    bot = TranslatorBot()
    bot.run(bot.config.discord_token)
