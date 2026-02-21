from pydantic import BaseModel, Field
from pathlib import Path
from typing import List
import yaml

DEFAULT_CONFIG = Path(__file__).parent / "config.yml"


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
    config_path = Path(path) if path else DEFAULT_CONFIG
    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)
    return Config(**raw)
