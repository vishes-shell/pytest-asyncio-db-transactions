import pytest
import sqlalchemy as sa
from app.models import metadata
from databases import Database

SQLITE_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="session")
def sqlite_db() -> Database:
    engine = sa.create_engine(SQLITE_DATABASE_URL)
    metadata.create_all(engine)

    yield Database(SQLITE_DATABASE_URL)

    metadata.drop_all(engine)
