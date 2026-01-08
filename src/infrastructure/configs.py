from pydantic_settings import BaseSettings, SettingsConfigDict


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


class RabbitMQConfig(BaseSettings):
    rabbitmq_default_user: str
    rabbitmq_default_pass: str
    rabbitmq_host: str

    def conn_url(self):
        return f"amqp://{self.rabbitmq_default_user}:{self.rabbitmq_default_pass}@{self.rabbitmq_host}"


db_conf = DBConfig()
app_conf = AppConfig()
rabbit_conf = RabbitMQConfig()
