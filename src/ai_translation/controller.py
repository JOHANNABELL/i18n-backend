"""
FastAPI Controller for AI Translation endpoints

Exposes REST API for:
- Translating files automatically
- Managing translation jobs
- Reviewing and approving translations
- Exporting translated content
"""

import logging
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from .translator import AITranslator, GroqTranslationProvider, AnthropicTranslationProvider, AIModel
from .service import AITranslationService, TranslationJobStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ai-translation", tags=["AI Translation"])


# ==================== Pydantic Models ====================

class TranslateFileRequest(BaseModel):
    """Request to translate an entire file"""
    target_language_code: str = Field(..., min_length=2, max_length=10, description="e.g. 'fr', 'es'")
    target_language_name: str = Field(..., min_length=1, max_length=100, description="e.g. 'French'")
    auto_approve: bool = Field(False, description="Auto-approve translations above confidence threshold")
    confidence_threshold: float = Field(0.85, ge=0.0, le=1.0, description="Minimum confidence for auto-approval")
    ai_model: str = Field("llama-3.1-70b", description="AI model to use")


class TranslateSingleMessageRequest(BaseModel):
    """Request to translate a single message"""
    key: str = Field(..., description="Message key")
    source_value: str = Field(..., min_length=1, description="Text to translate")
    source_language: str = Field(..., min_length=2, max_length=10)
    target_language: str = Field(..., min_length=2, max_length=10)
    context: Optional[str] = Field(None, description="Additional context for translation")
    auto_approve: bool = Field(False)


class ApproveTranslationsRequest(BaseModel):
    """Request to approve/reject translations"""
    updates: List[dict] = Field(..., description="List of {key, status, review_note}")


class BulkImportRequest(BaseModel):
    """Request to bulk import translations"""
    translations: dict = Field(..., description="Dict of {key: translated_value}")
    source: str = Field("manual", description="Source of import")


class TranslationFileResponse(BaseModel):
    """Response model for translation file"""
    id: str
    project_id: str
    language_code: str
    language_name: str
    created_by: str
    created_at: datetime
    messages_count: int
    approved_count: int
    pending_count: int


# ==================== Endpoints ====================

@router.post("/files/{file_id}/translate")
async def translate_file(
    file_id: str,
    request: TranslateFileRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(lambda: "user_id")  # Replace with actual auth
):
    """
    Translate an entire translation file to a target language using AI.
    
    Process:
    1. Create a translation job
    2. Read source file
    3. Translate all messages in parallel
    4. Create new translation file
    5. Auto-approve if confidence is high
    
    Args:
        file_id: UUID of source translation file
        request: Translation request parameters
        current_user: Current authenticated user
    
    Returns:
        TranslationFileResponse with created file details
    """
    
    try:
        # Initialize AI provider (in real app, use dependency injection)
        if request.ai_model.startswith("llama") or request.ai_model.startswith("mixtral"):
            provider = GroqTranslationProvider(
                api_key="your-groq-api-key",
                model=request.ai_model
            )
        else:
            provider = AnthropicTranslationProvider(
                api_key="your-anthropic-api-key"
            )
        
        translator = AITranslator(
            mongodb_url="mongodb://localhost:27017",
            ai_provider=provider,
            ai_model=AIModel.LLAMA_3_1
        )
        
        # Create translation job for async tracking
        service = AITranslationService(mongodb_url="mongodb://localhost:27017")
        
        # Get project_id from source file
        source_file = translator.get_translation_file(file_id)
        if not source_file:
            raise HTTPException(status_code=404, detail="Source file not found")
        
        project_id = source_file["project_id"]
        
        job = service.create_translation_job(
            project_id=project_id,
            source_file_id=file_id,
            target_language_code=request.target_language_code,
            target_language_name=request.target_language_name,
            translator_user_id=current_user,
            auto_approve=request.auto_approve,
            priority="normal"
        )
        
        # Start translation in background
        background_tasks.add_task(
            _translate_file_background,
            translator=translator,
            service=service,
            job_id=job["id"],
            file_id=file_id,
            target_language_code=request.target_language_code,
            target_language_name=request.target_language_name,
            auto_approve=request.auto_approve,
            confidence_threshold=request.confidence_threshold,
            user_id=current_user
        )
        
        return {
            "job_id": job["id"],
            "status": "PENDING",
            "message": "Translation job created. Processing in background..."
        }
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/messages/translate")
async def translate_single_message(
    file_id: str,
    request: TranslateSingleMessageRequest,
    current_user: str = Depends(lambda: "user_id")
):
    """
    Translate a single message within a file.
    
    Args:
        file_id: UUID of translation file
        request: Single message translation request
        current_user: Current authenticated user
    
    Returns:
        Translated message with confidence score
    """
    
    try:
        provider = GroqTranslationProvider(api_key="your-groq-api-key")
        translator = AITranslator(
            mongodb_url="mongodb://localhost:27017",
            ai_provider=provider
        )
        
        result = await translator.translate_message(
            file_id=file_id,
            key=request.key,
            source_value=request.source_value,
            source_language=request.source_language,
            target_language=request.target_language,
            translator_user_id=current_user,
            context=request.context,
            auto_approve=request.auto_approve
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        logger.error(f"Message translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{job_id}")
async def get_translation_job(job_id: str):
    """Get translation job status and progress"""
    
    service = AITranslationService(mongodb_url="mongodb://localhost:27017")
    job = service.get_translation_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job


@router.get("/files/{file_id}/jobs")
async def list_translation_jobs(
    file_id: str,
    status: Optional[str] = None,
    limit: int = 20
):
    """List all translation jobs for a file"""
    
    service = AITranslationService(mongodb_url="mongodb://localhost:27017")
    
    # Extract project_id from file
    translator = AITranslator(
        mongodb_url="mongodb://localhost:27017",
        ai_provider=None
    )
    
    file = translator.get_translation_file(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    project_id = file["project_id"]
    
    jobs = service.list_translation_jobs(
        project_id=project_id,
        status=TranslationJobStatus(status) if status else None,
        limit=limit
    )
    
    return jobs


@router.post("/files/{file_id}/approve")
async def approve_translations(
    file_id: str,
    request: ApproveTranslationsRequest,
    current_user: str = Depends(lambda: "user_id")
):
    """
    Approve or reject multiple translations at once.
    
    Args:
        file_id: UUID of translation file
        request: List of updates with status changes
        current_user: Current authenticated user (reviewer)
    
    Returns:
        Count of updated messages
    """
    
    try:
        service = AITranslationService(mongodb_url="mongodb://localhost:27017")
        
        result = service.bulk_update_statuses(
            file_id=file_id,
            updates=request.updates,
            reviewer_user_id=current_user
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Approval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{file_id}/stats")
async def get_translation_stats(file_id: str):
    """Get translation statistics for a file"""
    
    service = AITranslationService(mongodb_url="mongodb://localhost:27017")
    stats = service.get_translation_stats(file_id)
    
    if not stats:
        raise HTTPException(status_code=404, detail="File not found")
    
    return stats


@router.get("/files/{file_id}/export")
async def export_translation_file(
    file_id: str,
    flatten: bool = True
):
    """
    Export translation file as JSON.
    
    Args:
        file_id: UUID of translation file
        flatten: If True, return flat key-value pairs; if False, include metadata
    
    Returns:
        JSON representation of translations
    """
    
    service = AITranslationService(mongodb_url="mongodb://localhost:27017")
    
    translations = service.export_file_as_json(file_id, flatten=flatten)
    
    if not translations:
        raise HTTPException(status_code=404, detail="File not found")
    
    return translations


@router.post("/files/{file_id}/import")
async def import_translations(
    file_id: str,
    request: BulkImportRequest,
    current_user: str = Depends(lambda: "user_id")
):
    """
    Import translations from external source (CSV, external API, etc).
    
    Args:
        file_id: UUID of translation file
        request: Translations to import
        current_user: Current authenticated user
    
    Returns:
        Count of imported/updated translations
    """
    
    try:
        service = AITranslationService(mongodb_url="mongodb://localhost:27017")
        
        result = service.import_translations(
            file_id=file_id,
            translations=request.translations,
            translator_user_id=current_user,
            source=request.source
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Import error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{file_id}/messages")
async def get_messages_by_status(
    file_id: str,
    status: str,
    limit: int = 50
):
    """
    Get messages filtered by status.
    
    Args:
        file_id: UUID of translation file
        status: Status filter ("APPROVED", "PENDING", "IN_REVIEW", "REJECTED")
        limit: Maximum results
    
    Returns:
        List of filtered messages
    """
    
    service = AITranslationService(mongodb_url="mongodb://localhost:27017")
    
    messages = service.get_messages_by_status(file_id, status, limit)
    
    return messages


# ==================== Background Tasks ====================

async def _translate_file_background(
    translator: AITranslator,
    service: AITranslationService,
    job_id: str,
    file_id: str,
    target_language_code: str,
    target_language_name: str,
    auto_approve: bool,
    confidence_threshold: float,
    user_id: str
):
    """Background task to translate file"""
    
    try:
        service.update_job_status(job_id, TranslationJobStatus.IN_PROGRESS)
        
        result = await translator.translate_file(
            source_file_id=file_id,
            target_language_code=target_language_code,
            target_language_name=target_language_name,
            translator_user_id=user_id,
            auto_approve=auto_approve,
            confidence_threshold=confidence_threshold
        )
        
        if result.get("success"):
            service.update_job_status(
                job_id,
                TranslationJobStatus.COMPLETED,
                result=result
            )
        else:
            service.update_job_status(
                job_id,
                TranslationJobStatus.FAILED,
                error=result.get("error")
            )
        
    except Exception as e:
        logger.error(f"Background translation failed: {e}")
        service.update_job_status(
            job_id,
            TranslationJobStatus.FAILED,
            error=str(e)
        )
    
    finally:
        translator.close()
