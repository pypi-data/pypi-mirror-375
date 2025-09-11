from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import MetaData
from typing import Generic, Optional, TypeVar
from maleo.dtos.contexts.service import ServiceContext
from maleo.logging.logger import Database
from .config import (
    ElasticsearchConfig,
    MongoConfig,
    RedisConfig,
    MySQLConfig,
    PostgreSQLConfig,
    SQLiteConfig,
    SQLServerConfig,
    ConfigT,
)
from .managers import (
    ElasticsearchManager,
    MongoManager,
    RedisManager,
    MySQLManager,
    PostgreSQLManager,
    SQLiteManager,
    SQLServerManager,
    ManagerT,
)


class Handler(
    BaseModel,
    Generic[
        ConfigT,
        ManagerT,
    ],
):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    config: ConfigT = Field(..., description="Config")
    manager: ManagerT = Field(..., description="Manager")


HandlerT = TypeVar("HandlerT", bound=Handler)


class ElasticsearchHandler(Handler[ElasticsearchConfig, ElasticsearchManager]):
    @classmethod
    def new(
        cls,
        config: ElasticsearchConfig,
        logger: Database,
        service_context: Optional[ServiceContext] = None,
    ) -> "ElasticsearchHandler":
        manager = ElasticsearchManager(
            config=config, logger=logger, service_context=service_context
        )
        return cls(config=config, manager=manager)


class MongoHandler(Handler[MongoConfig, MongoManager]):
    pass


class RedisHandler(Handler[RedisConfig, RedisManager]):
    pass


class MySQLHandler(Handler[MySQLConfig, MySQLManager]):
    pass


class PostgreSQLHandler(Handler[PostgreSQLConfig, PostgreSQLManager]):
    @classmethod
    def new(
        cls,
        config: PostgreSQLConfig,
        logger: Database,
        metadata: MetaData,
        service_context: Optional[ServiceContext] = None,
    ) -> "PostgreSQLHandler":
        manager = PostgreSQLManager(
            config=config,
            logger=logger,
            metadata=metadata,
            service_context=service_context,
        )
        return cls(config=config, manager=manager)


class SQLiteHandler(Handler[SQLiteConfig, SQLiteManager]):
    pass


class SQLServerHandler(Handler[SQLServerConfig, SQLServerManager]):
    pass


class BaseHandlers(BaseModel, Generic[HandlerT]):
    primary: HandlerT = Field(..., description="Primary handler")


BaseHandlersT = TypeVar("BaseHandlersT", bound=Optional[BaseHandlers])


class ElasticsearchHandlers(BaseHandlers[ElasticsearchHandler]):
    pass


ElasticsearchHandlersT = TypeVar(
    "ElasticsearchHandlersT", bound=Optional[ElasticsearchHandlers]
)


class MongoHandlers(BaseHandlers[MongoHandler]):
    pass


MongoHandlersT = TypeVar("MongoHandlersT", bound=Optional[MongoHandlers])


class RedisHandlers(BaseHandlers[RedisHandler]):
    pass


RedisHandlersT = TypeVar("RedisHandlersT", bound=Optional[RedisHandlers])


class NoSQLHandlers(
    BaseModel, Generic[ElasticsearchHandlersT, MongoHandlersT, RedisHandlersT]
):
    elasticsearch: ElasticsearchHandlersT = Field(
        ..., description="Elasticsearch handlers"
    )
    mongo: MongoHandlersT = Field(..., description="Mongo handlers")
    redis: RedisHandlersT = Field(..., description="Redis handlers")


NoSQLHandlersT = TypeVar("NoSQLHandlersT", bound=Optional[NoSQLHandlers])


class MySQLHandlers(BaseHandlers[MySQLHandler]):
    pass


MySQLHandlersT = TypeVar("MySQLHandlersT", bound=Optional[MySQLHandlers])


class PostgreSQLHandlers(BaseHandlers[PostgreSQLHandler]):
    pass


PostgreSQLHandlersT = TypeVar("PostgreSQLHandlersT", bound=Optional[PostgreSQLHandlers])


class SQLiteHandlers(BaseHandlers[SQLiteHandler]):
    pass


SQLiteHandlersT = TypeVar("SQLiteHandlersT", bound=Optional[SQLiteHandlers])


class SQLServerHandlers(BaseHandlers[SQLServerHandler]):
    pass


SQLServerHandlersT = TypeVar("SQLServerHandlersT", bound=Optional[SQLServerHandlers])


class SQLHandlers(
    BaseModel,
    Generic[
        MySQLHandlersT,
        PostgreSQLHandlersT,
        SQLiteHandlersT,
        SQLServerHandlersT,
    ],
):
    mysql: MySQLHandlersT = Field(..., description="MySQL handlers")
    postgresql: PostgreSQLHandlersT = Field(..., description="PostgreSQL handlers")
    sqlite: SQLiteHandlersT = Field(..., description="SQLite handlers")
    sqlserver: SQLServerHandlersT = Field(..., description="SQLServer handlers")


SQLHandlersT = TypeVar("SQLHandlersT", bound=Optional[SQLHandlers])


class Handlers(
    BaseModel,
    Generic[
        NoSQLHandlersT,
        SQLHandlersT,
    ],
):
    nosql: NoSQLHandlersT = Field(..., description="NoSQL handlers")
    sql: NoSQLHandlersT = Field(..., description="SQL handlers")


HandlersT = TypeVar("HandlersT", bound=Optional[Handlers])
