"""
Exporteurs de contenu JSONB vers différents formats
Supporte: JSONB, YAML, JSON, Properties, ARB, Strings
"""

import json
import yaml
import logging
from typing import Dict, Any
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class BaseExporter:
    """Classe de base pour les exporteurs"""

    def __init__(self, file_name: str, language: str, language_code: str):
        """
        Initialise l'exporteur.
        
        Args:
            file_name: Nom du fichier de traduction
            language: Nom complet de la langue (e.g., "French")
            language_code: Code langue (e.g., "fr")
        """
        self.file_name = file_name
        self.language = language
        self.language_code = language_code
        self.metadata = {
            "file_name": file_name,
            "language": language,
            "language_code": language_code,
            "exported_at": datetime.now(timezone.utc).isoformat()
        }

    def export(self, content: Dict[str, Any]) -> str:
        """Exporte le contenu. À implémenter par les sous-classes."""
        raise NotImplementedError


class JSONBExporter(BaseExporter):
    """Exporte au format JSONB avec métadonnées"""

    def export(self, content: Dict[str, Any], include_metadata: bool = True) -> str:
        """
        Exporte en JSONB.
        
        Args:
            content: Contenu à exporter
            include_metadata: Inclure les métadonnées
            
        Returns:
            Contenu en format JSONB
        """
        export_data = {
            "metadata": self.metadata,
            "content": content
        } if include_metadata else content
        
        logger.info(f"Exporting to JSONB: {self.file_name}_{self.language_code}.jsonb")
        return json.dumps(export_data, ensure_ascii=False, indent=2)

    def get_filename(self) -> str:
        """Retourne le nom du fichier d'export"""
        return f"{self.file_name}_{self.language_code}.jsonb"


class YAMLExporter(BaseExporter):
    """Exporte au format YAML pour configuration"""

    def export(self, content: Dict[str, Any], include_metadata: bool = True) -> str:
        """
        Exporte en YAML.
        
        Args:
            content: Contenu à exporter
            include_metadata: Inclure les métadonnées
            
        Returns:
            Contenu en format YAML
        """
        export_data = {
            "metadata": self.metadata,
            "content": content
        } if include_metadata else content
        
        # Configuration YAML pour éviter les alias
        class NoAliasDumper(yaml.SafeDumper):
            def ignore_aliases(self, data):
                return True
        
        yaml_content = yaml.dump(
            export_data, 
            Dumper=NoAliasDumper,
            allow_unicode=True,
            default_flow_style=False
        )
        
        logger.info(f"Exporting to YAML: {self.file_name}_{self.language_code}.yaml")
        return yaml_content

    def get_filename(self) -> str:
        """Retourne le nom du fichier d'export"""
        return f"{self.file_name}_{self.language_code}.yaml"


class JSONExporter(BaseExporter):
    """Exporte au format JSON standard"""

    def export(self, content: Dict[str, Any], include_metadata: bool = True) -> str:
        """
        Exporte en JSON.
        
        Args:
            content: Contenu à exporter
            include_metadata: Inclure les métadonnées
            
        Returns:
            Contenu en format JSON
        """
        export_data = {
            "metadata": self.metadata,
            "content": content
        } if include_metadata else content
        
        logger.info(f"Exporting to JSON: {self.file_name}_{self.language_code}.json")
        return json.dumps(export_data, ensure_ascii=False, indent=2)

    def get_filename(self) -> str:
        """Retourne le nom du fichier d'export"""
        return f"{self.file_name}_{self.language_code}.json"


class PropertiesExporter(BaseExporter):
    """Exporte au format .properties (clé=valeur)"""

    def export(self, content: Dict[str, Any], include_metadata: bool = True) -> str:
        """
        Exporte en format Properties.
        
        Args:
            content: Contenu à exporter
            include_metadata: Inclure les métadonnées
            
        Returns:
            Contenu en format Properties
        """
        lines = []
        
        # Métadonnées
        if include_metadata:
            lines.append(f"# {self.file_name} - {self.language}")
            lines.append(f"# Language Code: {self.language_code}")
            lines.append(f"# Exported: {self.metadata['exported_at']}")
            lines.append("")
        
        # Contenu récursif
        def flatten(data, prefix=""):
            for key, value in data.items():
                full_key = f"{prefix}.{key}" if prefix else key
                
                if isinstance(value, dict):
                    flatten(value, full_key)
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            flatten(item, f"{full_key}[{i}]")
                        else:
                            lines.append(f"{full_key}[{i}]={item}")
                elif isinstance(value, str):
                    # Échappe les caractères spéciaux
                    escaped_value = value.replace("\\", "\\\\").replace("\n", "\\n").replace("\r", "\\r")
                    lines.append(f"{full_key}={escaped_value}")
                else:
                    lines.append(f"{full_key}={value}")
        
        flatten(content)
        
        logger.info(f"Exporting to Properties: {self.file_name}_{self.language_code}.properties")
        return "\n".join(lines)

    def get_filename(self) -> str:
        """Retourne le nom du fichier d'export"""
        return f"{self.file_name}_{self.language_code}.properties"


class ARBExporter(BaseExporter):
    """Exporte au format ARB (Application Resource Bundle)"""

    def export(self, content: Dict[str, Any], include_metadata: bool = True) -> str:
        """
        Exporte en format ARB.
        
        Args:
            content: Contenu à exporter
            include_metadata: Inclure les métadonnées
            
        Returns:
            Contenu en format ARB
        """
        arb_data = {}
        
        # Métadonnées ARB standard
        if include_metadata:
            arb_data["@@locale"] = self.language_code
            arb_data["@@context"] = f"{self.file_name} - {self.language}"

        # Contenu
        def flatten(data, prefix=""):
            for key, value in data.items():
                full_key = f"{prefix}_{key}" if prefix else key
                
                if isinstance(value, dict):
                    flatten(value, full_key)
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, str):
                            arb_data[f"{full_key}_{i}"] = item
                elif isinstance(value, str):
                    arb_data[full_key] = value
        
        flatten(content)
        
        logger.info(f"Exporting to ARB: {self.file_name}_{self.language_code}.arb")
        return json.dumps(arb_data, ensure_ascii=False, indent=2)

    def get_filename(self) -> str:
        """Retourne le nom du fichier d'export"""
        return f"{self.file_name}_{self.language_code}.arb"


class StringsExporter(BaseExporter):
    """Exporte au format Strings (pour iOS/macOS)"""

    def export(self, content: Dict[str, Any], include_metadata: bool = True) -> str:
        """
        Exporte au format Strings.
        
        Args:
            content: Contenu à exporter
            include_metadata: Inclure les métadonnées
            
        Returns:
            Contenu en format Strings
        """
        lines = []
        
        if include_metadata:
            lines.append(f"/* {self.file_name} - {self.language} */")
            lines.append(f"/* Language Code: {self.language_code} */")
            lines.append(f"/* Exported: {self.metadata['exported_at']} */")
            lines.append("")
        
        def flatten(data, prefix=""):
            for key, value in data.items():
                full_key = f"{prefix}_{key}" if prefix else key
                
                if isinstance(value, dict):
                    flatten(value, full_key)
                elif isinstance(value, str):
                    # Format Strings : "key" = "value";
                    escaped_value = value.replace('"', '\\"').replace("\n", "\\n")
                    lines.append(f'"{full_key}" = "{escaped_value}";')
        
        flatten(content)
        
        logger.info(f"Exporting to Strings: {self.file_name}_{self.language_code}.strings")
        return "\n".join(lines)

    def get_filename(self) -> str:
        """Retourne le nom du fichier d'export"""
        return f"{self.file_name}_{self.language_code}.strings"


class ExporterFactory:
    """Factory pour créer les exporteurs appropriés"""

    EXPORTERS = {
        "jsonb": JSONBExporter,
        "yaml": YAMLExporter,
        "json": JSONExporter,
        "properties": PropertiesExporter,
        "arb": ARBExporter,
        "strings": StringsExporter,
    }

    @classmethod
    def create_exporter(cls, format_type: str, file_name: str, language: str, language_code: str) -> BaseExporter:
        """
        Crée un exporteur du type spécifié.
        
        Args:
            format_type: Type de format ("jsonb", "yaml", "json", "properties", "arb", "strings")
            file_name: Nom du fichier
            language: Nom de la langue
            language_code: Code langue
            
        Returns:
            Instance de l'exporteur
        """
        if format_type.lower() not in cls.EXPORTERS:
            raise ValueError(f"Unknown export format: {format_type}. Available: {list(cls.EXPORTERS.keys())}")
        
        exporter_class = cls.EXPORTERS[format_type.lower()]
        return exporter_class(file_name, language, language_code)

    @classmethod
    def export(cls, format_type: str, content: Dict[str, Any], file_name: str, 
               language: str, language_code: str, include_metadata: bool = True) -> Tuple[str, str]:
        """
        Exporte directement le contenu.
        
        Args:
            format_type: Type de format
            content: Contenu à exporter
            file_name: Nom du fichier
            language: Nom de la langue
            language_code: Code langue
            include_metadata: Inclure les métadonnées
            
        Returns:
            (contenu_exporté, nom_fichier)
        """
        exporter = cls.create_exporter(format_type, file_name, language, language_code)
        exported_content = exporter.export(content, include_metadata)
        filename = exporter.get_filename()
        
        logger.info(f"Exported {file_name} to {format_type}: {filename}")
        return exported_content, filename


from typing import Tuple
