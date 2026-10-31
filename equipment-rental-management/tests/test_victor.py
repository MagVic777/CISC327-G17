# Victor's test file for the rental service API.

"""
Entities
Equipment: id, name, category, total_units, available_units, is_available
Renter: id, name, email, phone, membership_date
Rental: id, equipment_id, renter_id, rental_date, due_date, return_date,
        deposit_amount, deposit_released

Assigned operations:
GET /renters/<id> - Get one renter
PUT /renters/<id> - Update a renter
DELETE /renters/<id> - Delete a renter
POST /rentals - Check out equipment
PUT /rentals/<id>/return - Return rented equipment
GET /rentals?renter_id=&equipment_id= - Look up rentals

The client fixture clears stored data before each test.
Failed assertions can reveal application defects; they are not hidden.
"""
from datetime import date, timedelta


# ============================================================
# Get one Renter
# ============================================================

def test_V1_get_one_nonexistent_renter(client):
    # Attempt to retrieve a renter that does not exist
    response = client.get("/renters/9999")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Renter not found"


def test_V2_get_one_renter(client):
    # First, create a renter
    create_resp = client.post("/renters", json={"name": "Victor", "email": "victor@test.com"})
    assert create_resp.status_code == 201
    renter_id = create_resp.get_json()["id"]

    # Then, retrieve the renter and check their saved details
    response = client.get(f"/renters/{renter_id}")
    assert response.status_code == 200
    assert response.get_json()["id"] == renter_id
    assert response.get_json()["name"] == "Victor"
    assert response.get_json()["email"] == "victor@test.com"
    assert response.get_json()["membership_date"] == date.today().isoformat()


# ============================================================
# Update a renter
# ============================================================


def test_V3_update_renter(client):
    # First, create a renter
    create_resp = client.post("/renters", json={"name": "Victor", "email": "victor@test.com"})
    assert create_resp.status_code == 201
    renter_id = create_resp.get_json()["id"]

    # Then, update the renter
    update_resp = client.put(f"/renters/{renter_id}", json={"name": "Victor Updated", "email": "victor.updated@test.com"})
    assert update_resp.status_code == 200
    assert update_resp.get_json()["name"] == "Victor Updated"
    assert update_resp.get_json()["email"] == "victor.updated@test.com"

    # Retrieve the renter again to confirm the changes were saved
    response = client.get(f"/renters/{renter_id}")
    assert response.status_code == 200
    assert response.get_json() == {**create_resp.get_json(), "name": "Victor Updated", "email": "victor.updated@test.com"}


def test_V7_update_renter_name_only(client):
    # First, create a renter
    create_resp = client.post("/renters", json={"name": "Victor", "email": "victor@test.com"})
    assert create_resp.status_code == 201
    renter_id = create_resp.get_json()["id"]

    # Update only the supplied fields
    update_resp = client.put(f"/renters/{renter_id}", json={'name': 'Victor Updated'})
    assert update_resp.status_code == 200

    # Check that omitted fields were preserved and changes were saved
    expected = create_resp.get_json()
    expected.update({'name': 'Victor Updated'})
    assert update_resp.get_json() == expected
    assert client.get(f"/renters/{renter_id}").get_json() == expected


def test_V8_update_renter_email_only(client):
    # First, create a renter
    create_resp = client.post("/renters", json={"name": "Victor", "email": "victor@test.com"})
    assert create_resp.status_code == 201
    renter_id = create_resp.get_json()["id"]

    # Update only the supplied fields
    update_resp = client.put(f"/renters/{renter_id}", json={'email': 'victor.updated@test.com'})
    assert update_resp.status_code == 200

    # Check that omitted fields were preserved and changes were saved
    expected = create_resp.get_json()
    expected.update({'email': 'victor.updated@test.com'})
    assert update_resp.get_json() == expected
    assert client.get(f"/renters/{renter_id}").get_json() == expected


def test_V9_update_renter_with_no_changes(client):
    # First, create a renter
    create_resp = client.post("/renters", json={"name": "Victor", "email": "victor@test.com"})
    assert create_resp.status_code == 201
    renter_id = create_resp.get_json()["id"]

    # Update only the supplied fields
    update_resp = client.put(f"/renters/{renter_id}", json={})
    assert update_resp.status_code == 200

    # Check that omitted fields were preserved and changes were saved
    expected = create_resp.get_json()
    expected.update({})
    assert update_resp.get_json() == expected
    assert client.get(f"/renters/{renter_id}").get_json() == expected


def test_V10_update_nonexistent_renter(client):
    # First, create a renter
    create_resp = client.post("/renters", json={"name": "Victor", "email": "victor@test.com"})
    assert create_resp.status_code == 201
    renter_id = create_resp.get_json()["id"]

    # Attempt to update an unknown renter without changing an existing record
    response = client.put("/renters/9999", json={"name": "Changed"})
    assert response.status_code == 404
    assert response.get_json()["error"] == "Renter not found"
    assert client.get(f"/renters/{renter_id}").get_json() == create_resp.get_json()

# ============================================================
# Delete a renter
# ============================================================

def test_V4_delete_renter(client):
    # First, create a renter
    create_resp = client.post("/renters", json={"name": "Victor", "email": "victor@test.com"})
    assert create_resp.status_code == 201
    renter_id = create_resp.get_json()["id"]

    # Then, delete the renter
    delete_resp = client.delete(f"/renters/{renter_id}")
    assert delete_resp.status_code == 204
    assert delete_resp.data == b""

    # Confirm the renter can no longer be retrieved
    response = client.get(f"/renters/{renter_id}")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Renter not found"


def test_V5_delete_nonexistent_renter(client):
    # First, create a renter
    create_resp = client.post("/renters", json={"name": "Victor", "email": "victor@test.com"})
    assert create_resp.status_code == 201
    renter_id = create_resp.get_json()["id"]

    # Attempt to delete a renter that does not exist
    response = client.delete("/renters/9999")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Renter not found"

    # Confirm the existing renter was not affected
    assert client.get(f"/renters/{renter_id}").get_json() == create_resp.get_json()



def test_V11_delete_one_renter_preserves_another(client):
    # First, create a renter
    create_resp = client.post("/renters", json={"name": "Victor", "email": "victor@test.com"})
    assert create_resp.status_code == 201
    renter_id = create_resp.get_json()["id"]

    # Create another renter who should remain unchanged
    second_resp = client.post("/renters", json={"name": "Alex", "email": "alex@test.com"})
    assert second_resp.status_code == 201
    second_id = second_resp.get_json()["id"]

    # Delete only Victor and confirm Alex remains
    assert client.delete(f"/renters/{renter_id}").status_code == 204
    assert client.get(f"/renters/{renter_id}").status_code == 404
    assert client.get(f"/renters/{second_id}").get_json() == second_resp.get_json()
    assert client.get("/renters").get_json() == [second_resp.get_json()]


def test_V12_delete_renter_twice(client):
    # First, create a renter
    create_resp = client.post("/renters", json={"name": "Victor", "email": "victor@test.com"})
    assert create_resp.status_code == 201
    renter_id = create_resp.get_json()["id"]

    # Delete the renter, then attempt the same deletion again
    assert client.delete(f"/renters/{renter_id}").status_code == 204
    response = client.delete(f"/renters/{renter_id}")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Renter not found"
    assert client.get("/renters").get_json() == []





# ============================================================
# Check out equipment
# ============================================================

def test_V6_check_out_equipment(client):
    # First, create a renter
    create_resp = client.post("/renters", json={"name": "Victor", "email": "victor@test.com"})
    assert create_resp.status_code == 201
    renter_id = create_resp.get_json()["id"]

    # Create equipment with one available unit
    equipment_resp = client.post("/equipment", json={"name": "SkiBoard2000", "category": "Winter Sports", "total_units": 1, "is_available": True})
    assert equipment_resp.status_code == 201
    equipment_id = equipment_resp.get_json()["id"]

    # Then, check out the equipment
    checkout_resp = client.post("/rentals", json={"renter_id": renter_id, "equipment_id": equipment_id})
    assert checkout_resp.status_code == 201
    rental_id = checkout_resp.get_json()["id"]

    # Check the rental details and saved record
    assert checkout_resp.get_json()["renter_id"] == renter_id
    assert checkout_resp.get_json()["equipment_id"] == equipment_id
    assert checkout_resp.get_json()["rental_date"] == date.today().isoformat()
    assert checkout_resp.get_json()["due_date"] == (date.today() + timedelta(days=7)).isoformat()
    assert checkout_resp.get_json()["return_date"] is None
    assert client.get("/rentals").get_json() == [checkout_resp.get_json()]

    # Confirm checkout reduced the available units
    response = client.get(f"/equipment/{equipment_id}")
    assert response.get_json()["available_units"] == 0
    assert response.get_json()["total_units"] == 1




def test_V13_check_out_nonexistent_equipment(client):
    # First, create a renter
    create_resp = client.post("/renters", json={"name": "Victor", "email": "victor@test.com"})
    assert create_resp.status_code == 201
    renter_id = create_resp.get_json()["id"]
    # Create equipment with one available unit
    equipment_resp = client.post("/equipment", json={"name": "SkiBoard2000", "category": "Winter Sports", "total_units": 1, "is_available": True})
    assert equipment_resp.status_code == 201
    equipment_id = equipment_resp.get_json()["id"]

    # Attempt to check out unknown equipment
    response = client.post("/rentals", json={"renter_id": renter_id, "equipment_id": 9999})
    assert response.status_code == 404
    assert response.get_json()["error"] == "Equipment not found"
    assert client.get("/rentals").get_json() == []
    assert client.get(f"/equipment/{equipment_id}").get_json() == equipment_resp.get_json()


def test_V14_check_out_unavailable_equipment(client):
    # First, create a renter
    create_resp = client.post("/renters", json={"name": "Victor", "email": "victor@test.com"})
    assert create_resp.status_code == 201
    renter_id = create_resp.get_json()["id"]
    # Create equipment with one available unit
    equipment_resp = client.post("/equipment", json={"name": "SkiBoard2000", "category": "Winter Sports", "total_units": 1, "is_available": True})
    assert equipment_resp.status_code == 201
    equipment_id = equipment_resp.get_json()["id"]

    # Mark the equipment out of service before attempting checkout
    status_resp = client.patch(f"/equipment/{equipment_id}/status", json={"is_available": False})
    assert status_resp.status_code == 200
    response = client.post("/rentals", json={"renter_id": renter_id, "equipment_id": equipment_id})
    assert response.status_code == 400

    # A rejected checkout must not change stock or create a rental
    assert client.get(f"/equipment/{equipment_id}").get_json() == status_resp.get_json()
    assert client.get("/rentals").get_json() == []


def test_V15_check_out_equipment_with_no_units_remaining(client):
    # First, create a renter
    create_resp = client.post("/renters", json={"name": "Victor", "email": "victor@test.com"})
    assert create_resp.status_code == 201
    renter_id = create_resp.get_json()["id"]

    # Create equipment with one available unit
    equipment_resp = client.post("/equipment", json={"name": "SkiBoard2000", "category": "Winter Sports", "total_units": 1, "is_available": True})
    assert equipment_resp.status_code == 201
    equipment_id = equipment_resp.get_json()["id"]

    # Then, check out the equipment
    checkout_resp = client.post("/rentals", json={"renter_id": renter_id, "equipment_id": equipment_id})
    assert checkout_resp.status_code == 201
    rental_id = checkout_resp.get_json()["id"]

    # The first checkout used the last unit; try checking it out again
    assert client.get(f"/equipment/{equipment_id}").get_json()["available_units"] == 0
    response = client.post("/rentals", json={"renter_id": renter_id, "equipment_id": equipment_id})
    assert response.status_code == 400
    assert client.get(f"/equipment/{equipment_id}").get_json()["available_units"] == 0
    assert client.get("/rentals").get_json() == [checkout_resp.get_json()]


# =============================================================
# Return rented equipment
# =============================================================

def test_V16_return_equipment(client):
    # First, create a renter
    create_resp = client.post("/renters", json={"name": "Victor", "email": "victor@test.com"})
    assert create_resp.status_code == 201
    renter_id = create_resp.get_json()["id"]

    # Create equipment with one available unit
    equipment_resp = client.post("/equipment", json={"name": "SkiBoard2000", "category": "Winter Sports", "total_units": 1, "is_available": True})
    assert equipment_resp.status_code == 201
    equipment_id = equipment_resp.get_json()["id"]

    # Then, check out the equipment
    checkout_resp = client.post("/rentals", json={"renter_id": renter_id, "equipment_id": equipment_id})
    assert checkout_resp.status_code == 201
    rental_id = checkout_resp.get_json()["id"]

    # Return the equipment
    return_resp = client.put(f"/rentals/{rental_id}/return")
    assert return_resp.status_code == 200

    # Confirm the return date was saved and stock was restored
    expected = checkout_resp.get_json()
    expected["return_date"] = date.today().isoformat()
    assert return_resp.get_json() == expected
    assert client.get("/rentals").get_json() == [expected]
    assert client.get(f"/equipment/{equipment_id}").get_json()["available_units"] == 1

    # Confirm the returned equipment can be rented again
    response = client.post("/rentals", json={"renter_id": renter_id, "equipment_id": equipment_id})
    assert response.status_code == 201
    assert response.get_json()["id"] != rental_id
    assert response.get_json()["return_date"] is None
    assert client.get(f"/equipment/{equipment_id}").get_json()["available_units"] == 0


def test_V17_return_equipment_twice(client):
    # First, create a renter
    create_resp = client.post("/renters", json={"name": "Victor", "email": "victor@test.com"})
    assert create_resp.status_code == 201
    renter_id = create_resp.get_json()["id"]

    # Create equipment with one available unit
    equipment_resp = client.post("/equipment", json={"name": "SkiBoard2000", "category": "Winter Sports", "total_units": 1, "is_available": True})
    assert equipment_resp.status_code == 201
    equipment_id = equipment_resp.get_json()["id"]

    # Then, check out the equipment
    checkout_resp = client.post("/rentals", json={"renter_id": renter_id, "equipment_id": equipment_id})
    assert checkout_resp.status_code == 201
    rental_id = checkout_resp.get_json()["id"]

    # Return the equipment
    return_resp = client.put(f"/rentals/{rental_id}/return")
    assert return_resp.status_code == 200

    # Attempt to return the same rental again
    response = client.put(f"/rentals/{rental_id}/return")
    assert response.status_code == 400
    assert response.get_json()["error"] == "Rental already returned"
    assert client.get(f"/equipment/{equipment_id}").get_json()["available_units"] == 1
    assert client.get("/rentals").get_json() == [return_resp.get_json()]


def test_V18_return_nonexistent_rental(client):
    # Create equipment with one available unit
    equipment_resp = client.post("/equipment", json={"name": "SkiBoard2000", "category": "Winter Sports", "total_units": 1, "is_available": True})
    assert equipment_resp.status_code == 201
    equipment_id = equipment_resp.get_json()["id"]

    # Attempt to return a rental that does not exist
    response = client.put("/rentals/9999/return")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Rental not found"
    assert client.get(f"/equipment/{equipment_id}").get_json() == equipment_resp.get_json()
    assert client.get("/rentals").get_json() == []


# =============================================================
# Look up rentals
# ==============================================================


def test_V19_look_up_rentals_when_empty(client):
    # No rentals have been created
    response = client.get("/rentals")
    assert response.status_code == 200
    assert response.get_json() == []


def test_V20_look_up_all_rentals(client):
    # First, create a renter
    create_resp = client.post("/renters", json={"name": "Victor", "email": "victor@test.com"})
    assert create_resp.status_code == 201
    renter_id = create_resp.get_json()["id"]

    # Create another renter and two separate equipment records
    second_renter_resp = client.post("/renters", json={"name": "Alex", "email": "alex@test.com"})
    assert second_renter_resp.status_code == 201
    second_renter_id = second_renter_resp.get_json()["id"]
    # Create equipment with one available unit
    equipment_resp = client.post("/equipment", json={"name": "SkiBoard2000", "category": "Winter Sports", "total_units": 1, "is_available": True})
    assert equipment_resp.status_code == 201
    equipment_id = equipment_resp.get_json()["id"]

    second_equipment_resp = client.post("/equipment", json={"name": "Ski", "category": "Winter Sports", "total_units": 1})
    assert second_equipment_resp.status_code == 201
    second_equipment_id = second_equipment_resp.get_json()["id"]

    # Use different renter and equipment IDs to expose incorrect filtering
    first_checkout = client.post("/rentals", json={"renter_id": renter_id, "equipment_id": second_equipment_id})
    second_checkout = client.post("/rentals", json={"renter_id": second_renter_id, "equipment_id": equipment_id})
    assert first_checkout.status_code == 201
    assert second_checkout.status_code == 201
    first_rental = first_checkout.get_json()
    second_rental = second_checkout.get_json()

    # Retrieve both rentals without applying a filter
    response = client.get("/rentals")
    assert response.status_code == 200
    assert response.get_json() == [first_rental, second_rental]


def test_V21_look_up_rentals_by_equipment_id(client):
    # First, create a renter
    create_resp = client.post("/renters", json={"name": "Victor", "email": "victor@test.com"})
    assert create_resp.status_code == 201
    renter_id = create_resp.get_json()["id"]

    # Create another renter and two separate equipment records
    second_renter_resp = client.post("/renters", json={"name": "Alex", "email": "alex@test.com"})
    assert second_renter_resp.status_code == 201
    second_renter_id = second_renter_resp.get_json()["id"]
    # Create equipment with one available unit
    equipment_resp = client.post("/equipment", json={"name": "SkiBoard2000", "category": "Winter Sports", "total_units": 1, "is_available": True})
    assert equipment_resp.status_code == 201
    equipment_id = equipment_resp.get_json()["id"]

    second_equipment_resp = client.post("/equipment", json={"name": "Ski", "category": "Winter Sports", "total_units": 1})
    assert second_equipment_resp.status_code == 201
    second_equipment_id = second_equipment_resp.get_json()["id"]

    # Use different renter and equipment IDs to expose incorrect filtering
    first_checkout = client.post("/rentals", json={"renter_id": renter_id, "equipment_id": second_equipment_id})
    second_checkout = client.post("/rentals", json={"renter_id": second_renter_id, "equipment_id": equipment_id})
    assert first_checkout.status_code == 201
    assert second_checkout.status_code == 201
    first_rental = first_checkout.get_json()
    second_rental = second_checkout.get_json()

    # Filter for the first rental's equipment_id
    response = client.get("/rentals", query_string={"equipment_id": first_rental["equipment_id"]})
    assert response.status_code == 200
    assert response.get_json() == [first_rental]


def test_V22_look_up_rentals_by_renter_id(client):
    # First, create a renter
    create_resp = client.post("/renters", json={"name": "Victor", "email": "victor@test.com"})
    assert create_resp.status_code == 201
    renter_id = create_resp.get_json()["id"]

    # Create another renter and two separate equipment records
    second_renter_resp = client.post("/renters", json={"name": "Alex", "email": "alex@test.com"})
    assert second_renter_resp.status_code == 201
    second_renter_id = second_renter_resp.get_json()["id"]
    # Create equipment with one available unit
    equipment_resp = client.post("/equipment", json={"name": "SkiBoard2000", "category": "Winter Sports", "total_units": 1, "is_available": True})
    assert equipment_resp.status_code == 201
    equipment_id = equipment_resp.get_json()["id"]

    second_equipment_resp = client.post("/equipment", json={"name": "Ski", "category": "Winter Sports", "total_units": 1})
    assert second_equipment_resp.status_code == 201
    second_equipment_id = second_equipment_resp.get_json()["id"]

    # Use different renter and equipment IDs to expose incorrect filtering
    first_checkout = client.post("/rentals", json={"renter_id": renter_id, "equipment_id": second_equipment_id})
    second_checkout = client.post("/rentals", json={"renter_id": second_renter_id, "equipment_id": equipment_id})
    assert first_checkout.status_code == 201
    assert second_checkout.status_code == 201
    first_rental = first_checkout.get_json()
    second_rental = second_checkout.get_json()

    # Filter for the first rental's renter_id
    response = client.get("/rentals", query_string={"renter_id": first_rental["renter_id"]})
    assert response.status_code == 200
    assert response.get_json() == [first_rental]


def test_V23_look_up_rentals_with_both_matching_ids(client):
    # First, create a renter
    create_resp = client.post("/renters", json={"name": "Victor", "email": "victor@test.com"})
    assert create_resp.status_code == 201
    renter_id = create_resp.get_json()["id"]

    # Create another renter and two separate equipment records
    second_renter_resp = client.post("/renters", json={"name": "Alex", "email": "alex@test.com"})
    assert second_renter_resp.status_code == 201
    second_renter_id = second_renter_resp.get_json()["id"]
    # Create equipment with one available unit
    equipment_resp = client.post("/equipment", json={"name": "SkiBoard2000", "category": "Winter Sports", "total_units": 1, "is_available": True})
    assert equipment_resp.status_code == 201
    equipment_id = equipment_resp.get_json()["id"]

    second_equipment_resp = client.post("/equipment", json={"name": "Ski", "category": "Winter Sports", "total_units": 1})
    assert second_equipment_resp.status_code == 201
    second_equipment_id = second_equipment_resp.get_json()["id"]

    # Use different renter and equipment IDs to expose incorrect filtering
    first_checkout = client.post("/rentals", json={"renter_id": renter_id, "equipment_id": second_equipment_id})
    second_checkout = client.post("/rentals", json={"renter_id": second_renter_id, "equipment_id": equipment_id})
    assert first_checkout.status_code == 201
    assert second_checkout.status_code == 201
    first_rental = first_checkout.get_json()
    second_rental = second_checkout.get_json()

    # Both filters should identify the same rental
    response = client.get("/rentals", query_string={"renter_id": renter_id, "equipment_id": second_equipment_id})
    assert response.status_code == 200
    assert response.get_json() == [first_rental]


def test_V24_look_up_rentals_with_mismatched_ids(client):
    # First, create a renter
    create_resp = client.post("/renters", json={"name": "Victor", "email": "victor@test.com"})
    assert create_resp.status_code == 201
    renter_id = create_resp.get_json()["id"]

    # Create another renter and two separate equipment records
    second_renter_resp = client.post("/renters", json={"name": "Alex", "email": "alex@test.com"})
    assert second_renter_resp.status_code == 201
    second_renter_id = second_renter_resp.get_json()["id"]
    # Create equipment with one available unit
    equipment_resp = client.post("/equipment", json={"name": "SkiBoard2000", "category": "Winter Sports", "total_units": 1, "is_available": True})
    assert equipment_resp.status_code == 201
    equipment_id = equipment_resp.get_json()["id"]

    second_equipment_resp = client.post("/equipment", json={"name": "Ski", "category": "Winter Sports", "total_units": 1})
    assert second_equipment_resp.status_code == 201
    second_equipment_id = second_equipment_resp.get_json()["id"]

    # Use different renter and equipment IDs to expose incorrect filtering
    first_checkout = client.post("/rentals", json={"renter_id": renter_id, "equipment_id": second_equipment_id})
    second_checkout = client.post("/rentals", json={"renter_id": second_renter_id, "equipment_id": equipment_id})
    assert first_checkout.status_code == 201
    assert second_checkout.status_code == 201
    first_rental = first_checkout.get_json()
    second_rental = second_checkout.get_json()

    # This renter did not rent this equipment, so the result should be empty
    response = client.get("/rentals", query_string={"renter_id": renter_id, "equipment_id": equipment_id})
    assert response.status_code == 200
    assert response.get_json() == []


def test_V25_look_up_rentals_with_nonexistent_equipment_id(client):
    # First, create a renter
    create_resp = client.post("/renters", json={"name": "Victor", "email": "victor@test.com"})
    assert create_resp.status_code == 201
    renter_id = create_resp.get_json()["id"]

    # Create another renter and two separate equipment records
    second_renter_resp = client.post("/renters", json={"name": "Alex", "email": "alex@test.com"})
    assert second_renter_resp.status_code == 201
    second_renter_id = second_renter_resp.get_json()["id"]
    # Create equipment with one available unit
    equipment_resp = client.post("/equipment", json={"name": "SkiBoard2000", "category": "Winter Sports", "total_units": 1, "is_available": True})
    assert equipment_resp.status_code == 201
    equipment_id = equipment_resp.get_json()["id"]

    second_equipment_resp = client.post("/equipment", json={"name": "Ski", "category": "Winter Sports", "total_units": 1})
    assert second_equipment_resp.status_code == 201
    second_equipment_id = second_equipment_resp.get_json()["id"]

    # Use different renter and equipment IDs to expose incorrect filtering
    first_checkout = client.post("/rentals", json={"renter_id": renter_id, "equipment_id": second_equipment_id})
    second_checkout = client.post("/rentals", json={"renter_id": second_renter_id, "equipment_id": equipment_id})
    assert first_checkout.status_code == 201
    assert second_checkout.status_code == 201
    first_rental = first_checkout.get_json()
    second_rental = second_checkout.get_json()

    # Unknown filter IDs should return no results without changing stored rentals
    response = client.get("/rentals", query_string={"equipment_id": 9999})
    assert response.status_code == 200
    assert response.get_json() == []
    assert client.get("/rentals").get_json() == [first_rental, second_rental]


def test_V26_look_up_rentals_with_nonexistent_renter_id(client):
    # First, create a renter
    create_resp = client.post("/renters", json={"name": "Victor", "email": "victor@test.com"})
    assert create_resp.status_code == 201
    renter_id = create_resp.get_json()["id"]

    # Create another renter and two separate equipment records
    second_renter_resp = client.post("/renters", json={"name": "Alex", "email": "alex@test.com"})
    assert second_renter_resp.status_code == 201
    second_renter_id = second_renter_resp.get_json()["id"]
    # Create equipment with one available unit
    equipment_resp = client.post("/equipment", json={"name": "SkiBoard2000", "category": "Winter Sports", "total_units": 1, "is_available": True})
    assert equipment_resp.status_code == 201
    equipment_id = equipment_resp.get_json()["id"]

    second_equipment_resp = client.post("/equipment", json={"name": "Ski", "category": "Winter Sports", "total_units": 1})
    assert second_equipment_resp.status_code == 201
    second_equipment_id = second_equipment_resp.get_json()["id"]

    # Use different renter and equipment IDs to expose incorrect filtering
    first_checkout = client.post("/rentals", json={"renter_id": renter_id, "equipment_id": second_equipment_id})
    second_checkout = client.post("/rentals", json={"renter_id": second_renter_id, "equipment_id": equipment_id})
    assert first_checkout.status_code == 201
    assert second_checkout.status_code == 201
    first_rental = first_checkout.get_json()
    second_rental = second_checkout.get_json()

    # Unknown filter IDs should return no results without changing stored rentals
    response = client.get("/rentals", query_string={"renter_id": 9999})
    assert response.status_code == 200
    assert response.get_json() == []
    assert client.get("/rentals").get_json() == [first_rental, second_rental]

