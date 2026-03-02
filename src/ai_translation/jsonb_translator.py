"""
Module de traduction JSONB avec M2M100
Gère les traductions de contenu JSONB imbriqué avec protection des variables
"""

import json
import re
import logging
from typing import Dict, Any, Tuple, List
from datetime import datetime, timezone
from .models_m2m100 import TranslationModel
from .quality_assurance import protect_variables, restore_variables, translate_dict

logger = logging.getLogger(__name__)


class JSONBTranslator:
    """Translateur JSONB avec support des structures imbriquées et protection des variables"""

    def __init__(self, source_lang: str = "en", device: str = None):
        """
        Initialise le traducteur JSONB.
        
        Args:
            source_lang: Code langue source ("en", "fr", etc.)
            device: "cuda" ou "cpu" (auto-détection par défaut)
        """
        self.source_lang = source_lang
        self.model = TranslationModel()
        self.device = device or self.model.device
        self.translation_cache = {}
        logger.info(f"JSONBTranslator initialized with source_lang={source_lang}")

    def translate_text_with_protection(self, text: str, target_lang: str) -> str:
        """
        Traduit un texte en protégeant les variables dynamiques.
        
        Args:
            text: Texte à traduire
            target_lang: Code langue cible ("sw", "fr", "es", etc.)
            
        Returns:
            Texte traduit avec variables restaurées
        """
        if not text or not isinstance(text, str):
            return text

        # Étape 1: Protection des variables
        protected_text, placeholders = protect_variables(text)
        
        # Étape 2: Traduction
        try:
            translated_text = self.model.translate_text(
                protected_text, 
                self.source_lang, 
                target_lang
            )
        except Exception as e:
            logger.error(f"Translation error for '{text}': {e}")
            return text

        # Étape 3: Restauration des variables
        restored_text = restore_variables(translated_text, placeholders)
        
        logger.debug(f"Translated: '{text}' -> '{restored_text}'")
        return restored_text

    def translate_jsonb(self, data: Dict[str, Any], target_lang: str) -> Dict[str, Any]:
        """
        Traduit récursivement tout le contenu JSONB.
        
        Args:
            data: Contenu JSONB à traduire
            target_lang: Code langue cible
            
        Returns:
            Contenu JSONB traduit
        """
        def translator_func(text: str) -> str:
            return self.translate_text_with_protection(text, target_lang)
        
        logger.info(f"Starting JSONB translation to {target_lang}")
        return translate_dict(data, translator_func)

    def translate_jsonb_batch(self, data_list: List[Dict[str, Any]], target_lang: str) -> List[Dict[str, Any]]:
        """
        Traduit un lot de fichiers JSONB.
        
        Args:
            data_list: Liste de contenus JSONB
            target_lang: Code langue cible
            
        Returns:
            Liste de contenus traduits
        """
        logger.info(f"Starting batch translation of {len(data_list)} files to {target_lang}")
        return [self.translate_jsonb(data, target_lang) for data in data_list]

    def validate_structure(self, original: Dict[str, Any], translated: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valide que la traduction préserve la structure du JSON.
        
        Args:
            original: Contenu original
            translated: Contenu traduit
            
        Returns:
            (est_valide, liste_des_erreurs)
        """
        errors = []
        
        def check_structure(orig, trans, path=""):
            if type(orig) != type(trans):
                errors.append(f"{path}: Type mismatch {type(orig)} != {type(trans)}")
                return
            
            if isinstance(orig, dict):
                if set(orig.keys()) != set(trans.keys()):
                    missing = set(orig.keys()) - set(trans.keys())
                    extra = set(trans.keys()) - set(orig.keys())
                    if missing:
                        errors.append(f"{path}: Missing keys: {missing}")
                    if extra:
                        errors.append(f"{path}: Extra keys: {extra}")
                
                for key in orig.keys():
                    new_path = f"{path}.{key}" if path else key
                    if key in trans:
                        check_structure(orig[key], trans[key], new_path)
            
            elif isinstance(orig, list):
                if len(orig) != len(trans):
                    errors.append(f"{path}: List length mismatch {len(orig)} != {len(trans)}")
                else:
                    for i, (o, t) in enumerate(zip(orig, trans)):
                        new_path = f"{path}[{i}]"
                        check_structure(o, t, new_path)
        
        check_structure(original, translated)
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info("Structure validation passed")
        else:
            logger.warning(f"Structure validation failed with {len(errors)} errors")
        
        return is_valid, errors

    def get_statistics(self, original: Dict[str, Any], translated: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère des statistiques de traduction.
        
        Args:
            original: Contenu original
            translated: Contenu traduit
            
        Returns:
            Dictionnaire avec statistiques
        """
        def count_strings(data):
            count = 0
            chars = 0
            if isinstance(data, str):
                return 1, len(data)
            elif isinstance(data, dict):
                for v in data.values():
                    c, ch = count_strings(v)
                    count += c
                    chars += ch
            elif isinstance(data, list):
                for item in data:
                    c, ch = count_strings(item)
                    count += c
                    chars += ch
            return count, chars
        
        orig_strings, orig_chars = count_strings(original)
        trans_strings, trans_chars = count_strings(translated)
        
        stats = {
            "original_strings": orig_strings,
            "original_characters": orig_chars,
            "translated_strings": trans_strings,
            "translated_characters": trans_chars,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"Translation stats: {orig_strings} strings, {orig_chars} chars")
        return stats


class TranslationContentManager:
    """Gère le contenu JSONB des fichiers de traduction"""

    def __init__(self, db_session=None):
        """
        Initialise le gestionnaire de contenu.
        
        Args:
            db_session: Session SQLAlchemy pour les opérations DB
        """
        self.db = db_session
        self.jsonb_translator = None

    def initialize_translator(self, source_lang: str = "en"):
        """Initialise le traducteur JSONB"""
        self.jsonb_translator = JSONBTranslator(source_lang=source_lang)

    def parse_jsonb_content(self, content: str) -> Dict[str, Any]:
        """Parse le contenu JSONB"""
        try:
            if isinstance(content, dict):
                return content
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSONB content: {e}")
            raise ValueError(f"Invalid JSONB format: {e}")

    def serialize_jsonb_content(self, data: Dict[str, Any]) -> str:
        """Sérialise le contenu en JSONB"""
        return json.dumps(data, ensure_ascii=False, indent=2)

    def translate_file_content(self, 
                             content: Dict[str, Any], 
                             target_lang: str,
                             file_name: str = "translation",
                             quality_check: bool = True) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Traduit le contenu d'un fichier JSONB.
        
        Args:
            content: Contenu JSONB original
            target_lang: Langue cible
            file_name: Nom du fichier (pour logging)
            quality_check: Effectuer validation de structure
            
        Returns:
            (contenu_traduit, metadata_traduction)
        """
        if not self.jsonb_translator:
            raise RuntimeError("Translator not initialized. Call initialize_translator() first.")
        
        logger.info(f"Translating file '{file_name}' to {target_lang}")
        
        # Traduction
        translated_content = self.jsonb_translator.translate_jsonb(content, target_lang)
        
        # Validation
        metadata = {
            "file_name": file_name,
            "source_lang": self.jsonb_translator.source_lang,
            "target_lang": target_lang,
            "translation_date": datetime.now(timezone.utc).isoformat(),
            "quality_check": {}
        }
        
        if quality_check:
            is_valid, errors = self.jsonb_translator.validate_structure(content, translated_content)
            stats = self.jsonb_translator.get_statistics(content, translated_content)
            
            metadata["quality_check"]["valid"] = is_valid
            metadata["quality_check"]["errors"] = errors
            metadata["quality_check"]["statistics"] = stats
        
        return translated_content, metadata
