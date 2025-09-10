import asyncio
import functools
from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    AsyncIterator,
    Callable,
    Generator,
    Iterator,
    Optional,
    TypeVar,
)

from typing_extensions import ParamSpec, Self

from earthscope_sdk.client.data_access._query_plan._request_set import Req, RequestSet

if TYPE_CHECKING:
    import pyarrow as pa

    from earthscope_sdk.client import AsyncEarthScopeClient


class _QueryPlanBase(RequestSet[Req], ABC):
    """
    A base class for query plan objects.
    """

    @property
    @abstractmethod
    def planned(self) -> bool:
        """
        Whether or not query planning has occurred.
        """

    def __init__(self):
        super().__init__()

    def __repr__(self) -> str:
        if self.planned:
            return super().__repr__()
        else:
            return f"{self.__class__.__name__}(unplanned)"


class AsyncQueryPlan(_QueryPlanBase[Req]):
    """
    A query plan for an asynchronous bulk request.
    """

    @property
    def planned(self) -> bool:
        return self._planned

    def __init__(self, client: "AsyncEarthScopeClient"):
        super().__init__()
        self._client = client
        self._lock = asyncio.Lock()
        self._planned = False

        # wrap the synchronous hook to avoid blocking the event loop
        self.__async_hook = client.ctx.asyncify(self._hook)

    def __aiter__(self) -> AsyncIterator["pa.Table"]:
        return self._iter()

    ##########################################################################
    # Private methods
    ##########################################################################

    async def __build_plan_idempotent(self) -> None:
        """
        Fetch the requests for the query plan idempotently.
        """
        async with self._lock:
            if not self._planned:
                new_requests = await self._build_requests()
                self._replace_requests(new_requests)
                self._planned = True

    async def __collect_batch(self, batch: list[Req]) -> Optional["pa.Table"]:
        """
        Collect the results from a batch of requests into a single table.
        """
        import pyarrow as pa  # lazy import

        tables: list["pa.Table"] = []
        pending = [self._execute_one(request) for request in batch]

        for fut in asyncio.as_completed(pending):
            if table := await fut:
                tables.append(table)

        if len(tables) == 0:
            return None

        table = pa.concat_tables(tables)
        table = await self.__async_hook(table)
        return table

    ##########################################################################
    # Protected methods for subclasess to override
    ##########################################################################

    async def _iter(self) -> Generator["pa.Table", None, None]:
        """
        Iterate over the result set as tables composed of batches constructed from the request set.
        """
        await self.__build_plan_idempotent()
        for group in self.request_groups:
            if table := await self.__collect_batch(group):
                yield table

    @abstractmethod
    async def _build_requests(self) -> list[Req]:
        """
        Build the requests for the query plan.
        """

    @abstractmethod
    async def _execute_one(self, req: Req) -> Optional["pa.Table"]:
        """
        Execute a single request.
        """

    def _hook(self, table: "pa.Table") -> "pa.Table":
        """
        Hook to modify the table after execution.
        """
        return table

    ##########################################################################
    # Public methods
    ##########################################################################

    async def fetch(self) -> "pa.Table":
        """
        Materialize the entire result set into a single table.
        """
        await self.__build_plan_idempotent()
        return await self.__collect_batch(self.all_requests)

    async def plan(self):
        """
        Plan the individual requests necessary to fulfill the bulk request.
        """
        await self.__build_plan_idempotent()
        return self


A = TypeVar("A", bound="AsyncQueryPlan")
T_ParamSpec = ParamSpec("T_ParamSpec")
T_AsyncRequest = TypeVar("T_AsyncRequest")


class QueryPlan(_QueryPlanBase[Req]):
    """
    A query plan for a synchronous bulk request.
    """

    def __init__(self, async_plan: A):
        super().__init__()
        self._async_plan = async_plan
        self._client = async_plan._client

        # Expose the async query plan methods as sync methods
        self.fetch = self._async_plan._client.ctx.syncify(self._async_plan.fetch)
        self.plan = self._wrap_and_return_self(self._async_plan.plan)

        self.sort_by = self._wrap_and_return_self(self._async_plan.sort_by)
        self.group_by = self._wrap_and_return_self(self._async_plan.group_by)

    ##########################################################################
    # Redefine to wrap the async query plan
    ##########################################################################

    @property
    def all_requests(self) -> list[Req]:
        return self._async_plan.all_requests

    @property
    def planned(self) -> bool:
        return self._async_plan.planned

    @property
    def request_groups(self) -> list[list[Req]]:
        return self._async_plan.request_groups

    def __len__(self) -> int:
        return len(self._async_plan)

    def __repr__(self) -> str:
        if self.planned:
            return self._async_plan._repr(self.__class__)
        else:
            return f"{self.__class__.__name__}(unplanned)"

    ##########################################################################
    # Redefine the iterator to be synchronous
    ##########################################################################

    def __iter__(self) -> Iterator["pa.Table"]:
        return self.__iter()

    def __iter(self) -> Iterator["pa.Table"]:
        """
        Iterate over the result set as tables composed of batches constructed from the request set.
        """
        it = self._async_plan._iter()
        anext = self._async_plan._client.ctx.syncify(it.__anext__)
        while True:
            try:
                yield anext()
            except StopAsyncIteration:
                break

    ##########################################################################
    # Helper methods for sync compatibility
    ##########################################################################

    @classmethod
    def _syncify_query_plan(
        cls,
        fn: Callable[T_ParamSpec, T_AsyncRequest],
    ) -> Callable[T_ParamSpec, Self]:
        """
        Given a function that returns an async query plan,
        return a function that returns a sync query plan.
        """

        @functools.wraps(fn)
        def wrapper(*args: T_ParamSpec.args, **kwargs: T_ParamSpec.kwargs) -> Self:
            async_plan = fn(*args, **kwargs)
            return cls(async_plan)

        return wrapper

    def _wrap_and_return_self(
        self,
        fn: Callable[T_ParamSpec, T_AsyncRequest],
    ) -> Callable[T_ParamSpec, Self]:
        """
        Wrap a function that returns an async query plan and return
        a function that instead returns this sync query plan.
        """
        if not callable(fn):
            raise ValueError("fn must be a callable")

        if asyncio.iscoroutinefunction(fn):
            sync_fn = self._client.ctx.syncify(fn)
        else:
            sync_fn = fn

        @functools.wraps(fn)
        def wrapper(*args: T_ParamSpec.args, **kwargs: T_ParamSpec.kwargs) -> Self:
            sync_fn(*args, **kwargs)
            return self

        return wrapper
