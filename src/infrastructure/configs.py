# mypy: disable-error-code=call-arg
from pydantic_settings import BaseSettings


class DBConfig(BaseSettings):
    postgres_user: str
    postgres_db: str
    postgres_password: str
    postgres_host: str

    def conn_url(self):
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:5432/{self.postgres_db}"


class AppConfig(BaseSettings):
    token_expire_time: int
    reg_confirm_url: str
    secret: str
    invite_expire_time: int
    invite_confirm_url: str


class RabbitMQConfig(BaseSettings):
    rabbitmq_default_user: str
    rabbitmq_default_pass: str
    rabbitmq_host: str

    def conn_url(self):
        return f"amqp://{self.rabbitmq_default_user}:{self.rabbitmq_default_pass}@{self.rabbitmq_host}"


class EmailConfig(BaseSettings):
    email_sender: str
    email_sender_password: str
    email_host: str
    email_port: int


db_conf = DBConfig()
app_conf = AppConfig()
rabbit_conf = RabbitMQConfig()
email_conf = EmailConfig()
