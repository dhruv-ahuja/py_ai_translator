from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from decorators import singleton


class LogfireSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LOGFIRE_")

    token: SecretStr | None = Field(None)
    enable: bool = Field(True)

    @model_validator(mode="after")
    def validate_state(self) -> "LogfireSettings":
        if self.enable and self.token is None:
            raise ValueError("Logfire token can't be empty if the service is enabled")
        return self


class OpenRouterSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OPENROUTER_")

    api_key: SecretStr = Field(...)
    base_url: str = Field("https://openrouter.ai/api/v1")


@singleton
class Settings(BaseSettings):
    logfire: LogfireSettings = LogfireSettings()
    open_router: OpenRouterSettings = OpenRouterSettings()


settings = Settings()
