"""Settings management for Tech Docs Explorer.

This module handles loading and validating configuration from:
- Environment variables (.env file)
- YAML configuration file (config.yaml)
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv


class Settings:
    """Singleton class for application settings.

    Loads configuration from .env and config.yaml files and provides
    easy access to all application settings with validation.
    """

    _instance: Optional["Settings"] = None
    _initialized: bool = False

    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize settings (only once due to singleton pattern)."""
        if not Settings._initialized:
            self._load_settings()
            self._validate_settings()
            Settings._initialized = True

    def _load_settings(self):
        """Load settings from .env and config.yaml files."""
        # Load environment variables from .env file
        env_path = Path(__file__).parent.parent / ".env"
        load_dotenv(dotenv_path=env_path)

        # Load YAML configuration
        config_path = Path(__file__).parent / "config.yaml"
        try:
            with open(config_path, "r") as f:
                self._config: Dict[str, Any] = yaml.safe_load(f) or {}
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}\n"
                "Please ensure config.yaml exists in the config directory."
            )

        # Environment variables
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        self.rerank_model = os.getenv("RERANK_MODEL", "gpt-4o-mini")
        self.chroma_persist_dir = os.getenv("CHROMA_PERSIST_DIR", ".data/chroma")

    def _validate_settings(self):
        """Validate required settings are present."""
        if not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required. Please set it in your .env file.\n"
                "Copy .env.example to .env and add your API key."
            )

    # App settings
    @property
    def app_name(self) -> str:
        """Get application name."""
        return self._config.get("app", {}).get("name", "Tech Docs Explorer")

    @property
    def debug(self) -> bool:
        """Get debug mode setting."""
        return self._config.get("app", {}).get("debug", False)

    # Indexing settings
    @property
    def chunk_size(self) -> int:
        """Get chunk size for text splitting."""
        return self._config.get("indexing", {}).get("chunk_size", 1000)

    @property
    def chunk_overlap(self) -> int:
        """Get chunk overlap for text splitting."""
        return self._config.get("indexing", {}).get("chunk_overlap", 200)

    # RAG settings
    @property
    def default_top_k(self) -> int:
        """Get default top_k for retrieval."""
        return self._config.get("rag", {}).get("default_top_k", 5)

    @property
    def default_threshold(self) -> float:
        """Get default similarity threshold."""
        return self._config.get("rag", {}).get("default_threshold", 0.7)

    @property
    def hyde_enabled(self) -> bool:
        """Get HyDE default enabled state."""
        return self._config.get("rag", {}).get("hyde_enabled", False)

    @property
    def reranking_enabled(self) -> bool:
        """Get reranking default enabled state."""
        return self._config.get("rag", {}).get("reranking_enabled", False)

    # LLM settings
    @property
    def llm_provider(self) -> str:
        """Get LLM provider name."""
        return self._config.get("llm", {}).get("provider", "openai")

    # Pricing settings
    @property
    def llm_pricing(self) -> Dict[str, Any]:
        """Get LLM model pricing configuration."""
        return self._config.get("pricing", {}).get("llm_model", {})

    @property
    def embedding_pricing(self) -> Dict[str, Any]:
        """Get embedding model pricing configuration."""
        return self._config.get("pricing", {}).get("embedding_model", {})

    @property
    def rerank_pricing(self) -> Dict[str, Any]:
        """Get rerank model pricing configuration."""
        return self._config.get("pricing", {}).get("rerank_model", {})

    def get_chroma_path(self) -> Path:
        """Get ChromaDB persistence directory path."""
        path = Path(__file__).parent.parent / self.chroma_persist_dir
        path.mkdir(parents=True, exist_ok=True)
        return path


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance.

    Returns:
        Settings: The singleton settings instance.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
