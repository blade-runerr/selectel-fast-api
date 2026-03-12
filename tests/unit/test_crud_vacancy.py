from datetime import datetime, timezone

import pytest

from app.crud.vacancy import (
    create_vacancy,
    get_vacancy,
    get_vacancy_by_external_id,
    list_vacancies,
    update_vacancy,
    upsert_external_vacancies,
)
from app.schemas.vacancy import VacancyCreate, VacancyUpdate


def _vacancy_create_payload(external_id: int, title: str = "Backend Python") -> VacancyCreate:
    return VacancyCreate(
        title=title,
        timetable_mode_name="Гибкий",
        tag_name="backend",
        city_name="Санкт-Петербург",
        published_at=datetime.now(timezone.utc),
        is_remote_available=True,
        is_hot=False,
        external_id=external_id,
    )


@pytest.mark.asyncio
async def test_crud_create_and_get_vacancy(db_session):
    created = await create_vacancy(db_session, _vacancy_create_payload(1001))
    found = await get_vacancy(db_session, created.id)

    assert found is not None
    assert found.id == created.id
    assert found.external_id == 1001


@pytest.mark.asyncio
async def test_crud_update_uses_partial_payload(db_session):
    created = await create_vacancy(db_session, _vacancy_create_payload(1002))

    updated = await update_vacancy(
        db_session,
        created,
        VacancyUpdate(title="Updated", city_name=None),
    )

    assert updated.title == "Updated"
    assert updated.timetable_mode_name == "Гибкий"


@pytest.mark.asyncio
async def test_crud_list_filters(db_session):
    await create_vacancy(db_session, _vacancy_create_payload(2001, title="Python Dev"))
    await create_vacancy(
        db_session,
        VacancyCreate(
            title="QA Engineer",
            timetable_mode_name="Fixed",
            tag_name="qa",
            city_name="Moscow",
            published_at=datetime.now(timezone.utc),
            is_remote_available=False,
            is_hot=False,
            external_id=2002,
        ),
    )

    filtered = await list_vacancies(
        db_session,
        timetable_mode_name="Fix",
        city_name="mos",
    )

    assert len(filtered) == 1
    assert filtered[0].title == "QA Engineer"


@pytest.mark.asyncio
async def test_crud_upsert_creates_then_updates(db_session):
    created_count = await upsert_external_vacancies(
        db_session,
        [
            {
                "external_id": 3001,
                "title": "First",
                "timetable_mode_name": "Гибкий",
                "tag_name": "backend",
                "city_name": None,
                "published_at": datetime.now(timezone.utc),
                "is_remote_available": True,
                "is_hot": False,
            }
        ],
    )
    assert created_count == 1

    created = await get_vacancy_by_external_id(db_session, 3001)
    assert created is not None
    assert created.title == "First"

    updated_count = await upsert_external_vacancies(
        db_session,
        [
            {
                "external_id": 3001,
                "title": "First Updated",
                "timetable_mode_name": "Гибкий",
                "tag_name": "backend",
                "city_name": "Москва",
                "published_at": datetime.now(timezone.utc),
                "is_remote_available": True,
                "is_hot": True,
            }
        ],
    )
    assert updated_count == 0

    updated = await get_vacancy_by_external_id(db_session, 3001)
    assert updated is not None
    assert updated.title == "First Updated"
    assert updated.city_name == "Москва"
