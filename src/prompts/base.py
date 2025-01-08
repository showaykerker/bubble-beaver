from typing import List
from pydantic import BaseModel

SUPPORTED_LANGUAGES = ["English", "#zh-TW"]

class TranslationMetadata(BaseModel):
    confidence: float
    mentioned_artists: List[str]
    cultural_notes: List[str]
    korean_specific_terms: List[str]

class TranslateToLanguage(BaseModel):
    lang: str
    content: str

class TranslationOfSentence(BaseModel):
    uuid: str
    update_previous_translation: bool
    message_orig: str
    translations: List[TranslateToLanguage]
    metadata: TranslationMetadata

class TranslationResponse(BaseModel):
    translations: List[TranslationOfSentence]

class BasePrompt:
    def format(self, **kwargs) -> str:
        raise NotImplementedError


class TranslationPrompt(BasePrompt):
    def __init__(self, template: str):
        self.template = template
    
    def format(self, **kwargs) -> str:
        return self.template.format(**kwargs)

# Single translation prompt for all languages
TRANSLATION_PROMPT = TranslationPrompt(
    "==============================\n\n"
    "You are a skilled translator specializing in Korean idol and celebrity content. "
    "You understand the unique style and expressions of {artist_name}, a Korean artist.\n"
    "You will be given a list of messages from {artist_name} and possibly their fans. \n"
    "Translate the given Korean text within the context to {supported_languages} while:\n"
    "1. Maintaining the artist's personal tone and style\n"
    "2. Preserving Korean honorifics when culturally significant\n"
    "3. Keeping emojis and emoticons where appropriate\n"
    "4. Ensuring the translation is natural in the target language\n\n"
    "==============================\n\n"
    "Artist-specific context: {artist_prompt}\n\n"
    "==============================\n\n"
    "You should return message if the translation is not yet finished, "
    "or if the translation should be updated:\n\n"
    "Your response should provide:\n"
    "- uuid: the given uuid of the message\n"
    "- update_previous_translation [boolean]: whether to update the previous translation, "
        "if current_translation is provided and not good enough\n"
    "- message_orig: the original message\n"
    "- translations: "
    "\t- lang: the language of the translation\n"
    "\t- content: the translation\n"
    "- metadata: the metadata of the translation\n"
    "\t- confidence: the confidence level of the translation\n"
    "\t- mentioned_artists: the artists mentioned in the translation\n"
    "\t- cultural_notes: cultural notes in the translation\n"
    "\t- korean_specific_terms: korean-specific terms in the translation\n\n"
)

SYSTEM_PROMPTS = {
    'translation': (
        "You are a Korean content translation assistant. Respond in JSON format with the following structure:\n"
        "{\n"
        '  "translations": {\n'
        '    "target": "translated text in requested language"\n'
        '  },\n'
        '  "needs_context": boolean,\n'
        '  "n_required_context": optional number,\n'
        '  "metadata": {\n'
        '    "confidence": float between 0 and 1,\n'
        '    "korean_specific_terms": [list of Korean terms preserved],\n'
        '    "cultural_notes": optional string\n'
        '  }\n'
        "}"
    ),
    'context_translation': (
        "You are a Korean content translation assistant. You will receive previous messages as context.\n"
        "Respond in JSON format with translations that maintain:\n"
        "1. Consistent translation of Korean-specific terms\n"
        "2. Proper honorific levels throughout the conversation\n"
        "3. Cultural context and references\n"
        "4. Fan-specific terminology if present"
    ),
    'safety_check': (
        "You are a content safety checker familiar with Korean idol content standards. "
        "Analyze the translation for:\n"
        "1. Appropriate language for idol content\n"
        "2. Correct honorific levels\n"
        "3. Cultural sensitivity\n"
        "4. Platform-appropriate tone\n\n"
        "Respond with a JSON object:\n"
        "{\n"
        '  "safety_status": boolean,\n'
        '  "issues": [\n'
        '    {\n'
        '      "issue": "description",\n'
        '      "severity": "low/medium/high"\n'
        '    }\n'
        '  ]\n'
        "}"
    )
}