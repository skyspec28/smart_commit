from pydantic import BaseModel, Field
from typing import List, Dict
import yaml
import os

class AIConfig(BaseModel):
    model: str = "gemini-2.5-flash"
    temperature: float = Field(ge=0.0, le=1.0, default=0.7)
    max_tokens: int = Field(gt=0, default=100)
    rules: List[str] = []

class CommitConfig(BaseModel):
    auto_emoji: bool = True
    validate_conventional: bool = True
    preview_diff: bool = True
    interactive_mode: bool = True
    allowed_types: List[str] = ['feat', 'fix', 'docs', 'style', 'refactor']

class GitConfig(BaseModel):
    branch_reference: bool = True
    similar_commits: int = Field(ge=0, default=3)

class Config(BaseModel):
    ai: AIConfig
    commit: CommitConfig
    git: GitConfig


def load_config(path: str = None) -> Config:
    # List of possible config file locations in order of preference
    config_paths = [
        path,  # User-specified path (if provided)
        "smart_commit/config.yml",  # Local project path
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "smart_commit/config.yml"),  # Package directory
        "/usr/local/etc/smart-commit/config.yml",  # Global system path
    ]

    # Filter out None values
    config_paths = [p for p in config_paths if p]

    # Try each path in order
    for config_path in config_paths:
        try:
            with open(config_path, "r") as file:
                raw = yaml.safe_load(file)
                return Config(**raw)
        except (FileNotFoundError, IOError):
            continue

    # If we get here, no config file was found
    raise FileNotFoundError(f"Could not find config file. Tried: {', '.join(config_paths)}")
