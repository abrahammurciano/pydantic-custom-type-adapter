import datetime
import uuid

import pytest


@pytest.fixture
def utc_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


@pytest.fixture
def test_uuid() -> uuid.UUID:
    return uuid.uuid4()
