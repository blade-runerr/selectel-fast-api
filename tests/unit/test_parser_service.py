from datetime import datetime, timezone

import pytest

from app.schemas.external import (
    ExternalCity,
    ExternalTag,
    ExternalTimetableMode,
    ExternalVacanciesResponse,
    ExternalVacancyItem,
)
from app.services import parser as parser_service


def _response_with_nullable_city() -> ExternalVacanciesResponse:
    return ExternalVacanciesResponse(
        item_count=1,
        items=[
            ExternalVacancyItem(
                id=5001,
                title="Python Developer",
                timetable_mode=ExternalTimetableMode(id=1, name="Гибкий"),
                tag=ExternalTag(id=1, name="backend", description="Backend"),
                city=None,
                published_at=datetime.now(timezone.utc),
                is_remote_available=True,
                is_hot=False,
            )
        ],
        items_per_page=1000,
        page=1,
        page_count=1,
    )


@pytest.mark.asyncio
async def test_parse_and_store_handles_nullable_city(monkeypatch):
    async def fake_fetch_page(client, page):
        return _response_with_nullable_city()

    captured_payloads = []

    async def fake_upsert_external_vacancies(session, payloads):
        captured_payloads.extend(payloads)
        return len(payloads)

    monkeypatch.setattr(parser_service, "fetch_page", fake_fetch_page)
    monkeypatch.setattr(
        parser_service, "upsert_external_vacancies", fake_upsert_external_vacancies
    )

    created = await parser_service.parse_and_store(session=object())

    assert created == 1
    assert captured_payloads[0]["external_id"] == 5001
    assert captured_payloads[0]["city_name"] is None


@pytest.mark.asyncio
async def test_parse_and_store_returns_zero_on_fetch_error(monkeypatch):
    async def fake_fetch_page(client, page):
        raise parser_service.httpx.RequestError("network issue")

    monkeypatch.setattr(parser_service, "fetch_page", fake_fetch_page)

    created = await parser_service.parse_and_store(session=object())
    assert created == 0
