from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter
from sqlalchemy.orm import registry, relationship, configure_mappers

from infrastructure.broker.factories import RabbitMQConsumerFactory
from infrastructure.db.tables import *
from application.messaging.registries import MessageConsumerRegistry
from interfaces.http import *
from domain.entities import *

AuthenticatedUserId = int


mapper_registry = registry()


def map_tables():
    mapper_registry.map_imperatively(User, users, properties={
        "tags": relationship(Tag, back_populates="users", secondary=users_tags, lazy='selectin'),
        "courses": relationship(Course, back_populates="_students", secondary=users_courses, lazy='selectin'),
    })
    mapper_registry.map_imperatively(Tag, tags, properties={
        "users": relationship(User, back_populates="tags", secondary=users_tags, lazy='selectin')
    })
    mapper_registry.map_imperatively(Course, courses, properties={
        "_students": relationship(User, secondary=users_courses, back_populates="courses", lazy='selectin'),
        "problems": relationship(Problem, back_populates="course", lazy='selectin')
    })
    mapper_registry.map_imperatively(Problem, problems)
    mapper_registry.map_imperatively(Attempt, attempts)
    configure_mappers()


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    map_tables()

api_router = APIRouter(prefix="/api/v1", tags=["API for Runlet"])
api_router.include_router(auth_router)

app = FastAPI(lifespan=lifespan_handler)

app.include_router(auth_router)

app.dependency_overrides
