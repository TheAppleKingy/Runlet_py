from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter
from sqlalchemy.orm import mapper, registry, relationship, column_property

from infrastructure.broker.factories import RabbitMQConsumerFactory
from infrastructure.db.tables import *
from application.messaging.registries import MessageConsumerRegistry
from interfaces.broker.rabbitmq.callback import callback_registry
from interfaces.http import *
from domain.entities import *

AuthenticatedUserId = int


mapper_registry = registry()


def map_tables():
    mapper_registry.map_imperatively(User, users, properties={
        "tags": relationship(Tag, back_populates="users", secondary=users_tags, lazy='selectin'),
        "courses": relationship(Tag, back_populates="_students", secondary=users_courses, lazy='selectin'),
    })
    mapper_registry.map_imperatively(Tag, tags, properties={
        "users": relationship(User, back_populates="tags", secondary=users_tags, lazy='selectin')
    })
    mapper_registry.map_imperatively(Course, courses, properties={
        "_students": relationship(User, secondary=users_courses, back_populates="courses", lazy='selectin'),
        "problems": relationship(Problem, back_populates="course", lazy='selectin'),
        "_teacher_id": column_property(courses.c.teacher_id)
    })
    mapper_registry.map_imperatively(Problem, problems)


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    _consumer_registry = MessageConsumerRegistry(RabbitMQConsumerFactory())
    _consumer_registry.register("callback", callback_registry)

api_router = APIRouter(prefix="/api/v1", tags=["API for Runlet"])
api_router.include_router(auth_router)

app = FastAPI(lifespan=lifespan_handler)

app.include_router(auth_router)

app.dependency_overrides
