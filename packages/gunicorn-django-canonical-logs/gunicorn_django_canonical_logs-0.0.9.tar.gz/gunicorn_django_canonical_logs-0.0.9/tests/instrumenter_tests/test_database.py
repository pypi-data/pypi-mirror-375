from collections.abc import Generator

import pytest
import requests

from gunicorn_django_canonical_logs.event_context import Context
from gunicorn_django_canonical_logs.instrumenters.database import DatabaseInstrumenter, QueryCollector


@pytest.fixture
def instrumenter() -> Generator[DatabaseInstrumenter, None, None]:
    Context.reset()
    QueryCollector.reset()
    instrumenter = DatabaseInstrumenter()
    instrumenter.setup()
    yield instrumenter
    instrumenter.teardown()


def test_queries(instrumenter, live_server):
    Context.reset()
    QueryCollector.reset()
    url = live_server + "/db_queries/"
    resp = requests.get(url)
    assert resp.status_code == 200

    db_namespace = "db"

    instrumenter.call()

    assert Context.get("queries", namespace=db_namespace) == 3
    assert float(Context.get("time", namespace=db_namespace)) >= 0
    assert Context.get("dup_queries", namespace=db_namespace) == 2
    assert float(Context.get("dup_time", namespace=db_namespace)) >= 0


def test_reset(instrumenter, live_server):
    Context.reset()
    QueryCollector.reset()
    url = live_server + "/db_queries/"
    resp = requests.get(url)
    assert resp.status_code == 200

    db_namespace = "db"

    instrumenter.call()

    assert Context.get("queries", namespace=db_namespace) > 0
    assert float(Context.get("time", namespace=db_namespace)) >= 0
    assert Context.get("dup_queries", namespace=db_namespace) > 0
    assert float(Context.get("dup_time", namespace=db_namespace)) >= 0

    instrumenter.call()

    assert Context.get("queries", namespace=db_namespace) == 0
    assert float(Context.get("time", namespace=db_namespace)) == 0
    assert Context.get("dup_queries", namespace=db_namespace) == 0
    assert float(Context.get("dup_time", namespace=db_namespace)) == 0


def test_instrumenter_query_counts():
    QueryCollector.reset()
    QueryCollector.add("duplicate query", 1)
    QueryCollector.add("duplicate query", 2.50001)
    QueryCollector.add("unique query", 1)

    expected_data = {
        "dup_queries": 2,
        "dup_time": "3.500",
        "queries": 3,
        "time": "4.500",
    }

    assert QueryCollector.get_data() == expected_data
