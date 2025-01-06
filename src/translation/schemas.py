from pydantic import BaseModel, Field
from typing import Optional, Dict, List

class TranslationResponse(BaseModel):
    translations: Dict[str, str]
    needs_context: bool = Field(default=False)
    n_required_context: Optional[int] = Field(default=None)
    safety_check: Dict[str, bool] = Field(default_factory=dict)
    metadata: Dict[str, str] = Field(default_factory=dict)

class TranslationContext(BaseModel):
    messages: List[Dict[str, str]]
    current_message: str
