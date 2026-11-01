
from datetime import date, timedelta

from flask import Blueprint, jsonify, request

from app import store
from app.models.rental import Rental
from app.models.equipment_issue import EquipmentIssue

rentals_bp = Blueprint("rentals", __name__, url_prefix="/rentals")


@rentals_bp.route("", methods=["GET"])
def list_rentals():
    results = list(store.rentals.values())

    renter_id = request.args.get("renter_id", type=int)
    equipment_id = request.args.get("equipment_id", type=int)

    if renter_id is not None:
        results = [r for r in results if r.renter_id == renter_id]

    if equipment_id is not None:
        results = [r for r in results if r.equipment_id == equipment_id]

    return jsonify([r.to_dict() for r in results])


@rentals_bp.route("", methods=["POST"])
def checkout_equipment():
    data = request.get_json()
    item = store.equipment.get(data["equipment_id"])
    if item is None:
        return jsonify({"error": "Equipment not found"}), 404

    if not item.is_available:
        return jsonify({"error": "Equipment is currently unavailable"}), 400

    if item.available_units <= 0:
        return jsonify({"error": "No available units remaining"}), 400

    # Existing checkout behaviour
    item.available_units -= 1

    rental_id = store.next_id("rental")
    rental = Rental(
        id=rental_id,
        equipment_id=data["equipment_id"],
        renter_id=data["renter_id"],
        due_date=Rental.default_due_date(),
        deposit_amount=data.get("deposit_amount", 0.0),
    )
    store.rentals[rental_id] = rental
    return jsonify(rental.to_dict()), 201


@rentals_bp.route("/<int:rental_id>/return", methods=["PUT"])
def return_equipment(rental_id):
    rental = store.rentals.get(rental_id)
    if rental is None:
        return jsonify({"error": "Rental not found"}), 404
    if rental.return_date is not None:
        return jsonify({"error": "Rental already returned"}), 400

    rental.return_date = date.today()
    item = store.equipment.get(rental.equipment_id)
    if item is not None:
        item.available_units += 1

    return jsonify(rental.to_dict())


@rentals_bp.route("/<int:rental_id>/extend", methods=["PUT"])
def extend_rental(rental_id):
    """Extend a rental's due date by the given number of days."""
    rental = store.rentals.get(rental_id)
    if rental is None:
        return jsonify({"error": "Rental not found"}), 404
    if rental.return_date is not None:
        return jsonify({"error": "Rental already returned"}), 400

    data = request.get_json()
    days = data.get("days", 1)
    rental.due_date = rental.due_date + timedelta(days=days)
    return jsonify(rental.to_dict())


@rentals_bp.route("/<int:rental_id>/deposit/release", methods=["PUT"])
def release_deposit(rental_id):
    """Release the damage deposit hold for a returned rental."""
    rental = store.rentals.get(rental_id)
    if rental is None:
        return jsonify({"error": "Rental not found"}), 404
    if rental.return_date is None:
        return jsonify({"error": "Equipment has not been returned yet"}), 400

    # Existing behaviour retained
    return jsonify({"rental_id": rental_id, "deposit_released": True})


@rentals_bp.route("/<int:rental_id>/issue", methods=["POST"])
def report_equipment_issue(rental_id):
    """Report damaged or missing equipment associated with a rental."""

    rental = store.rentals.get(rental_id)
    if rental is None:
        return jsonify({"error": "Rental not found"}), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A valid JSON request body is required"}), 400

    issue_type = data.get("issue_type")
    description = data.get("description")

    if issue_type not in ("damaged", "missing"):
        return jsonify({
            "error": "Issue type must be 'damaged' or 'missing'"
        }), 400

    if not isinstance(description, str) or not description.strip():
        return jsonify({
            "error": "A non-empty description is required"
        }), 400

    item = store.equipment.get(rental.equipment_id)
    if item is None:
        return jsonify({"error": "Equipment not found"}), 404

    issue_id = store.next_id("issue")

    issue = EquipmentIssue(
        id=issue_id,
        rental_id=rental.id,
        equipment_id=item.id,
        issue_type=issue_type,
        description=description.strip(),
    )

    store.issues[issue_id] = issue
    item.is_available = False

    return jsonify(issue.to_dict()), 201
