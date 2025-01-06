import os
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        
        self.discord_token = os.getenv('DISCORD_TOKEN')
        if not self.discord_token:
            raise ValueError("DISCORD_TOKEN environment variable is required")
            
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
            
        self.base_dir = Path(__file__).parent.parent.parent
