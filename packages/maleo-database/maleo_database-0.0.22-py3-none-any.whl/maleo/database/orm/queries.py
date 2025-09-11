from sqlalchemy import asc, cast, desc, or_, select
from sqlalchemy.orm import DeclarativeBase, Session, aliased
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql import Select
from sqlalchemy.types import DATE, String, TEXT, TIMESTAMP
from typing import Any, Sequence, Tuple, Type, TypeVar
from maleo.enums.sort import Order
from maleo.mixins.general import DateFilter, SortColumn
from maleo.types.base.any import OptionalAny
from maleo.types.base.boolean import OptionalBoolean
from maleo.types.base.integer import OptionalListOfIntegers
from maleo.types.base.string import OptionalListOfStrings, OptionalString
from maleo.types.enums.status import OptionalListOfDataStatuses


T = TypeVar("T", bound=DeclarativeBase)
R = TypeVar(
    "R", bound=Tuple[Any, ...]
)  # result shape inferred from Select (tuple[...])


def filter_column(
    stmt: Select[R],
    table: Type[T],
    column: str,
    value: OptionalAny = None,
    include_null: bool = False,
) -> Select[R]:
    column_attr = getattr(table, column, None)
    if column_attr is None or not isinstance(column_attr, InstrumentedAttribute):
        return stmt

    value_filters = []
    if value is not None:
        value_filters.extend([column_attr == val for val in value])

    if value_filters:
        if include_null:
            value_filters.append(column_attr.is_(None))
        stmt = stmt.filter(or_(*value_filters))

    return stmt


def filter_ids(
    stmt: Select[R],
    table: Type[T],
    column: str,
    ids: OptionalListOfIntegers = None,
    include_null: bool = False,
) -> Select[R]:
    column_attr = getattr(table, column, None)
    if column_attr is None or not isinstance(column_attr, InstrumentedAttribute):
        return stmt

    id_filters = []
    if ids is not None:
        id_filters.extend([column_attr == id for id in ids])

    if id_filters:
        if include_null:
            id_filters.append(column_attr.is_(None))
        stmt = stmt.filter(or_(*id_filters))

    return stmt


def filter_timestamps(
    stmt: Select[R],
    table: Type[T],
    date_filters: Sequence[DateFilter],
) -> Select[R]:
    if date_filters:
        for date_filter in date_filters:
            try:
                sqla_table = table.__table__
                column = sqla_table.columns[date_filter.name]
                column_attr: InstrumentedAttribute = getattr(table, date_filter.name)
                if isinstance(column.type, (TIMESTAMP, DATE)):
                    if date_filter.from_date and date_filter.to_date:
                        stmt = stmt.filter(
                            column_attr.between(
                                date_filter.from_date, date_filter.to_date
                            )
                        )
                    elif date_filter.from_date:
                        stmt = stmt.filter(column_attr >= date_filter.from_date)
                    elif date_filter.to_date:
                        stmt = stmt.filter(column_attr <= date_filter.to_date)
            except KeyError:
                continue
    return stmt


def filter_statuses(
    stmt: Select[R],
    table: Type[T],
    statuses: OptionalListOfDataStatuses,
) -> Select[R]:
    if statuses is not None:
        status_filters = [table.status == status for status in statuses]  # type: ignore
        stmt = stmt.filter(or_(*status_filters))
    return stmt


def filter_is_root(
    stmt: Select[R],
    table: Type[T],
    parent_column: str = "parent_id",
    is_root: OptionalBoolean = None,
) -> Select[R]:
    parent_attr = getattr(table, parent_column, None)
    if parent_attr is None or not isinstance(parent_attr, InstrumentedAttribute):
        return stmt
    if is_root is not None:
        stmt = stmt.filter(
            parent_attr.is_(None) if is_root else parent_attr.is_not(None)
        )
    return stmt


def filter_is_parent(
    session: Session,
    stmt: Select[R],
    table: Type[T],
    id_column: str = "id",
    parent_column: str = "parent_id",
    is_parent: OptionalBoolean = None,
) -> Select[R]:
    id_attr = getattr(table, id_column, None)
    if id_attr is None or not isinstance(id_attr, InstrumentedAttribute):
        return stmt
    parent_attr = getattr(table, parent_column, None)
    if parent_attr is None or not isinstance(parent_attr, InstrumentedAttribute):
        return stmt
    if is_parent is not None:
        child_table = aliased(table)
        child_parent_attr = getattr(child_table, parent_column)
        subq = select(child_table).filter(child_parent_attr == id_attr).exists()
        stmt = stmt.filter(subq if is_parent else ~subq)
    return stmt


def filter_is_child(
    stmt: Select[R],
    table: Type[T],
    parent_column: str = "parent_id",
    is_child: OptionalBoolean = None,
) -> Select[R]:
    parent_attr = getattr(table, parent_column, None)
    if parent_attr is None or not isinstance(parent_attr, InstrumentedAttribute):
        return stmt
    if is_child is not None:
        stmt = stmt.filter(
            parent_attr.is_not(None) if is_child else parent_attr.is_(None)
        )
    return stmt


def filter_is_leaf(
    session: Session,
    stmt: Select[R],
    table: Type[T],
    id_column: str = "id",
    parent_column: str = "parent_id",
    is_leaf: OptionalBoolean = None,
) -> Select[R]:
    id_attr = getattr(table, id_column, None)
    if id_attr is None or not isinstance(id_attr, InstrumentedAttribute):
        return stmt
    parent_attr = getattr(table, parent_column, None)
    if parent_attr is None or not isinstance(parent_attr, InstrumentedAttribute):
        return stmt
    if is_leaf is not None:
        child_table = aliased(table)
        child_parent_attr = getattr(child_table, parent_column)
        subq = select(child_table).filter(child_parent_attr == id_attr).exists()
        stmt = stmt.filter(~subq if is_leaf else subq)
    return stmt


def search(
    stmt: Select[R],
    table: Type[T],
    search: OptionalString = None,
    columns: OptionalListOfStrings = None,
) -> Select[R]:
    if search is None:
        return stmt

    search_term = f"%{search}%"
    sqla_table = table.__table__
    search_filters = []

    for name, attr in vars(table).items():
        if not isinstance(attr, InstrumentedAttribute):
            continue

        try:
            column = sqla_table.columns[name]
        except KeyError:
            continue

        if columns is not None and name not in columns:
            continue

        if isinstance(column.type, (String, TEXT)):
            search_filters.append(cast(attr, TEXT).ilike(search_term))

    if search_filters:
        stmt = stmt.filter(or_(*search_filters))

    return stmt


def sort(
    stmt: Select[R],
    table: Type[T],
    sort_columns: Sequence[SortColumn],
) -> Select[R]:
    for sort_column in sort_columns:
        try:
            sort_col = getattr(table, sort_column.name)
            sort_col = (
                asc(sort_col) if sort_column.order is Order.ASC else desc(sort_col)
            )
            stmt = stmt.order_by(sort_col)
        except AttributeError:
            continue
    return stmt


def paginate(stmt: Select[R], page: int, limit: int) -> Select[R]:
    offset: int = int((page - 1) * limit)
    stmt = stmt.limit(limit).offset(offset)
    return stmt
