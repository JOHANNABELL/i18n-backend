"""
AI Translation Module

Provides automatic translation of i18n files using AI models
(Groq, Anthropic Claude, OpenAI, etc.)

Main Components:
- translator.py: Core AI translation engine
- service.py: Business logic layer
- controller.py: FastAPI endpoints
- models.py: Pydantic request/response models
"""

from .translator import (
    AITranslator,
    AIModel,
    TranslationProvider,
    GroqTranslationProvider,
    AnthropicTranslationProvider,
    TranslationStatus,
    TranslatedMessage,
)

from .service import (
    AITranslationService,
    TranslationJobStatus,
)

from .controller import router

__all__ = [
    "AITranslator",
    "AIModel",
    "TranslationProvider",
    "GroqTranslationProvider",
    "AnthropicTranslationProvider",
    "TranslationStatus",
    "TranslatedMessage",
    "AITranslationService",
    "TranslationJobStatus",
    "router",
]
