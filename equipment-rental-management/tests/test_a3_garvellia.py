"""Garvellia (Member B): Notification failure/non-trigger tests & coverage-directed tests."""

from unittest.mock import patch
from datetime import date, timedelta
from app import store
from app.models.equipment import Equipment
from app.models.renter import Renter
from app.models.rental import Rental

def _create_rental(client, equipment_name="Mountain Bike"):
    """Create equipment, renter, and rental via API endpoints (no trailing slashes)."""
    eq_res = client.post("/equipment", json={"name": equipment_name, "category": "Sports"})
    eq_id = eq_res.get_json()["id"]

    renter_res = client.post("/renters", json={"name": "Jane Doe", "email": "jane@example.com"})
    renter_id = renter_res.get_json()["id"]

    rental_res = client.post("/rentals", json={"equipment_id": eq_id, "renter_id": renter_id})
    return rental_res.get_json()["id"]


# --- 1. NOTIFICATION FAILURE & NON-TRIGGER TESTS (TASK 2.3) ---

def test_return_reminder_handles_notification_failure(client):
    """Stub: When send_notification returns False (failure), the endpoint still handles it gracefully."""
    rental_id = _create_rental(client)
    
    # Patch send_notification to simulate a failure (returning False)
    with patch("app.routes.rentals.send_notification", return_value=False) as mock_send:
        response = client.post(f"/rentals/{rental_id}/return-reminder")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["reminder_sent"] is False
        mock_send.assert_called_once()


def test_return_reminder_sent_not_called_if_already_returned(client):
    """Mock (Non-trigger path): No notification is sent if equipment has already been returned."""
    rental_id = _create_rental(client)
    
    client.put(f"/rentals/{rental_id}/return") # Return it first
    
    with patch("app.routes.rentals.send_notification") as mock_send:
        response = client.post(f"/rentals/{rental_id}/return-reminder")
        
        assert response.status_code == 400
        assert response.get_json() == {"error": "Equipment has already been returned"}
        mock_send.assert_not_called()


# --- 2. COVERAGE-DIRECTED TESTS FOR RENTALS & EQUIPMENT ISSUES (TASK 3) ---

def test_equipment_issue_model_to_dict():
    """Directly test EquipmentIssue model initialization and to_dict for coverage."""
    from app.models.equipment_issue import EquipmentIssue
    issue = EquipmentIssue(id=1, rental_id=1, equipment_id=1, issue_type="damaged", description="Flat tire")
    d = issue.to_dict()
    assert d["issue_type"] == "damaged"
    assert d["description"] == "Flat tire"


def test_extend_rental_not_found(client):
    """Test extending a non-existent rental returns 404."""
    response = client.put("/rentals/999/extend", json={"days": 5})
    assert response.status_code == 404


def test_release_deposit_not_found(client):
    """Test releasing deposit for a non-existent rental returns 404."""
    response = client.put("/rentals/999/deposit/release")
    assert response.status_code == 404