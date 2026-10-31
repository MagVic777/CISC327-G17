# Assignment 2 - Part 2

# Helper function to add equipment
def create_equipment(client, name, category, total_units):
    return client.post("/equipment", json={
        "name": name,
        "category": category,
        "total_units": total_units
    })


def create_renter(client, name, email):
    return client.post("/renters", json={
        "name": name,
        "email": email
    })


# Sample outdoor equipment inventory
def equipment_inventory(client):
    equipment_list = [
        ("Family Camping Tent", "Camping", 10),
        ("Two-Person Tent", "Camping", 15),
        ("Sleeping Bag", "Camping", 25),
        ("Camping Stove", "Cooking", 8),
        ("Camping Chair", "Camping Furniture", 20),
        ("Kayak", "Water Sports", 12),
        ("Canoe", "Water Sports", 5),
        ("Life Jacket", "Safety Equipment", 20),
        ("Mountain Bike", "Cycling", 10),
        ("Bicycle Helmet", "Cycling", 15),
        ("Hiking Backpack", "Hiking", 5),
        ("Hiking Poles", "Hiking", 5)
    ]

    for name, category, quantity in equipment_list:
        create_equipment(client, name, category, quantity)


# FEATURE 1: LIST EQUIPMENT


def test_list_equipment_returns_empty_list_initially(client):
    response = client.get("/equipment")

    assert response.status_code == 200
    assert response.get_json() == []


def test_list_equipment_returns_all_created_equipment(client):
    equipment_inventory(client)

    response = client.get("/equipment")
    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 12

    equipment_names = [item["name"] for item in data]

    assert "Family Camping Tent" in equipment_names
    assert "Kayak" in equipment_names
    assert "Mountain Bike" in equipment_names
    assert "Life Jacket" in equipment_names
    assert "Hiking Backpack" in equipment_names


def test_list_equipment_returns_correct_categories(client):
    equipment_inventory(client)

    response = client.get("/equipment")
    data = response.get_json()

    categories = [item["category"] for item in data]

    assert "Camping" in categories
    assert "Water Sports" in categories
    assert "Cycling" in categories
    assert "Hiking" in categories
    assert "Safety Equipment" in categories


def test_equipment_records_have_unique_ids(client):
    equipment_inventory(client)

    response = client.get("/equipment")
    data = response.get_json()

    equipment_ids = [item["id"] for item in data]

    assert len(equipment_ids) == len(set(equipment_ids))


# FEATURE 2: ADD EQUIPMENT

def test_add_camping_equipment_successfully(client):
    response = create_equipment(
        client, "Family Camping Tent", "Camping", 10
    )

    data = response.get_json()

    assert response.status_code == 201
    assert data["name"] == "Family Camping Tent"
    assert data["category"] == "Camping"
    assert data["total_units"] == 10
    assert data["available_units"] == 10
    assert data["is_available"] is True


def test_add_different_types_of_outdoor_equipment(client):
    equipment = [
        ("Kayak", "Water Sports", 4),
        ("Mountain Bike", "Cycling", 6),
        ("Sleeping Bag", "Camping", 12),
        ("Hiking Backpack", "Hiking", 8)
    ]

    for name, category, quantity in equipment:
        response = create_equipment(
            client, name, category, quantity
        )

        assert response.status_code == 201

        data = response.get_json()
        assert data["name"] == name
        assert data["category"] == category
        assert data["total_units"] == quantity


def test_add_equipment_uses_default_quantity(client):
    response = client.post("/equipment", json={
        "name": "Camping Lantern",
        "category": "Camping"
    })

    data = response.get_json()

    assert response.status_code == 201
    assert data["total_units"] == 1
    assert data["available_units"] == 1


def test_inventory_can_represent_approximately_150_units(client):
    equipment_inventory(client)

    response = client.get("/equipment")
    data = response.get_json()

    total_inventory = sum(
        item["total_units"] for item in data
    )

    assert response.status_code == 200
    assert total_inventory == 150


# FEATURE 3: VIEW EQUIPMENT DETAILS

def test_view_equipment_returns_correct_details(client):
    create_response = create_equipment(
        client, "Single-Person Kayak", "Water Sports", 5
    )

    equipment_id = create_response.get_json()["id"]

    response = client.get(f"/equipment/{equipment_id}")
    data = response.get_json()

    assert response.status_code == 200
    assert data["id"] == equipment_id
    assert data["name"] == "Single-Person Kayak"
    assert data["category"] == "Water Sports"
    assert data["total_units"] == 5
    assert data["available_units"] == 5
    assert data["is_available"] is True


def test_view_nonexistent_equipment_returns_404(client):
    response = client.get("/equipment/999")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Equipment not found"


def test_view_equipment_shows_correct_availability(client):
    create_response = create_equipment(
        client, "Mountain Bike", "Cycling", 8
    )

    equipment_id = create_response.get_json()["id"]

    # Mark the equipment as unavailable
    client.put(f"/equipment/{equipment_id}", json={
        "is_available": False
    })

    response = client.get(f"/equipment/{equipment_id}")
    data = response.get_json()

    assert response.status_code == 200
    assert data["is_available"] is False


# FEATURE 4: UPDATE EQUIPMENT

def test_update_equipment_details(client):
    create_response = create_equipment(
        client, "Old Camping Tent", "Camping", 5
    )

    equipment_id = create_response.get_json()["id"]

    response = client.put(f"/equipment/{equipment_id}", json={
        "name": "Large Family Tent",
        "category": "Camping",
        "total_units": 8,
        "available_units": 8
    })

    data = response.get_json()

    assert response.status_code == 200
    assert data["id"] == equipment_id
    assert data["name"] == "Large Family Tent"
    assert data["category"] == "Camping"
    assert data["total_units"] == 8
    assert data["available_units"] == 8

    # Confirm that changes were saved
    get_response = client.get(f"/equipment/{equipment_id}")

    assert get_response.get_json()["name"] == "Large Family Tent"


def test_update_equipment_availability_status(client):
    create_response = create_equipment(
        client, "Kayak", "Water Sports", 4
    )

    equipment_id = create_response.get_json()["id"]

    response = client.put(f"/equipment/{equipment_id}", json={
        "is_available": False
    })

    data = response.get_json()

    assert response.status_code == 200
    assert data["is_available"] is False


def test_update_equipment_preserves_fields_not_changed(client):
    create_response = create_equipment(
        client, "Hiking Backpack", "Hiking", 10
    )

    equipment_id = create_response.get_json()["id"]

    response = client.put(f"/equipment/{equipment_id}", json={
        "name": "Large Hiking Backpack"
    })

    data = response.get_json()

    assert response.status_code == 200
    assert data["name"] == "Large Hiking Backpack"
    assert data["category"] == "Hiking"
    assert data["total_units"] == 10
    assert data["available_units"] == 10


def test_update_nonexistent_equipment_returns_404(client):
    response = client.put("/equipment/999", json={
        "name": "Updated Kayak"
    })

    assert response.status_code == 404
    assert response.get_json()["error"] == "Equipment not found"



# FEATURE 5: DELETE EQUIPMENT

def test_delete_equipment_removes_it_from_inventory(client):
    create_response = create_equipment(
        client, "Old Camping Stove", "Cooking", 3
    )

    equipment_id = create_response.get_json()["id"]

    response = client.delete(f"/equipment/{equipment_id}")

    assert response.status_code == 204

    # Confirm equipment no longer exists
    get_response = client.get(f"/equipment/{equipment_id}")

    assert get_response.status_code == 404
    assert get_response.get_json()["error"] == "Equipment not found"


def test_delete_equipment_does_not_remove_other_equipment(client):
    create_equipment(client, "Kayak", "Water Sports", 4)

    second_response = create_equipment(
        client, "Mountain Bike", "Cycling", 6
    )

    second_id = second_response.get_json()["id"]

    # Delete the first equipment item
    client.delete("/equipment/1")

    response = client.get(f"/equipment/{second_id}")
    data = response.get_json()

    assert response.status_code == 200
    assert data["name"] == "Mountain Bike"


def test_delete_nonexistent_equipment_returns_404(client):
    response = client.delete("/equipment/999")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Equipment not found"


# FEATURE 6: LIST RENTERS

def test_list_renters_returns_empty_list_initially(client):
    response = client.get("/renters")

    assert response.status_code == 200
    assert response.get_json() == []


def test_list_renters_returns_all_created_renters(client):
    create_renter(client, "Jane Smith", "jane@example.com")
    create_renter(client, "John Brown", "john@example.com")
    create_renter(client, "Alex Green", "alex@example.com")

    response = client.get("/renters")
    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 3

    names = [renter["name"] for renter in data]

    assert "Jane Smith" in names
    assert "John Brown" in names
    assert "Alex Green" in names


def test_list_renters_returns_correct_email_information(client):
    create_renter(
        client, "Jane Smith", "jane@example.com"
    )

    response = client.get("/renters")
    data = response.get_json()

    assert response.status_code == 200
    assert data[0]["email"] == "jane@example.com"


# FEATURE 7: CREATE RENTERS

def test_create_renter_successfully(client):
    response = create_renter(
        client, "Jane Smith", "jane@example.com"
    )

    data = response.get_json()

    assert response.status_code == 201
    assert data["name"] == "Jane Smith"
    assert data["email"] == "jane@example.com"
    assert "id" in data


def test_create_multiple_renters_with_unique_ids(client):
    renter1 = create_renter(
        client, "Jane Smith", "jane@example.com"
    )

    renter2 = create_renter(
        client, "John Brown", "john@example.com"
    )

    assert renter1.status_code == 201
    assert renter2.status_code == 201

    id1 = renter1.get_json()["id"]
    id2 = renter2.get_json()["id"]

    assert id1 != id2


def test_created_renter_appears_in_renter_list(client):
    create_response = create_renter(
        client, "Jane Smith", "jane@example.com"
    )

    renter_id = create_response.get_json()["id"]

    response = client.get("/renters")
    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["id"] == renter_id
    assert data[0]["name"] == "Jane Smith"
    assert data[0]["email"] == "jane@example.com"
