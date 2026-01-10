from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import registry, relationship

from application.use_cases.user import *
from infrastructure.db.tables import *
from domain.exc import HandlingError
from interfaces.http import *
from domain.entities import *
from container import get_register_confirm_usecase, get_register_request_usecase
from logger import logger


mapper_registry = registry()


def map_tables():
    mapper_registry.map_imperatively(Problem, problems)
    mapper_registry.map_imperatively(Attempt, attempts)
    mapper_registry.map_imperatively(User, users, properties={
        "tags": relationship(Tag, back_populates="users", secondary=users_tags, lazy='selectin'),
        "courses": relationship(Course, back_populates="_students", secondary=users_courses, lazy='selectin'),
    })
    mapper_registry.map_imperatively(Tag, tags, properties={
        "users": relationship(User, back_populates="tags", secondary=users_tags, lazy='selectin')
    })
    mapper_registry.map_imperatively(Course, courses, properties={
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
    app.include_router(api_router)
