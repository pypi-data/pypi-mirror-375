from maleo.mixins.parameter import (
    Filters,
    ListOfDataStatuses,
    Sorts,
    Search,
    UseCache,
    StatusUpdateAction,
)
from maleo.dtos.pagination import BaseFlexiblePagination, BaseStrictPagination


class ReadSingleQuery(
    ListOfDataStatuses,
    UseCache,
):
    pass


class BaseReadMultipleQuery(
    Sorts,
    Search,
    ListOfDataStatuses,
    Filters,
    UseCache,
):
    pass


class ReadUnpaginatedMultipleQuery(
    BaseFlexiblePagination,
    BaseReadMultipleQuery,
):
    pass


class ReadPaginatedMultipleQuery(
    BaseStrictPagination,
    BaseReadMultipleQuery,
):
    pass


class StatusUpdateBody(StatusUpdateAction):
    pass
