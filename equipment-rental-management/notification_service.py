"""Local notification simulator for equipment-rental return reminders.

Place this file beside ``run.py``. The simulator records notifications in
memory and never contacts an email provider or makes a network request. It is
intended only for Assignment 3 stub and mock testing.
"""

SUBJECT_PREFIX = "[Equipment Rental Reminder]"

_notifications = []


def is_service_available() -> bool:
    """Return whether the local simulator is available."""
    return True


def send_notification(recipient: str, subject: str, message: str) -> bool:
    """Record a simulated equipment-rental reminder and return success.

    Invalid or blank arguments, and an unavailable simulator, return ``False``
    without recording a notification.  The name, parameters, and Boolean
    result deliberately match the Assignment 3 supplied service. A consistent
    reminder prefix is added to the stored subject.
    """
    if not all(isinstance(value, str) and value.strip()
               for value in (recipient, subject, message)):
        return False
    if not is_service_available():
        return False
    formatted_subject = subject.strip()
    if not formatted_subject.startswith(SUBJECT_PREFIX):
        formatted_subject = f"{SUBJECT_PREFIX} {formatted_subject}"

    _notifications.append({
        "recipient": recipient,
        "subject": formatted_subject,
        "message": message,
    })
    return True


def get_notifications() -> list:
    """Return copies of notifications recorded by this simulator."""
    return [notification.copy() for notification in _notifications]


def clear_notifications() -> None:
    """Clear the in-memory notification history."""
    _notifications.clear()
