from datetime import datetime, timezone

import pytest


def _create_payload(external_id: int, title: str = "Backend Python") -> dict:
    return {
        "title": title,
        "timetable_mode_name": "Гибкий",
        "tag_name": "backend",
        "city_name": "Санкт-Петербург",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "is_remote_available": True,
        "is_hot": False,
        "external_id": external_id,
    }


@pytest.mark.asyncio
async def test_api_create_get_update_delete_vacancy(api_client):
    create_resp = await api_client.post("/api/v1/vacancies/", json=_create_payload(9001))
    assert create_resp.status_code == 201
    vacancy_id = create_resp.json()["id"]

    get_resp = await api_client.get(f"/api/v1/vacancies/{vacancy_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["external_id"] == 9001

    update_resp = await api_client.put(
        f"/api/v1/vacancies/{vacancy_id}",
        json={"title": "Updated via API"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "Updated via API"

    delete_resp = await api_client.delete(f"/api/v1/vacancies/{vacancy_id}")
    assert delete_resp.status_code == 204

    get_after_delete = await api_client.get(f"/api/v1/vacancies/{vacancy_id}")
    assert get_after_delete.status_code == 404


@pytest.mark.asyncio
async def test_api_rejects_duplicate_external_id(api_client):
    first_resp = await api_client.post("/api/v1/vacancies/", json=_create_payload(9002))
    assert first_resp.status_code == 201

    duplicate_resp = await api_client.post(
        "/api/v1/vacancies/",
        json=_create_payload(9002, title="Duplicate"),
    )
    assert duplicate_resp.status_code == 409


@pytest.mark.asyncio
async def test_api_rejects_duplicate_external_id_on_put(api_client):
    first_resp = await api_client.post("/api/v1/vacancies/", json=_create_payload(9010))
    assert first_resp.status_code == 201

    second_resp = await api_client.post("/api/v1/vacancies/", json=_create_payload(9011))
    assert second_resp.status_code == 201
    second_id = second_resp.json()["id"]

    update_resp = await api_client.put(
        f"/api/v1/vacancies/{second_id}",
        json={"external_id": 9010},
    )
    assert update_resp.status_code == 409


@pytest.mark.asyncio
async def test_api_filters_by_city_and_timetable(api_client):
    await api_client.post("/api/v1/vacancies/", json=_create_payload(9003, title="Python Dev"))
    await api_client.post(
        "/api/v1/vacancies/",
        json={
            "title": "QA Engineer",
            "timetable_mode_name": "Fixed",
            "tag_name": "qa",
            "city_name": "Moscow",
            "published_at": datetime.now(timezone.utc).isoformat(),
            "is_remote_available": False,
            "is_hot": False,
            "external_id": 9004,
        },
    )

    filtered_resp = await api_client.get(
        "/api/v1/vacancies/",
        params={"city_name": "mos", "timetable_mode_name": "fix"},
    )
    assert filtered_resp.status_code == 200
    data = filtered_resp.json()
    assert len(data) == 1
    assert data[0]["title"] == "QA Engineer"
