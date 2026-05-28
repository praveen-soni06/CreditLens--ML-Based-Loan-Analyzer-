from datetime import datetime
import random

from app.database.db import Application, ApplicationTimelineEvent, db


TRACKING_LABELS = {
    "submitted": "Submitted",
    "email_verified": "Email Verified",
    "under_review": "Under Review",
    "ml_completed": "ML Analysis Completed",
    "manual_review": "Manual Review",
    "approved": "Approved",
    "rejected": "Rejected",
    "hold": "On Hold",
}


PUBLIC_TRACKING_STEPS = [
    ("submitted", "Submitted"),
    ("under_review", "Under Review"),
    ("ml_completed", "ML Analysis Completed"),
    ("manual_review", "Manual Review"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
]


def generate_application_ref():
    year = datetime.utcnow().strftime("%Y")
    while True:
        suffix = f"{random.randint(0, 99999999):08d}"
        candidate = f"CL-{year}-{suffix}"
        if not Application.query.filter_by(application_ref=candidate).first():
            return candidate


def add_timeline_event(application_id, event_key, title, description=None, actor_role="system", commit=False):
    event = ApplicationTimelineEvent(
        application_id=application_id,
        event_key=event_key,
        title=title,
        description=description,
        actor_role=actor_role,
        created_at=datetime.utcnow()
    )
    db.session.add(event)
    if commit:
        db.session.commit()
    return event


def set_application_status(application, status, queue=None, actor_role="system", description=None, commit=False):
    application.tracking_status = status
    if queue:
        application.review_queue = queue
    application.status_updated_at = datetime.utcnow()
    add_timeline_event(
        application_id=application.id,
        event_key=status,
        title=TRACKING_LABELS.get(status, status.replace("_", " ").title()),
        description=description,
        actor_role=actor_role
    )
    if commit:
        db.session.commit()


def get_public_timeline(application):
    event_keys = {event.event_key for event in application.timeline_events}
    current = application.tracking_status

    visible = []
    for key, label in PUBLIC_TRACKING_STEPS:
        if current in ("approved", "rejected") and key in ("approved", "rejected") and key != current:
            continue
        visible.append({
            "key": key,
            "label": label,
            "completed": key in event_keys or key == current,
            "active": key == current,
        })
    return visible
