"""Victor (Member A): return-reminder notification success tests."""

from unittest.mock import patch

from app import store


def _create_rental(client, equipment_name="Snowboard"):
    renter_response = client.post(
        "/renters",
        json={"name": "Victor", "email": "victor@example.com"},
    )
    assert renter_response.status_code == 201
    renter = renter_response.get_json()

    equipment_response = client.post(
        "/equipment",
        json={
            "name": equipment_name,
            "category": "Skiing",
            "total_units": 1,
        },
    )
    assert equipment_response.status_code == 201
    equipment = equipment_response.get_json()

    rental_response = client.post(
        "/rentals",
        json={"equipment_id": equipment["id"], "renter_id": renter["id"]},
    )
    assert rental_response.status_code == 201
    return rental_response.get_json()


def test_return_reminder_stub_success_preserves_rental(client, monkeypatch):
    """Use a successful stub and verify the response and rental state."""
    rental = _create_rental(client)
    monkeypatch.setattr(
        "app.routes.rentals.send_notification",
        lambda recipient, subject, message: True,
    )

    response = client.post(f"/rentals/{rental['id']}/return-reminder")

    assert response.status_code == 200
    assert response.get_json() == {
        "rental_id": rental["id"],
        "due_date": rental["due_date"],
        "reminder_sent": True,
    }
    assert client.get("/rentals").get_json() == [rental]


def test_return_reminder_sends_expected_notification(client):
    """Use a mock to verify the recipient, subject, message, and call count."""
    rental = _create_rental(client, equipment_name="SkiBoard")

    with patch(
        "app.routes.rentals.send_notification", return_value=True
    ) as mock_send:
        response = client.post(f"/rentals/{rental['id']}/return-reminder")

    assert response.status_code == 200
    assert response.get_json()["reminder_sent"] is True
    assert client.get("/rentals").get_json() == [rental]
    mock_send.assert_called_once_with(
        "victor@example.com",
        "Return reminder for SkiBoard",
        f"Hello Victor, please return SkiBoard by {rental['due_date']}.",
    )


def test_home_page_displays_management_navigation(client):
    """The browser home page exposes links to all three management pages."""
    response = client.get("/")

    assert response.status_code == 200
    assert b"/ui/equipment" in response.data
    assert b"/ui/renters" in response.data
    assert b"/ui/rentals" in response.data


def test_equipment_browser_create_list_and_delete(client):
    """Equipment created through the browser is shown and can be removed."""
    create_response = client.post(
        "/ui/equipment",
        data={"name": "Ski Poles", "category": "Skiing", "total_units": "2"},
    )

    assert create_response.status_code == 302
    assert len(store.equipment) == 1
    equipment = next(iter(store.equipment.values()))
    assert equipment.name == "Ski Poles"
    assert equipment.category == "Skiing"
    assert equipment.available_units == 2

    page_response = client.get("/ui/equipment")
    assert page_response.status_code == 200
    assert b"Ski Poles" in page_response.data

    delete_response = client.post(f"/ui/equipment/{equipment.id}/delete")
    assert delete_response.status_code == 302
    assert store.equipment == {}


def test_renter_browser_create_list_and_delete(client):
    """A renter created through the browser is displayed and can be removed."""
    create_response = client.post(
        "/ui/renters",
        data={"name": "Victor", "email": "victor@example.com"},
    )

    assert create_response.status_code == 302
    assert len(store.renters) == 1
    renter = next(iter(store.renters.values()))
    assert renter.name == "Victor"
    assert renter.email == "victor@example.com"

    page_response = client.get("/ui/renters")
    assert page_response.status_code == 200
    assert b"Victor" in page_response.data

    delete_response = client.post(f"/ui/renters/{renter.id}/delete")
    assert delete_response.status_code == 302
    assert store.renters == {}


def test_rental_browser_checkout_and_return_updates_inventory(client):
    """The browser rental workflow consumes and then restores one unit."""
    renter = client.post(
        "/renters", json={"name": "Victor", "email": "victor@example.com"}
    ).get_json()
    equipment = client.post(
        "/equipment",
        json={"name": "SuperBoard2000", "category": "Skiing", "total_units": 2},
    ).get_json()

    checkout_response = client.post(
        "/ui/rentals",
        data={"equipment_id": str(equipment["id"]), "renter_id": str(renter["id"])},
    )

    assert checkout_response.status_code == 302
    assert len(store.rentals) == 1
    rental = next(iter(store.rentals.values()))
    assert rental.equipment_id == equipment["id"]
    assert rental.renter_id == renter["id"]
    assert store.equipment[equipment["id"]].available_units == 1

    page_response = client.get("/ui/rentals")
    assert page_response.status_code == 200
    assert f"/ui/rentals/{rental.id}/return".encode() in page_response.data

    return_response = client.post(f"/ui/rentals/{rental.id}/return")
    assert return_response.status_code == 302
    assert rental.return_date is not None
    assert store.equipment[equipment["id"]].available_units == 2


def test_missing_equipment_status_and_availability_return_not_found(client):
    """Both equipment subresources reject an unknown equipment identifier."""
    status_response = client.patch(
        "/equipment/999/status", json={"is_available": False}
    )
    availability_response = client.get("/equipment/999/availability")

    assert status_response.status_code == 404
    assert status_response.get_json() == {"error": "Equipment not found"}
    assert availability_response.status_code == 404
    assert availability_response.get_json() == {"error": "Equipment not found"}
