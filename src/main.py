from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from dishka.integrations.fastapi import setup_dishka
from sqlalchemy.orm import registry, relationship, column_property
from ploomby.registry import MessageConsumerRegistry
from ploomby.rabbit import RabbitConsumerFactory

from src.application.use_cases.student import *
from src.application.use_cases.user import *
from src.application.use_cases.teacher import *
from src.infrastructure.db.tables import *
from src.domain.exc import HandlingError
from src.interfaces.http import *
from src.domain.entities import *
from src.logger import logger
from src.container import (
    container
)


def map_tables():
    mapper_registry = registry()
    mapper_registry.map_imperatively(Problem, problems)
    mapper_registry.map_imperatively(Attempt, attempts, properties={
        "problem": relationship(Problem, lazy='raise', uselist=False)
    })
    mapper_registry.map_imperatively(Module, modules, properties={
        "_problems": relationship(Problem, lazy="raise", cascade="all, delete-orphan", passive_deletes=True)
    })
    mapper_registry.map_imperatively(User, users, properties={
        "courses": relationship(Course, secondary=users_courses, back_populates="_students", lazy='raise')
    })
    mapper_registry.map_imperatively(Tag, tags, properties={
        "students": relationship(User, secondary=users_tags, lazy='raise')
    })
    mapper_registry.map_imperatively(Course, courses, properties={
        "_teacher_id": column_property(courses.c.teacher_id),
        "_tags": relationship(Tag, lazy='raise', cascade="all, delete-orphan", passive_deletes=True),
        "_students": relationship(User, secondary=users_courses, back_populates="courses", lazy='raise'),
        "_modules": relationship(Module, lazy='raise', cascade="all, delete-orphan", passive_deletes=True)
    })
    mapper_registry.configure()


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    map_tables()
    setup_routers(app)
    # await consumer_registry.register("callback", "task_name")
    logger.info("App is ready. Starting...")
    yield
    await container.close()
    logger.info("App shutdown")


app = FastAPI(lifespan=lifespan_handler)
setup_dishka(container, app)


@app.exception_handler(HandlingError)
async def handle_auth(r: Request, e: HandlingError):
    return JSONResponse({"detail": str(e)}, e.status)


def setup_routers(app: FastAPI):
    api_router = APIRouter(prefix="/api/v1")
    api_router.include_router(auth_router)
    user_router.include_router(student_router)
    user_router.include_router(teacher_router)
    api_router.include_router(user_router)
    app.include_router(api_router)
