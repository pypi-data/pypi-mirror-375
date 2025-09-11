from sqlalchemy.orm import DeclarativeBase
from typing import TypeVar


DeclarativeBaseT = TypeVar("DeclarativeBaseT", bound=DeclarativeBase)
