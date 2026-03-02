"""
AI Translation Service Layer

Provides high-level operations for translation management,
integrating with the core translator module.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
from enum import Enum

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

logger = logging.getLogger(__name__)


class TranslationJobStatus(Enum):
    """Status of translation jobs"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AITranslationService:
    """Service layer for AI translation operations"""
    
    def __init__(self, mongodb_url: str, db_name: str = "i18n_db"):
        self.client = MongoClient(mongodb_url)
        self.db = self.client[db_name]
    
    def create_translation_job(
        self,
        project_id: str,
        source_file_id: str,
        target_language_code: str,
        target_language_name: str,
        translator_user_id: str,
        auto_approve: bool = False,
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """
        Create a translation job for async processing.
        
        Args:
            project_id: UUID of the project
            source_file_id: UUID of source translation file
            target_language_code: Target language code (e.g., "fr")
            target_language_name: Target language name (e.g., "French")
            translator_user_id: UUID of translator user
            auto_approve: Auto-approve translations above threshold
            priority: Job priority ("low", "normal", "high")
        
        Returns:
            Translation job document
        """
        
        job_id = str(uuid.uuid4())
        
        job = {
            "id": job_id,
            "project_id": project_id,
            "source_file_id": source_file_id,
            "target_language_code": target_language_code,
            "target_language_name": target_language_name,
            "translator_user_id": translator_user_id,
            "status": TranslationJobStatus.PENDING.value,
            "priority": priority,
            "auto_approve": auto_approve,
            "progress": {
                "total_messages": 0,
                "translated_messages": 0,
                "approved_messages": 0,
                "failed_messages": 0
            },
            "result": None,
            "error": None,
            "created_at": datetime.now(timezone.utc),
            "started_at": None,
            "completed_at": None
        }
        
        self.db.translation_jobs.insert_one(job)
        logger.info(f"Created translation job: {job_id}")
        
        return job
    
    def get_translation_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get translation job by ID"""
        return self.db.translation_jobs.find_one({"id": job_id})
    
    def update_job_status(
        self,
        job_id: str,
        status: TranslationJobStatus,
        progress: Optional[Dict[str, int]] = None,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update translation job status"""
        
        update_doc = {"status": status.value}
        
        if status == TranslationJobStatus.IN_PROGRESS:
            update_doc["started_at"] = datetime.now(timezone.utc)
        
        if status == TranslationJobStatus.COMPLETED:
            update_doc["completed_at"] = datetime.now(timezone.utc)
        
        if progress:
            update_doc["progress"] = progress
        
        if result:
            update_doc["result"] = result
        
        if error:
            update_doc["error"] = error
        
        return self.db.translation_jobs.find_one_and_update(
            {"id": job_id},
            {"$set": update_doc},
            return_document=True
        )
    
    def list_translation_jobs(
        self,
        project_id: str,
        status: Optional[TranslationJobStatus] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """List translation jobs for a project"""
        
        query = {"project_id": project_id}
        
        if status:
            query["status"] = status.value
        
        return list(
            self.db.translation_jobs.find(query)
            .sort("created_at", -1)
            .limit(limit)
        )
    
    def get_translation_stats(self, file_id: str) -> Dict[str, Any]:
        """Get translation statistics for a file"""
        
        file = self.db.translation_files.find_one({"id": file_id})
        
        if not file:
            return {}
        
        messages = file.get("messages", {})
        
        stats = {
            "file_id": file_id,
            "language_code": file.get("language_code"),
            "total_keys": len(messages),
            "by_status": {
                "approved": 0,
                "pending": 0,
                "in_review": 0,
                "rejected": 0
            },
            "by_ai": {
                "ai_translated": 0,
                "manual": 0
            },
            "confidence": {
                "average": 0.0,
                "min": 1.0,
                "max": 0.0
            }
        }
        
        confidences = []
        
        for key, message in messages.items():
            status = message.get("status", "PENDING").upper()
            stats["by_status"][status.lower()] = stats["by_status"].get(status.lower(), 0) + 1
            
            metadata = message.get("metadata", {})
            if metadata.get("ai_translated"):
                stats["by_ai"]["ai_translated"] += 1
                confidence = metadata.get("ai_confidence", 0.0)
                confidences.append(confidence)
                stats["confidence"]["min"] = min(stats["confidence"]["min"], confidence)
                stats["confidence"]["max"] = max(stats["confidence"]["max"], confidence)
            else:
                stats["by_ai"]["manual"] += 1
        
        if confidences:
            stats["confidence"]["average"] = sum(confidences) / len(confidences)
        
        return stats
    
    def get_messages_by_status(
        self,
        file_id: str,
        status: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get messages by status from a file"""
        
        file = self.db.translation_files.find_one({"id": file_id})
        
        if not file:
            return []
        
        messages = []
        for key, message in file.get("messages", {}).items():
            if message.get("status") == status:
                messages.append({
                    "key": key,
                    **message
                })
                if len(messages) >= limit:
                    break
        
        return messages
    
    def bulk_update_statuses(
        self,
        file_id: str,
        updates: List[Dict[str, Any]],
        reviewer_user_id: str
    ) -> Dict[str, Any]:
        """
        Bulk update message statuses (approve, reject, etc).
        
        Args:
            file_id: UUID of translation file
            updates: List of {key, status, review_note}
            reviewer_user_id: UUID of reviewer
        
        Returns:
            Update result with count of updated messages
        """
        
        file = self.db.translation_files.find_one({"id": file_id})
        
        if not file:
            return {"success": False, "error": "File not found"}
        
        messages = file.get("messages", {})
        updated_count = 0
        
        for update in updates:
            key = update.get("key")
            new_status = update.get("status")
            review_note = update.get("review_note")
            
            if key in messages and new_status:
                messages[key]["status"] = new_status
                messages[key]["review_note"] = review_note
                messages[key]["metadata"]["reviewed_by"] = reviewer_user_id
                messages[key]["metadata"]["reviewed_at"] = datetime.now(timezone.utc)
                updated_count += 1
        
        # Update in database
        self.db.translation_files.update_one(
            {"id": file_id},
            {
                "$set": {
                    "messages": messages,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        # Update stats
        self._update_file_stats(file_id)
        
        return {
            "success": True,
            "file_id": file_id,
            "updated_count": updated_count
        }
    
    def export_file_as_json(
        self,
        file_id: str,
        flatten: bool = True
    ) -> Dict[str, Any]:
        """
        Export translation file as JSON.
        
        Args:
            file_id: UUID of translation file
            flatten: If True, flatten nested structure to dotted keys
        
        Returns:
            JSON-serializable dictionary
        """
        
        file = self.db.translation_files.find_one({"id": file_id})
        
        if not file:
            return {}
        
        messages = file.get("messages", {})
        
        if flatten:
            # Return flat structure
            result = {}
            for key, message in messages.items():
                result[key] = message.get("value")
            return result
        else:
            # Return full message objects
            return messages
    
    def import_translations(
        self,
        file_id: str,
        translations: Dict[str, str],
        translator_user_id: str,
        source: str = "manual"
    ) -> Dict[str, Any]:
        """
        Import translations from external source.
        
        Args:
            file_id: UUID of translation file
            translations: Dict of key -> translated_value
            translator_user_id: UUID of translator
            source: Source of import ("manual", "api", etc)
        
        Returns:
            Import result with count of updated messages
        """
        
        file = self.db.translation_files.find_one({"id": file_id})
        
        if not file:
            return {"success": False, "error": "File not found"}
        
        messages = file.get("messages", {})
        updated_count = 0
        
        for key, value in translations.items():
            if key in messages:
                messages[key]["value"] = value
                messages[key]["status"] = "PENDING"
                messages[key]["metadata"]["created_by"] = translator_user_id
                messages[key]["metadata"]["ai_translated"] = False
                updated_count += 1
        
        self.db.translation_files.update_one(
            {"id": file_id},
            {
                "$set": {
                    "messages": messages,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        self._update_file_stats(file_id)
        
        return {
            "success": True,
            "file_id": file_id,
            "imported_count": updated_count
        }
    
    def _update_file_stats(self, file_id: str):
        """Update statistics for a translation file"""
        
        file = self.db.translation_files.find_one({"id": file_id})
        
        if not file:
            return
        
        messages = file.get("messages", {})
        
        stats = {
            "total_keys": len(messages),
            "approved": sum(1 for m in messages.values() if m.get("status") == "APPROVED"),
            "pending": sum(1 for m in messages.values() if m.get("status") == "PENDING"),
            "rejected": sum(1 for m in messages.values() if m.get("status") == "REJECTED"),
            "in_review": sum(1 for m in messages.values() if m.get("status") == "IN_REVIEW"),
            "ai_translated": sum(
                1 for m in messages.values() 
                if m.get("metadata", {}).get("ai_translated")
            )
        }
        
        confidences = [
            m.get("metadata", {}).get("ai_confidence", 0.0)
            for m in messages.values()
            if m.get("metadata", {}).get("ai_translated")
        ]
        
        if confidences:
            stats["average_confidence"] = sum(confidences) / len(confidences)
        
        self.db.translation_files.update_one(
            {"id": file_id},
            {"$set": {"stats": stats}}
        )
    
    def close(self):
        """Close database connection"""
        self.client.close()
