from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import registry, relationship

from src.application.use_cases.student import *
from src.infrastructure.db.tables import *
from src.domain.exc import HandlingError
from src.interfaces.http import *
from src.domain.entities import *
from src.logger import logger


mapper_registry = registry()


def map_tables():
    mapper_registry.map_imperatively(Problem, problems)
    mapper_registry.map_imperatively(Attempt, attempts)
    mapper_registry.map_imperatively(User, users, properties={
        "courses": relationship(Course, back_populates="_students", secondary=users_courses, lazy='selectin'),
    })
    mapper_registry.map_imperatively(Tag, tags, properties={
        "students": relationship(User, secondary=users_tags, lazy='selectin')
    })
    mapper_registry.map_imperatively(Course, courses, properties={
        "tags": relationship(Tag, lazy='selectin'),
        "_students": relationship(User, secondary=users_courses, back_populates="courses", lazy='selectin'),
        "problems": relationship(Problem, lazy='selectin')
    })
    mapper_registry.configure()


def handle_errs(r: Request, e: HandlingError):
    raise HTTPException(e.status, detail=str(e))


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    map_tables()
    setup_routers(app)
    logger.info("App is ready. Starting...")
    yield
    logger.info("App shutdown")


app = FastAPI(lifespan=lifespan_handler)


@app.middleware("http")
async def handle_auth(r: Request, call_next):
    try:
        return await call_next(r)
    except HandlingError as e:
        return JSONResponse({"detail": str(e)}, e.status)


def setup_routers(app: FastAPI):
    api_router = APIRouter(prefix="/api/v1")
    api_router.include_router(auth_router)
    user_router.include_router(student_router)
    user_router.include_router(teacher_router)
    api_router.include_router(user_router)
    app.include_router(api_router)
