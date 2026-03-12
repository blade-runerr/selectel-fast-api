from datetime import datetime, timezone

from app.schemas.vacancy import VacancyCreate, VacancyUpdate


def test_vacancy_create_requires_required_fields():
    payload = VacancyCreate(
        title="Backend Python",
        timetable_mode_name="Гибкий",
        tag_name="backend",
        city_name="Санкт-Петербург",
        published_at=datetime.now(timezone.utc),
        is_remote_available=True,
        is_hot=False,
        external_id=101,
    )

    assert payload.title == "Backend Python"
    assert payload.external_id == 101


def test_vacancy_update_accepts_partial_payload():
    payload = VacancyUpdate(title="Updated title")

    dumped = payload.model_dump(exclude_unset=True)
    assert dumped == {"title": "Updated title"}
