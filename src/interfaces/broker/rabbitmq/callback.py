from pydantic import BaseModel
from fastapi import Depends

from ploomby.registry import HandlersRegistry

from src.logger import logger

callback_registry = HandlersRegistry()
