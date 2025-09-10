from typing import NamedTuple

import pyarrow as pa
import pytest

from earthscope_sdk.client._client import AsyncEarthScopeClient, EarthScopeClient
from earthscope_sdk.client.data_access._query_plan._query_plan import (
    AsyncQueryPlan,
    QueryPlan,
)

_responses = {
    1: pa.table({"key": [1, 2, 3], "value": ["a", "b", "c"]}),
    2: pa.table({"key": [4, 5, 6], "value": ["d", "e", "f"]}),
    3: pa.table({"key": [7, 8, 9], "value": ["g", "h", "i"]}),
    4: pa.table({"key": [10, 11, 12], "value": ["j", "k", "l"]}),
}

_join_table = pa.table(
    {
        "key": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        "meta": [
            "foo",
            "bar",
            "baz",
            "qux",
            "quux",
            "corge",
            "grault",
            "garply",
            "waldo",
            "fred",
            "plugh",
            "xyzzy",
        ],
    }
)


class MyReq(NamedTuple):
    request_key: int


class MyAsyncQueryPlan(AsyncQueryPlan[MyReq]):
    def __init__(self, client: AsyncEarthScopeClient):
        super().__init__(client)

    async def _build_requests(self) -> list[MyReq]:
        return [MyReq(request_key=k) for k in _responses.keys()]

    async def _execute_one(self, req: MyReq) -> pa.Table:
        return _responses[req.request_key]

    def _hook(self, table: pa.Table) -> pa.Table:
        return table.join(_join_table, keys="key").combine_chunks().sort_by("key")


class MySyncQueryPlan(QueryPlan[MyReq]): ...


class TestAsyncQueryPlan:
    @pytest.mark.asyncio
    async def test_fetch(self):
        async with AsyncEarthScopeClient() as client:
            plan = MyAsyncQueryPlan(client)

            assert len(plan) == 0
            assert repr(plan) == "MyAsyncQueryPlan(unplanned)"

            table = await plan.fetch()
            assert table == pa.table(
                {
                    "key": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                    "value": [
                        "a",
                        "b",
                        "c",
                        "d",
                        "e",
                        "f",
                        "g",
                        "h",
                        "i",
                        "j",
                        "k",
                        "l",
                    ],
                    "meta": [
                        "foo",
                        "bar",
                        "baz",
                        "qux",
                        "quux",
                        "corge",
                        "grault",
                        "garply",
                        "waldo",
                        "fred",
                        "plugh",
                        "xyzzy",
                    ],
                }
            )

    @pytest.mark.asyncio
    async def test_iteration(self):
        async with AsyncEarthScopeClient() as client:
            plan = await MyAsyncQueryPlan(client).plan()

            assert len(plan) == 4
            assert len(plan.request_groups) == 4

            plan.group_by(lambda r: r.request_key % 2)
            assert len(plan.request_groups) == 2

            it = plan.__aiter__()
            t0 = await it.__anext__()
            t1 = await it.__anext__()
            with pytest.raises(StopAsyncIteration):
                await it.__anext__()

            assert t0 == pa.table(
                {
                    "key": [1, 2, 3, 7, 8, 9],
                    "value": ["a", "b", "c", "g", "h", "i"],
                    "meta": ["foo", "bar", "baz", "grault", "garply", "waldo"],
                }
            )
            assert t1 == pa.table(
                {
                    "key": [4, 5, 6, 10, 11, 12],
                    "value": ["d", "e", "f", "j", "k", "l"],
                    "meta": ["qux", "quux", "corge", "fred", "plugh", "xyzzy"],
                }
            )


class TestSyncQueryPlan:
    def test_fetch(self):
        with EarthScopeClient() as client:
            async_plan = MyAsyncQueryPlan(client._async_client)
            plan = MySyncQueryPlan(async_plan)

            assert len(plan) == 0
            assert repr(plan) == "MySyncQueryPlan(unplanned)"

            table = plan.fetch()
            assert table == pa.table(
                {
                    "key": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                    "value": [
                        "a",
                        "b",
                        "c",
                        "d",
                        "e",
                        "f",
                        "g",
                        "h",
                        "i",
                        "j",
                        "k",
                        "l",
                    ],
                    "meta": [
                        "foo",
                        "bar",
                        "baz",
                        "qux",
                        "quux",
                        "corge",
                        "grault",
                        "garply",
                        "waldo",
                        "fred",
                        "plugh",
                        "xyzzy",
                    ],
                }
            )

    def test_iteration(self):
        with EarthScopeClient() as client:
            async_plan = MyAsyncQueryPlan(client._async_client)
            plan = MySyncQueryPlan(async_plan).plan()

            assert len(plan) == 4
            assert len(plan.request_groups) == 4

            plan.group_by(lambda r: r.request_key % 2)
            assert len(plan.request_groups) == 2

            it = iter(plan)
            t0 = next(it)
            t1 = next(it)
            with pytest.raises(StopIteration):
                next(it)

            assert t0 == pa.table(
                {
                    "key": [1, 2, 3, 7, 8, 9],
                    "value": ["a", "b", "c", "g", "h", "i"],
                    "meta": ["foo", "bar", "baz", "grault", "garply", "waldo"],
                }
            )
            assert t1 == pa.table(
                {
                    "key": [4, 5, 6, 10, 11, 12],
                    "value": ["d", "e", "f", "j", "k", "l"],
                    "meta": ["qux", "quux", "corge", "fred", "plugh", "xyzzy"],
                }
            )
