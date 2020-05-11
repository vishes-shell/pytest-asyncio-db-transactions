import asyncio
import pytest
from app.models import notes
import functools


@pytest.fixture
async def check_empty_database(sqlite_db):
    """All tests use transaction and database clean after tests
    """
    yield

    query = notes.select()
    data = await sqlite_db.fetch_all(query)
    if data:
        pytest.fail("db data should be rolled back")


@pytest.fixture
async def rollback_transaction(sqlite_db):
    async with sqlite_db.transaction(force_rollback=True):
        yield


async def main(sqlite_db):
    query = notes.insert().values(text="text", completed=False)
    await sqlite_db.execute(query)

    query = notes.select()
    if not await sqlite_db.fetch_all(query):
        pytest.fail("no data in database")


def transaction_wrapper(func, force_rollback=True):
    @functools.wraps(func)
    async def wrapper(sqlite_db, *args, **kwargs):
        async with sqlite_db.transaction(force_rollback=force_rollback):
            return await func(sqlite_db, *args, **kwargs)

    return wrapper


def async_adapter(wrapped_func):
    """Decorator used to run async test cases.

    Source: https://github.com/encode/databases/blob/master/tests/test_databases.py#L100-L111
    """

    @functools.wraps(wrapped_func)
    def run_sync(*args, **kwargs):
        loop = asyncio.new_event_loop()
        task = wrapped_func(*args, **kwargs)
        return loop.run_until_complete(task)

    return run_sync


@transaction_wrapper
@pytest.mark.asyncio
async def test_transaction_wrapper(sqlite_db, check_empty_database):
    """Transaction wrapper with default rolling back
    rolls transaction after tests completes with pytest asyncio mark
    """
    await main(sqlite_db)


@async_adapter
@transaction_wrapper
async def test_transaction_wrapper_and_async_adapter(sqlite_db, check_empty_database):
    """Transaction wrapper with default rolling back
    rolls transaction after wrapper in async_adapter
    """
    await main(sqlite_db)


@pytest.mark.asyncio
async def test_base_context_manager(sqlite_db, check_empty_database):
    """Transaction context manager with force_rollback
    rolls transaction after all
    """
    async with sqlite_db.transaction(force_rollback=True):
        await main(sqlite_db)


@async_adapter
async def test_rollback_transaction_fixture_and_async_adapter(
    sqlite_db, rollback_transaction, check_empty_database
):
    await main(sqlite_db)


@pytest.mark.asyncio
async def test_rollback_transaction_fixture_and_asyncio_mark(
    sqlite_db, rollback_transaction, check_empty_database
):
    await main(sqlite_db)
