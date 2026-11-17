"""Time accounting tools from pull request #3."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from zammad_mcp_server.client import ZammadClient
from zammad_mcp_server.models import ArticleCreateRequest, TimeAccounting


def _client() -> ZammadClient:
    return ZammadClient(url="https://zammad.example.com", http_token="tok")


def test_create_time_accounting_builds_request(monkeypatch: Any) -> None:
    client = _client()
    calls: list[tuple[str, str, dict[str, Any]]] = []

    def fake_request(method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        calls.append((method, path, kwargs))
        return {"id": 1, "ticket_id": 42, "time_unit": "60"}

    monkeypatch.setattr(client, "_request", fake_request)
    result = client.create_time_accounting(
        ticket_id=42, time_unit=60, type_id=3, ticket_article_id=99
    )

    assert calls == [
        (
            "POST",
            "/tickets/42/time_accountings",
            {"json": {"time_unit": "60", "type_id": 3, "ticket_article_id": 99}},
        )
    ]
    assert result.time_unit == "60"


def test_create_time_accounting_minimal(monkeypatch: Any) -> None:
    client = _client()
    captured: dict[str, Any] = {}

    def fake_request(method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        captured.update({"method": method, "path": path, **kwargs})
        return {"id": 2, "time_unit": "15"}

    monkeypatch.setattr(client, "_request", fake_request)
    client.create_time_accounting(ticket_id=7, time_unit=15)

    assert captured["json"] == {"time_unit": "15"}


def test_get_time_accountings_list(monkeypatch: Any) -> None:
    client = _client()
    monkeypatch.setattr(
        client, "_request", lambda _method, _path, **_kwargs: [{"id": 1, "time_unit": "30"}]
    )
    entries = client.get_time_accountings(7)
    assert entries[0].time_unit == "30"


def test_create_article_books_time(monkeypatch: Any) -> None:
    client = _client()
    paths: list[str] = []

    def fake_request(method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        paths.append(path)
        if path == "/ticket_articles":
            return {"id": 555, "ticket_id": 42, "body": "x", "type": "note", "internal": True}
        return {"id": 1, "time_unit": "60"}

    monkeypatch.setattr(client, "_request", fake_request)
    article = client.create_article(
        ArticleCreateRequest(ticket_id=42, body="x", internal=True, time_unit=60)
    )

    assert article.id == 555
    assert "/tickets/42/time_accountings" in paths


def test_create_article_without_time_does_not_book(monkeypatch: Any) -> None:
    client = _client()
    paths: list[str] = []

    def fake_request(method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        paths.append(path)
        return {"id": 555, "ticket_id": 42, "body": "x", "type": "note", "internal": False}

    monkeypatch.setattr(client, "_request", fake_request)
    client.create_article(ArticleCreateRequest(ticket_id=42, body="x"))

    assert paths == ["/ticket_articles"]


def test_time_unit_must_be_positive() -> None:
    with pytest.raises(ValueError):
        ArticleCreateRequest(ticket_id=1, body="x", time_unit=0)


def test_get_time_accountings_tool_totals(unrestricted_controller: Any) -> None:
    with (
        patch("zammad_mcp_server.server.get_client") as mock_get_client,
        patch("zammad_mcp_server.server.get_access_controller") as mock_get_controller,
    ):
        mock_client = MagicMock()
        ticket = MagicMock()
        ticket.model_dump.return_value = {"id": 7, "group": "Support"}
        ticket.get_group_name.return_value = "Support"
        mock_client.get_ticket.return_value = ticket
        mock_client.get_time_accountings.return_value = [
            TimeAccounting(id=1, time_unit="30"),
            TimeAccounting(id=2, time_unit="15"),
        ]
        mock_get_client.return_value = mock_client
        mock_get_controller.return_value = unrestricted_controller

        from zammad_mcp_server.server import get_time_accountings

        result = get_time_accountings(7)

    assert result["count"] == 2
    assert result["total_time_unit"] == 45
