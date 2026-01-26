"""Configuration for CourSumm pipeline."""

from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel
import yaml
import os


class PublicSafetyConfig(BaseModel):
    """Safety thresholds for public output."""
    enabled: bool = True
    max_ngram_overlap: float = 0.02  # 2%
    max_cosine_similarity: float = 0.80
    max_consecutive_words: int = 8
    regeneration_attempts: int = 3


class Config(BaseModel):
    """Main configuration."""
    
    # Paths
    transcripts_dir: Path = Path("./transcripts")
    output_dir: Path = Path("./output")
    intermediate_dir: Path = Path("./intermediate")
    
    # LLM settings
    llm_provider: str = "openai"  # "openai" or "anthropic"
    llm_model: str = "gpt-4o-mini"
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Chunking
    chunk_min_words: int = 300
    chunk_max_words: int = 800
    
    # Topic categories
    topics: List[str] = [
        "truth",
        "knowledge",
        "mind",
        "free_will",
        "god_religion",
        "morality",
        "meaning",
    ]
    
    # Public safety
    public_safety: PublicSafetyConfig = PublicSafetyConfig()
    
    # Output format
    output_format: str = "md"  # "md", "docx", or "both"
    
    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "Config":
        """Load config from YAML file and environment."""
        data = {}
        
        # Try to load from YAML
        if config_path and config_path.exists():
            with open(config_path) as f:
                data = yaml.safe_load(f) or {}
        elif Path("config.yaml").exists():
            with open("config.yaml") as f:
                data = yaml.safe_load(f) or {}
        
        # Override with environment variables
        data["openai_api_key"] = os.environ.get("OPENAI_API_KEY", data.get("openai_api_key"))
        data["anthropic_api_key"] = os.environ.get("ANTHROPIC_API_KEY", data.get("anthropic_api_key"))
        
        return cls(**data)


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get or load the global config."""
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def set_config(config: Config):
    """Set the global config."""
    global _config
    _config = config
