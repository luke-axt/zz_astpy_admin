import os
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    port: int = 8000
    host: str = "0.0.0.0"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_prefix = ""
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


@lru_cache
def get_yaml_config() -> dict:
    if not CONFIG_PATH.exists():
        return {"models": {}, "team_keys": {}}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def resolve_model(alias: str) -> str:
    models = get_yaml_config().get("models", {})
    return models.get(alias, alias)


def get_team_key_info(key: str) -> dict | None:
    team_keys = get_yaml_config().get("team_keys", {})
    return team_keys.get(key)
