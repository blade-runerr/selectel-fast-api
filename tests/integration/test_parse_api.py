import pytest

from app.api.v1 import parse as parse_api


@pytest.mark.asyncio
async def test_parse_endpoint_returns_created_count(api_client, monkeypatch):
    async def fake_parse_and_store(session):
        return 7

    monkeypatch.setattr(parse_api, "parse_and_store", fake_parse_and_store)

    response = await api_client.post("/api/v1/parse/")

    assert response.status_code == 200
    assert response.json() == {"created": 7}
