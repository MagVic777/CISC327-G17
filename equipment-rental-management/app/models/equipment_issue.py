from datetime import date


class EquipmentIssue:
    def __init__(self, id, rental_id, equipment_id, issue_type, description):
        self.id = id
        self.rental_id = rental_id
        self.equipment_id = equipment_id
        self.issue_type = issue_type
        self.description = description
        self.reported_date = date.today()

    def to_dict(self):
        return {
            "id": self.id,
            "rental_id": self.rental_id,
            "equipment_id": self.equipment_id,
            "issue_type": self.issue_type,
            "description": self.description,
            "reported_date": self.reported_date.isoformat(),
        }