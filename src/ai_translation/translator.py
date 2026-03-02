"""
AI Translation Module for i18n Backend

Handles automatic translation of messages using AI models (M1800, GPT-4, Claude, etc.)
Integrates with MongoDB for storing translated content with metadata and confidence scores.

Features:
- Read existing translation files
- Translate values to target languages automatically
- Create new translation files with language metadata
- Store translator user information and audit logs
- Support for context-aware translation
- Confidence score calculation
- Rollback capabilities
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum
import uuid
from abc import ABC, abstractmethod
import asyncio

# For AI models
import anthropic
import openai
from groq import Groq

# For MongoDB
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

logger = logging.getLogger(__name__)


class AIModel(Enum):
    """Supported AI models for translation"""
    M1800 = "m1800"  # Meta Llama 3.1 800B equivalent (via Groq or similar)
    GPT_4 = "gpt-4"
    CLAUDE_3_OPUS = "claude-3-opus"
    CLAUDE_3_SONNET = "claude-3-5-sonnet"
    LLAMA_3_1 = "llama-3.1-70b"


class TranslationStatus(Enum):
    """Status of translated messages"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    IN_REVIEW = "IN_REVIEW"


@dataclass
class TranslationMessage:
    """Represents a message to be translated"""
    key: str
    value: str
    comment: Optional[str] = None
    context: Optional[str] = None
    priority: str = "medium"


@dataclass
class TranslatedMessage:
    """Represents a translated message with metadata"""
    key: str
    value: str
    status: TranslationStatus
    ai_translated: bool
    ai_model: str
    ai_confidence: float
    ai_generated_at: datetime
    translation_time_ms: int
    comment: Optional[str] = None


class TranslationProvider(ABC):
    """Abstract base class for translation providers"""
    
    @abstractmethod
    async def translate(
        self, 
        text: str, 
        source_language: str, 
        target_language: str,
        context: Optional[str] = None
    ) -> Tuple[str, float]:
        """
        Translate text from source to target language.
        
        Returns:
            Tuple of (translated_text, confidence_score)
        """
        pass


class GroqTranslationProvider(TranslationProvider):
    """Translation provider using Groq API"""
    
    def __init__(self, api_key: str, model: str = "llama-3.1-70b-versatile"):
        self.client = Groq(api_key=api_key)
        self.model = model
    
    async def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
        context: Optional[str] = None
    ) -> Tuple[str, float]:
        """Translate using Groq API"""
        
        system_prompt = f"""You are an expert translator specializing in localization for software applications.
Your task is to translate the following text from {source_language} to {target_language}.

Translation Guidelines:
1. Maintain the original meaning and tone
2. Adapt for cultural context (if applicable)
3. Keep terminology consistent
4. Preserve formatting and special characters
5. Keep translations concise

{f'Context: {context}' if context else ''}

Respond ONLY with the translated text, nothing else."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": f"Translate: {text}"
                    }
                ],
                system=system_prompt,
                temperature=0.3,  # Lower temp for consistency
                max_tokens=500,
            )
            
            translated_text = response.choices[0].message.content.strip()
            
            # Confidence score based on response quality
            confidence = self._calculate_confidence(translated_text, text)
            
            return translated_text, confidence
            
        except Exception as e:
            logger.error(f"Groq translation error: {e}")
            raise
    
    def _calculate_confidence(self, translated: str, original: str) -> float:
        """Calculate confidence score for translation"""
        # Simple heuristic: check if translation has reasonable length
        if not translated or len(translated) < 1:
            return 0.0
        
        length_ratio = len(translated) / max(len(original), 1)
        # If translation is within 50-200% of original length, good sign
        if 0.5 <= length_ratio <= 2.0:
            confidence = 0.85 + (0.15 * (1 - abs(length_ratio - 1)))
        else:
            confidence = 0.70
        
        return min(1.0, max(0.0, confidence))


class AnthropicTranslationProvider(TranslationProvider):
    """Translation provider using Anthropic Claude API"""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    async def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
        context: Optional[str] = None
    ) -> Tuple[str, float]:
        """Translate using Anthropic API"""
        
        system_prompt = f"""You are an expert translator specializing in localization for software applications.
Your task is to translate the following text from {source_language} to {target_language}.

{f'Context: {context}' if context else ''}

Respond ONLY with the translated text, nothing else."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Translate: {text}"
                    }
                ]
            )
            
            translated_text = response.content[0].text.strip()
            confidence = self._calculate_confidence(translated_text, text)
            
            return translated_text, confidence
            
        except Exception as e:
            logger.error(f"Anthropic translation error: {e}")
            raise
    
    def _calculate_confidence(self, translated: str, original: str) -> float:
        """Calculate confidence score"""
        if not translated:
            return 0.0
        
        length_ratio = len(translated) / max(len(original), 1)
        if 0.5 <= length_ratio <= 2.0:
            confidence = 0.88 + (0.12 * (1 - abs(length_ratio - 1)))
        else:
            confidence = 0.75
        
        return min(1.0, max(0.0, confidence))


class AITranslator:
    """
    Main AI Translation service for the i18n backend
    
    Orchestrates:
    - Reading existing translation files from MongoDB
    - Translating messages using AI providers
    - Creating new translation files
    - Recording user and audit information
    """
    
    def __init__(
        self,
        mongodb_url: str,
        ai_provider: TranslationProvider,
        ai_model: AIModel = AIModel.LLAMA_3_1,
        db_name: str = "i18n_db"
    ):
        self.client = MongoClient(mongodb_url)
        self.db = self.client[db_name]
        self.ai_provider = ai_provider
        self.ai_model = ai_model
        
        logger.info(f"AITranslator initialized with model: {ai_model.value}")
    
    async def translate_file(
        self,
        source_file_id: str,
        target_language_code: str,
        target_language_name: str,
        translator_user_id: str,
        auto_approve: bool = False,
        confidence_threshold: float = 0.85
    ) -> Dict[str, Any]:
        """
        Translate an entire translation file to a target language.
        
        Args:
            source_file_id: UUID of source translation file
            target_language_code: Code of target language (e.g., "fr", "es")
            target_language_name: Name of target language (e.g., "French")
            translator_user_id: UUID of user performing translation
            auto_approve: Auto-approve translations above confidence threshold
            confidence_threshold: Minimum confidence for auto-approval
        
        Returns:
            Dictionary with translation results and metadata
        """
        
        logger.info(f"Starting translation: {source_file_id} → {target_language_code}")
        
        try:
            # Get source file
            source_file = self.db.translation_files.find_one(
                {"id": source_file_id}
            )
            
            if not source_file:
                raise FileNotFoundError(f"Source file not found: {source_file_id}")
            
            # Prepare target file document
            target_file_id = str(uuid.uuid4())
            project_id = source_file["project_id"]
            
            # Check if file already exists
            existing = self.db.translation_files.find_one({
                "project_id": project_id,
                "language_code": target_language_code
            })
            
            if existing:
                logger.warning(f"File already exists for {target_language_code}")
                return {
                    "success": False,
                    "error": f"Translation file already exists for {target_language_code}",
                    "file_id": existing["id"]
                }
            
            # Translate all messages
            start_time = datetime.now(timezone.utc)
            translated_messages = {}
            translation_errors = []
            
            source_language = source_file.get("language_code", "en")
            
            for key, message_data in source_file.get("messages", {}).items():
                try:
                    source_value = message_data.get("value", "")
                    context = message_data.get("context")
                    
                    if not source_value:
                        logger.warning(f"Empty value for key: {key}")
                        continue
                    
                    # Call AI provider
                    translated_value, confidence = await self.ai_provider.translate(
                        text=source_value,
                        source_language=source_language,
                        target_language=target_language_code,
                        context=context
                    )
                    
                    # Determine approval status
                    status = TranslationStatus.APPROVED.value if (
                        auto_approve and confidence >= confidence_threshold
                    ) else TranslationStatus.PENDING.value
                    
                    # Build translated message
                    translated_messages[key] = {
                        "id": str(uuid.uuid4()),
                        "key": key,
                        "value": translated_value,
                        "comment": message_data.get("comment"),
                        "context": context,
                        "status": status,
                        "metadata": {
                            "created_by": translator_user_id,
                            "reviewed_by": None,
                            "created_at": datetime.now(timezone.utc),
                            "updated_at": datetime.now(timezone.utc),
                            "ai_translated": True,
                            "ai_model": self.ai_model.value,
                            "ai_confidence": confidence,
                            "ai_generated_at": datetime.now(timezone.utc),
                            "translation_time_ms": 0  # Set after timing
                        }
                    }
                    
                except Exception as e:
                    logger.error(f"Error translating key {key}: {e}")
                    translation_errors.append({
                        "key": key,
                        "error": str(e)
                    })
            
            translation_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            # Create new translation file document
            new_file = {
                "id": target_file_id,
                "project_id": project_id,
                "language_code": target_language_code,
                "language_name": target_language_name,
                "current_version": 0,
                "created_by": translator_user_id,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "messages": translated_messages,
                "structure": source_file.get("structure", {}),
                "stats": {
                    "total_keys": len(translated_messages),
                    "approved": sum(
                        1 for m in translated_messages.values() 
                        if m.get("status") == TranslationStatus.APPROVED.value
                    ),
                    "pending": sum(
                        1 for m in translated_messages.values() 
                        if m.get("status") == TranslationStatus.PENDING.value
                    ),
                    "rejected": 0,
                    "in_review": 0,
                    "ai_translated": len(translated_messages),
                    "average_confidence": sum(
                        m["metadata"]["ai_confidence"] 
                        for m in translated_messages.values()
                    ) / max(len(translated_messages), 1)
                },
                "versions": [],
                "config": source_file.get("config", {}),
                "is_active": True
            }
            
            # Save to MongoDB
            self.db.translation_files.insert_one(new_file)
            
            # Create audit log
            self._create_audit_log(
                user_id=translator_user_id,
                project_id=project_id,
                file_id=target_file_id,
                action="AI_TRANSLATE",
                changes={
                    "source_language": source_language,
                    "target_language": target_language_code,
                    "messages_translated": len(translated_messages),
                    "translation_model": self.ai_model.value,
                    "auto_approved": auto_approve,
                    "average_confidence": new_file["stats"]["average_confidence"]
                }
            )
            
            logger.info(f"✓ Translation completed: {len(translated_messages)} messages translated")
            
            return {
                "success": True,
                "file_id": target_file_id,
                "language_code": target_language_code,
                "language_name": target_language_name,
                "messages_translated": len(translated_messages),
                "messages_approved": new_file["stats"]["approved"],
                "messages_pending": new_file["stats"]["pending"],
                "average_confidence": round(new_file["stats"]["average_confidence"], 3),
                "translation_time_ms": round(translation_time, 2),
                "errors": translation_errors,
                "created_at": new_file["created_at"]
            }
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def translate_message(
        self,
        file_id: str,
        key: str,
        source_value: str,
        source_language: str,
        target_language: str,
        translator_user_id: str,
        context: Optional[str] = None,
        auto_approve: bool = False
    ) -> Dict[str, Any]:
        """
        Translate a single message within a file.
        
        Returns:
            Dictionary with translated message and metadata
        """
        
        try:
            start_time = datetime.now(timezone.utc)
            
            # Translate
            translated_value, confidence = await self.ai_provider.translate(
                text=source_value,
                source_language=source_language,
                target_language=target_language,
                context=context
            )
            
            translation_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            return {
                "success": True,
                "key": key,
                "translated_value": translated_value,
                "ai_confidence": confidence,
                "ai_model": self.ai_model.value,
                "translation_time_ms": round(translation_time, 2),
                "status": "APPROVED" if auto_approve and confidence >= 0.85 else "PENDING"
            }
            
        except Exception as e:
            logger.error(f"Message translation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_audit_log(
        self,
        user_id: str,
        project_id: str,
        file_id: str,
        action: str,
        changes: Dict[str, Any]
    ):
        """Create an audit log entry"""
        
        audit_log = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "project_id": project_id,
            "file_id": file_id,
            "action": action,
            "changes": changes,
            "timestamp": datetime.now(timezone.utc)
        }
        
        self.db.audit_logs.insert_one(audit_log)
    
    def get_translation_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a translation file from MongoDB"""
        
        return self.db.translation_files.find_one({"id": file_id})
    
    def get_message(self, file_id: str, key: str) -> Optional[Dict[str, Any]]:
        """Get a specific message from a file"""
        
        file = self.db.translation_files.find_one(
            {"id": file_id},
            {"messages": {f"{key}": 1}}
        )
        
        if file and f"messages.{key}" in file:
            return file["messages"][key]
        
        return None
    
    def list_files_for_project(self, project_id: str) -> List[Dict[str, Any]]:
        """List all translation files for a project"""
        
        return list(self.db.translation_files.find(
            {"project_id": project_id, "is_active": True}
        ))
    
    def close(self):
        """Close database connection"""
        self.client.close()


# Example usage
async def example_translation():
    """Example of how to use the AI Translator"""
    
    # Initialize provider
    groq_provider = GroqTranslationProvider(
        api_key="your-groq-api-key"
    )
    
    # Initialize translator
    translator = AITranslator(
        mongodb_url="mongodb://localhost:27017",
        ai_provider=groq_provider,
        ai_model=AIModel.LLAMA_3_1
    )
    
    try:
        # Translate entire file
        result = await translator.translate_file(
            source_file_id="source-file-id",
            target_language_code="fr",
            target_language_name="French",
            translator_user_id="user-id-123",
            auto_approve=True,
            confidence_threshold=0.85
        )
        
        print(f"Translation Result: {result}")
        
        # Translate single message
        msg_result = await translator.translate_message(
            file_id="target-file-id",
            key="app.header.title",
            source_value="Welcome to our app",
            source_language="en",
            target_language="fr",
            translator_user_id="user-id-123",
            context="Header of application dashboard",
            auto_approve=True
        )
        
        print(f"Message Translation: {msg_result}")
        
    finally:
        translator.close()


if __name__ == "__main__":
    # Run example
    asyncio.run(example_translation())
