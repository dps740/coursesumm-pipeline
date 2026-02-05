"""Configuration for CourseSumm v2."""

import os
from pathlib import Path
from typing import Optional
import yaml


class Config:
    """Configuration management for CourseSumm v2."""
    
    def __init__(self):
        # API Keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        
        # LLM Settings
        self.llm_provider = "openai"  # or "anthropic"
        self.llm_model = "gpt-4"
        self.llm_temperature = 0.7
        self.llm_max_tokens = 2000
        
        # Whisper Settings
        self.whisper_model = "medium"  # tiny, base, small, medium, large
        self.whisper_device = "cpu"  # Will auto-detect GPU
        
        # Output Settings
        self.min_summary_words = 300
        self.max_summary_words = 500
        
        # Paths (will be set per run)
        self.input_folder: Optional[Path] = None
        self.output_folder: Optional[Path] = None
        
    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> 'Config':
        """Load configuration from YAML file."""
        config = cls()
        
        if config_path and config_path.exists():
            with open(config_path) as f:
                data = yaml.safe_load(f)
                if data:
                    for key, value in data.items():
                        if hasattr(config, key):
                            setattr(config, key, value)
        
        return config
    
    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        return {
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "whisper_model": self.whisper_model,
            "min_summary_words": self.min_summary_words,
            "max_summary_words": self.max_summary_words,
        }


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global config instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def set_config(config: Config):
    """Set the global config instance."""
    global _config
    _config = config
