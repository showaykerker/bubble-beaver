from openai import OpenAI
from typing import Dict, Optional, List
import json
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential
from ..models.message import FormattedMessage
from ..models.artist import FormattedArtist
from ..prompts.base import TranslationResponse
from ..prompts.base import TRANSLATION_PROMPT, SUPPORTED_LANGUAGES
from sqlalchemy.orm import Session
from sqlalchemy import select

class Translator:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    async def translate(self, artist: FormattedArtist, messages: List[FormattedMessage]) -> TranslationResponse:

        formatted_prompt = TRANSLATION_PROMPT.format(
            artist_name=artist.name,
            artist_prompt=artist.prompt.get('prompt', "No specific context available."),
            supported_languages=SUPPORTED_LANGUAGES,
        )
        
        response = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": formatted_prompt},
                {"role": "user", "content": "\n".join(messages)}
            ],
            response_format=TranslationResponse
        )

        # Should handle the following error:
        # "message": {
        #   "role": "assistant",
        #   "refusal": "I'm sorry, I cannot assist with that request."
        # } 

        print(response.usage)
        return response.choices[0].message.parsed


    # def _format_prompt(self, artist: Artist, target_lang: str) -> str:
    #     """Format prompt with artist-specific information and target language"""
    #     return TRANSLATION_PROMPT.format(
    #         artist_name=artist.name,
    #         target_lang=SUPPORTED_LANGUAGES[target_lang],
    #         artist_prompt=artist.prompt.get('prompt', "No specific context available.")
    #     )

    # async def _translate_to_language(self, text: str, artist: Artist, target_lang: str, prev_message: Dict[str, str] = None) -> Dict[str, str]:
    #     """Translate text to a specific language"""
    #     formatted_prompt = self._format_prompt(artist, target_lang)
    #     system_prompt = SYSTEM_PROMPTS['translation']
    #     response = self.client.chat.completions.create(
    #         model="gpt-4o-mini",
    #         response_format={ "type": "json_object" },
    #         messages=[
    #             {"role": "system", "content": system_prompt},
    #             {"role": "user", "content": (
    #                 f"Translation prompt:\n{formatted_prompt}\n\n"
    #                 f"Previous messages:\n{json.dumps(prev_message, ensure_ascii=False)}\n\n" if prev_message else ""
    #                 f"Text to translate:\n{text}"
    #             )}
    #         ]
    #     )
        
    #     result = json.loads(response.choices[0].message.content)
    #     return result

    # @retry(stop=stop_after_attempt(1), wait=wait_exponential(multiplier=1, min=4, max=10))
    # async def translate(self, text: str, artist: Artist, db: Session) -> TranslationResponse:
    #     """Translate text to all supported languages"""
    #     translations = {}
    #     metadata = None
    #     needs_context = False
    #     n_required_context = None

    #     for lang in SUPPORTED_LANGUAGES.keys():
    #         result = await self._translate_to_language(text, artist, lang)
    #         translations[lang] = result['translations']['target']
            
    #         # Use metadata from first translation
    #         if metadata is None:
    #             metadata = result.get('metadata', {})
    #             needs_context = result.get('needs_context', False)
    #             n_required_context = result.get('n_required_context')

    #     # Convert metadata values to strings
    #     if metadata:
    #         metadata = {k: str(v) for k, v in metadata.items()}

    #     return TranslationResponse(
    #         translations=translations,
    #         needs_context=needs_context,
    #         n_required_context=n_required_context,
    #         metadata=metadata
    #     )

    # async def translate_with_context(self, context: TranslationContext, artist: Artist) -> TranslationResponse:
    #     """Translate with context to all supported languages"""
    #     translations = {}
    #     metadata = None

    #     for lang in SUPPORTED_LANGUAGES.keys():
    #         result = await self._translate_to_language(context.current_message, artist, lang, context.messages)
    #         translations[lang] = result['translations']['target']
            
    #         # Use metadata from first translation
    #         if metadata is None:
    #             metadata = result.get('metadata', {})

    #     # Convert metadata values to strings
    #     if metadata:
    #         metadata = {k: str(v) for k, v in metadata.items()}

    #     return TranslationResponse(
    #         translations=translations,
    #         needs_context=False,  # Context already provided
    #         metadata=metadata
    #     )

    # async def safety_check(self, translations: Dict[str, str], artist: Artist) -> Dict[str, bool]:
    #     """Check translations for safety and appropriateness"""
    #     try:
    #         system_prompt = SYSTEM_PROMPTS['safety_check']
            
    #         response = self.client.chat.completions.create(
    #             model="gpt-4o-mini",
    #             response_format={ "type": "json_object" },
    #             messages=[
    #                 {"role": "system", "content": system_prompt},
    #                 {"role": "user", "content": (
    #                     f"Artist: {artist.name}\n"
    #                     f"Check these translations:\n{json.dumps(translations, ensure_ascii=False)}"
    #                 )}
    #             ]
    #         )
            
    #         result = json.loads(response.choices[0].message.content)
    #         return {lang: result['safety_status'] for lang in translations.keys()}
            
    #     except Exception as e:
    #         raise Exception(f"Safety check failed: {str(e)}")

    # async def get_context_messages(self, message: Message, db: Session, n_required: int) -> List[Dict[str, str]]:
    #     """Retrieve context messages for a given message"""
    #     stmt = select(Message).join(MessageContext).where(
    #         MessageContext.context_group == message.contexts[0].context_group,
    #         Message.id != message.id
    #     ).order_by(Message.context_order)
        
    #     context_messages = db.execute(stmt).scalars().all()
        
    #     return [
    #         {
    #             "role": "user" if i % 2 == 0 else "assistant",
    #             "content": msg.message_orig if i % 2 == 0 else f"ENG: {msg.message_eng}\nZH-TW: {msg.message_zh_tw}"
    #         }
    #         for i, msg in enumerate(context_messages[-n_required:])
    #     ]
