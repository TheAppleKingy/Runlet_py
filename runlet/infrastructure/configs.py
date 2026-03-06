# mypy: disable-error-code=call-arg
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBConfig(BaseSettings):
    postgres_user: str
    postgres_db: str
    postgres_password: str
    postgres_host: str

    @property
    def conn_url(self):
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:5432/{self.postgres_db}"


class AppConfig(BaseSettings):
    token_expire_time: int
    reg_confirm_url: str
    secret: str
    invite_expire_time: int
    invite_confirm_url: str
    password_change_confirm_url: str
    available_langs_codes: list[str]

    @property
    def available_langs(self):
        map_ = {
            "py": "Python",
            "go": "Golang",
            "cs": "C#",
            "js": "Java Script",
            "cpp": "C++",
            "java": "Java",
            "c": "C",
            "rb": "Ruby"
        }
        res = {map_.get(code.lower().strip()) for code in self.available_langs_codes}
        return [lang for lang in res if lang is not None]


class RabbitMQConfig(BaseSettings):
    rabbitmq_default_user: str
    rabbitmq_default_pass: str
    rabbitmq_host: str

    @property
    def conn_url(self):
        return f"amqp://{self.rabbitmq_default_user}:{self.rabbitmq_default_pass}@{self.rabbitmq_host}"


class EmailConfig(BaseSettings):
    email_sender: str
    email_sender_password: str
    email_host: str
    email_port: int
