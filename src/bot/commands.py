import discord
from discord import app_commands
from typing import Dict, Optional
from ..database.session import db
from ..models.artist import Artist
from ..models.message import Message
from datetime import datetime, timedelta
import json

class Commands:
    def __init__(self, bot: discord.Client):
        self.bot = bot

    async def setup(self, tree: app_commands.CommandTree):
        @tree.command(name="mirror_channel", description="Create mirror channels for an artist")
        async def mirror_channel(interaction: discord.Interaction, artist_name: str):
            await interaction.response.defer()
            
            with db.get_session() as session:
                # Check if artist exists
                artist = session.query(Artist).filter(Artist.name == artist_name).first()
                if not artist:
                    # Create artist with default prompts
                    artist = Artist(name=artist_name, prompt={"prompt": f"The artist name is {artist_name}."})
                    session.add(artist)
                
                try:
                    # Create channels
                    category = await interaction.guild.create_category(f"{artist_name} Translations")
                    channels = {}
                    
                    for suffix, attr in [
                        ('original', 'channel_orig'),
                        ('eng', 'channel_eng'),
                        ('zh-tw', 'channel_zh_tw')
                    ]:
                        channel = await interaction.guild.create_text_channel(
                            f"{artist_name}_{suffix}",
                            category=category
                        )
                        setattr(artist, attr, channel.id)
                        channels[suffix] = channel.id
                    
                    session.commit()
                    await interaction.followup.send(
                        f"Created mirror channels for {artist_name}!",
                        ephemeral=True
                    )
                except Exception as e:
                    session.rollback()
                    await interaction.followup.send(
                        f"Error creating channels: {str(e)}",
                        ephemeral=True
                    )

        @tree.command(name="show", description="Show translation prompt for an artist")
        async def show(interaction: discord.Interaction, artist_name: str):
            with db.get_session() as session:
                artist = session.query(Artist).filter(Artist.name == artist_name).first()
                if not artist:
                    await interaction.response.send_message(
                        f"No translation prompt found for artist: {artist_name}",
                        ephemeral=True
                    )
                    return

                embed = discord.Embed(title=f"Translation Prompt for {artist_name}")
                embed.add_field(name="Prompt", value=artist.prompt.get("prompt", "No prompt set")[:1024], inline=False)
                
                await interaction.response.send_message(embed=embed, ephemeral=True)

        @tree.command(name="modify", description="Modify translation prompt for an artist")
        async def modify(interaction: discord.Interaction, artist_name: str):
            with db.get_session() as session:
                artist = session.query(Artist).filter(Artist.name == artist_name).first()
                if not artist:
                    await interaction.response.send_message(
                        f"Artist {artist_name} not found. Create mirror channels first.",
                        ephemeral=True
                    )
                    return

                # Create text input field
                modal = PromptModal(artist_name)
                modal.prompt.default = artist.prompt.get('prompt', '')
                
                await interaction.response.send_modal(modal)

class PromptModal(discord.ui.Modal, title='Modify Translation Prompt'):
    def __init__(self, artist_name: str):
        super().__init__()
        self.artist_name = artist_name
        self.prompt = discord.ui.TextInput(
            label='Translation Prompt',
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000,
            placeholder="Enter the translation prompt for this artist..."
        )
        self.add_item(self.prompt)

    async def on_submit(self, interaction: discord.Interaction):
        with db.get_session() as session:
            artist = session.query(Artist).filter(Artist.name == self.artist_name).first()
            if artist:
                artist.prompt = {"prompt": self.prompt.value}
                session.commit()
                await interaction.response.send_message(
                    f"Updated translation prompt for {self.artist_name}!",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"Artist {self.artist_name} not found.",
                    ephemeral=True
                )
