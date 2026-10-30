# Victor's test file for the rental service API.



# ============================================================
# EXAMPLE TESTS — READ THESE, THEN WRITE YOUR OWN
# ============================================================
# These two tests are provided as scaffolding to show you:
#   1. How to use the `client` fixture from conftest.py
#   2. Two common patterns: empty-list check and create-then-verify
#
# DO NOT count these toward your required test functions.
# Write your own tests in a separate file, e.g. tests/test_<yourname>.py
# ============================================================

""" 
Entities
Equipment: id, name, category, total_units, available_units, is_available
Renter: id, name, email, phone, membership_date
Rental: id, equipment_id, renter_id, rental_date, due_date, return_date, deposit_amount, deposit_released

| GET | /renters/<id> | Get one renter |
| PUT | /renters/<id> | Update a renter |
| DELETE | /renters/<id> | Delete a renter |
| POST | /rentals | Check out equipment (equipment_id, renter_id) |
| PUT | /rentals/<id>/return | Return rented equipment |
| GET | /rentals?renter_id=&equipment_id= | Look up rentals |

"""





"""
Sample test cases:
"""
def test_list_rentals_returns_empty_list_initially(client):
    """Rentals endpoint returns an empty list when no rentals have been made.

    This is the simplest possible test — it confirms the endpoint exists,
    responds with HTTP 200, and that the store starts clean for every test
    (thanks to the reset() call in conftest.py).
    """
    response = client.get("/rentals")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_equipment_and_check_availability(client):
    """Equipment POSTed to /equipment can have its availability queried.

    This is the create-then-verify pattern using the /availability sub-endpoint.
    You can extend this idea to test what happens to available_units after a
    checkout, or what the availability endpoint returns after equipment is
    marked out-of-service — think about whether the app behaves the way
    your requirements say it should.
    """
    payload = {
        "name": "Extension Ladder",
        "category": "Climbing",
        "total_units": 3,
    }
    create_resp = client.post("/equipment", json=payload)
    assert create_resp.status_code == 201
    equipment_id = create_resp.get_json()["id"]

    avail_resp = client.get(f"/equipment/{equipment_id}/availability")
    assert avail_resp.status_code == 200
    data = avail_resp.get_json()
    assert data["available_units"] == 3
    assert data["is_available"] is True


def test_list_rentals_returns_empty_list_initially(client):
    """Rentals endpoint returns an empty list when no rentals have been made.

    This is the simplest possible test — it confirms the endpoint exists,
    responds with HTTP 200, and that the store starts clean for every test
    (thanks to the reset() call in conftest.py).
    """
    response = client.get("/rentals")
    assert response.status_code == 200
    assert response.get_json() == []

"""
End of Sample test cases
"""


def test_V1_get_one_nonexistent_renter(client):
    # Attempt to retrieve a renter that doesn't exist
    response = client.get("/renters/9999")  # Assuming 9999 is a non-existent ID
    assert response.status_code == 404
    assert response.get_json()["error"] == "Renter not found"

def test_V2_get_one_renter(client):
    # First, create a renter
    create_resp = client.post("/renters", json={"name": "Victor", "email": "victor@test.com"})
    renter_id = create_resp.get_json()["id"]

    # Then, retrieve the renter
    response = client.get(f"/renters/{renter_id}")
    assert response.status_code == 200
    assert response.get_json()["name"] == "Victor"
    assert response.get_json()["email"] == "victor@test.com"

def test_V3_update_renter(client):
    # Create a renter first
    create_resp = client.post("/renters", json={"name": "Victor", "email": "victor@test.com"})
    renter_id = create_resp.get_json()["id"]

    # Then, update the renter
    update_resp = client.put(f"/renters/{renter_id}", json={"name": "Victor Updated", "email": "victor.updated@test.com"})
    assert update_resp.status_code == 200
    assert update_resp.get_json()["name"] == "Victor Updated"
    assert update_resp.get_json()["email"] == "victor.updated@test.com"

def test_V4_delete_renter(client):
    # Create a renter first
    create_resp = client.post("/renters", json={"name": "Victor", "email": "victor@test.com"})
    renter_id = create_resp.get_json()["id"]

    # Then, delete the renter
    delete_resp = client.delete(f"/renters/{renter_id}")
    assert delete_resp.status_code ==  204

def test_V5_delete_nonexistent_renter(client):
    # Attempt to delete a renter that doesn't exist
    response = client.delete("/renters/9999")  # Assuming 9999 is a non-existent ID
    assert response.status_code == 404
    assert response.get_json()["error"] == "Renter not found"
