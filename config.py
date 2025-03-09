from pathlib import Path

from pydantic import Field, SecretStr, field_validator, model_validator
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


class GeneralSettings(BaseSettings):
    # default to current directory to output any data to write
    output_folder: str = Field(".")

    @field_validator("output_folder")
    @classmethod
    def validate_path(cls, value: str) -> str:
        try:
            path = Path(value)
        except Exception as ex:
            print(f"error parsing output file path: {ex}")
            raise ValueError("Invalid output file path given.")

        if path.exists() and path.is_file():
            raise ValueError("Invalid output file path given. Path can't be a file.")

        return str(path.absolute())


@singleton
class Settings(BaseSettings):
    logfire: LogfireSettings = LogfireSettings()
    open_router: OpenRouterSettings = OpenRouterSettings()
    general: GeneralSettings = GeneralSettings()


settings = Settings()
