import re

import pytest

from gunicorn_django_canonical_logs import Context
from gunicorn_django_canonical_logs.instrumenters.request import RequestInstrumenter


def test_request_ok(client, settings):
    settings.MIDDLEWARE = [RequestInstrumenter().request_middleware_string_path]
    resp = client.get("/ok/")
    assert resp.status_code == 200

    expected_req_context = {"method": "GET", "path": "/ok/", "referrer": None, "user_agent": None}

    req_namespace = "req"
    resp_namespace = "resp"

    for key, val in expected_req_context.items():
        assert Context.get(key, namespace=req_namespace) == val

    expected_resp_context = {"status": 200, "view": "app.ok"}

    for key, val in expected_resp_context.items():
        assert Context.get(key, namespace=resp_namespace) == val

    assert re.match(r"0\.\d{3}", Context.get("time", namespace=resp_namespace))
    assert re.match(r"0\.\d{3}", Context.get("cpu_time", namespace=resp_namespace))


def test_request_404(client, settings):
    settings.MIDDLEWARE = [RequestInstrumenter().request_middleware_string_path]
    resp = client.get("/does-not-exist/")
    assert resp.status_code == 404

    expected_req_context = {
        "method": "GET",
        "path": "/does-not-exist/",
        "referrer": None,
        "user_agent": None,
    }

    req_namespace = "req"
    resp_namespace = "resp"

    for key, val in expected_req_context.items():
        assert Context.get(key, namespace=req_namespace) == val

    expected_resp_context = {"status": 404, "view": None}

    for key, val in expected_resp_context.items():
        assert Context.get(key, namespace=resp_namespace) == val

    assert re.match(r"0\.\d{3}", Context.get("time", namespace=resp_namespace))
    assert re.match(r"0\.\d{3}", Context.get("cpu_time", namespace=resp_namespace))


def test_request_500(client, settings):
    settings.MIDDLEWARE = [RequestInstrumenter().request_middleware_string_path]

    with pytest.raises(match="Oh noes!"):
        client.get("/view_exception/")

    expected_req_context = {
        "method": "GET",
        "path": "/view_exception/",
        "referrer": None,
        "user_agent": None,
    }

    req_namespace = "req"
    resp_namespace = "resp"

    for key, val in expected_req_context.items():
        assert Context.get(key, namespace=req_namespace) == val

    expected_resp_context = {"status": 500, "view": "app.view_exception"}

    for key, val in expected_resp_context.items():
        assert Context.get(key, namespace=resp_namespace) == val

    assert re.match(r"0\.\d{3}", Context.get("time", namespace=resp_namespace))
    assert re.match(r"0\.\d{3}", Context.get("cpu_time", namespace=resp_namespace))


def test_request_headers(client, settings):
    settings.MIDDLEWARE = [RequestInstrumenter().request_middleware_string_path]

    referer = "http://some-other-site.com"
    user_agent = "some http client"

    resp = client.get("/ok/", headers={"User-agent": user_agent, "Referrer": referer})
    assert resp.status_code == 200

    expected_req_context = {"referrer": referer, "user_agent": user_agent}

    req_namespace = "req"

    for key, val in expected_req_context.items():
        assert Context.get(key, namespace=req_namespace) == val
