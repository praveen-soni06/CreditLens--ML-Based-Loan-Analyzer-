from datetime import datetime, timedelta

from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for

from app.database.db import Application
from app.utils.email_utils import generate_verification_code, send_verification_code_email
from app.utils.lifecycle import TRACKING_LABELS

tracking_bp = Blueprint('tracking', __name__)


def mask_email(email):
    if not email or '@' not in email:
        return email or ""
    name, domain = email.split('@', 1)
    if len(name) <= 2:
        masked_name = name[:1] + "***"
    else:
        masked_name = name[:2] + "***" + name[-1:]
    return f"{masked_name}@{domain}"


def build_customer_tracking_view(application):
    current = application.tracking_status
    timeline_events = sorted(application.timeline_events, key=lambda event: event.created_at)
    steps = []
    for event in timeline_events:
        description = event.description or ""
        if event.actor_role == "credit_manager":
            description = "Status updated by the bank."
        steps.append({
            "key": event.event_key,
            "label": event.title or TRACKING_LABELS.get(event.event_key, event.event_key.replace("_", " ").title()),
            "description": description,
            "date": event.created_at,
            "completed": event.event_key != current,
            "active": event.event_key == current,
        })

    if not steps:
        steps.append({
            "key": current,
            "label": TRACKING_LABELS.get(current, current.replace("_", " ").title()),
            "description": "Status fetched from your application record.",
            "date": application.status_updated_at or application.submitted_at,
            "completed": False,
            "active": True,
        })

    if not any(step["active"] for step in steps):
        steps[-1]["active"] = True
        steps[-1]["completed"] = False

    status_tone = "success" if current == "approved" else "danger" if current == "rejected" else "warning" if current == "hold" else "info"
    latest_update = steps[-1]

    return {
        "steps": steps,
        "latest_update": latest_update,
        "status_tone": status_tone,
        "masked_email": mask_email(application.customer_email),
        "event_count": len(steps),
    }


def render_tracking_verification(application, error=None, notice=None):
    return render_template(
        'track_verify.html',
        application_ref=application.application_ref,
        customer_email=application.customer_email,
        error=error,
        notice=notice
    )


@tracking_bp.route('/track', methods=['GET', 'POST'])
def track_application():
    if request.method == 'POST':
        application_ref = request.form.get('application_ref', '').strip().upper()
        customer_email = request.form.get('customer_email', '').strip().lower()
        application = Application.query.filter_by(
            application_ref=application_ref,
            customer_email=customer_email
        ).first()

        if not application:
            return render_template('track.html', error="No application found for the provided details.")

        code = generate_verification_code()
        session['tracking_application_id'] = application.id
        session['tracking_otp'] = code
        session['tracking_otp_expires_at'] = (datetime.utcnow() + timedelta(minutes=10)).isoformat()

        send_verification_code_email(application.customer_name, application.customer_email, code)
        flash("A verification code has been sent to the registered email.", "success")
        return render_tracking_verification(
            application,
            notice="We have sent a 6-digit verification code to the registered email address."
        )

    return render_template('track.html')


@tracking_bp.route('/track/verify', methods=['POST'])
def verify_tracking_otp():
    code = request.form.get('verification_code', '').strip()
    application_id = session.get('tracking_application_id')
    expected = session.get('tracking_otp')
    expires_at = session.get('tracking_otp_expires_at')

    if not application_id or not expected or not expires_at:
        return redirect(url_for('tracking.track_application'))

    if datetime.utcnow() > datetime.fromisoformat(expires_at):
        flash("Tracking verification code has expired. Please request a new one.", "error")
        return redirect(url_for('tracking.track_application'))

    if code != expected:
        application = Application.query.get(application_id)
        if not application:
            return redirect(url_for('tracking.track_application'))
        return render_tracking_verification(application, error="Invalid verification code.")

    session['tracking_verified_application_id'] = application_id
    return redirect(url_for('tracking.tracking_status'))


@tracking_bp.route('/track/verify/api', methods=['POST'])
def verify_tracking_otp_api():
    payload = request.get_json(silent=True) or {}
    code = str(payload.get('verification_code', '')).strip()
    application_id = session.get('tracking_application_id')
    expected = session.get('tracking_otp')
    expires_at = session.get('tracking_otp_expires_at')

    if not application_id or not expected or not expires_at:
        return jsonify({
            "success": False,
            "message": "Tracking session expired. Please start tracking again.",
            "redirect_url": url_for('tracking.track_application')
        }), 400

    if datetime.utcnow() > datetime.fromisoformat(expires_at):
        return jsonify({
            "success": False,
            "message": "Tracking verification code has expired. Please request a new OTP."
        }), 400

    if code != expected:
        return jsonify({
            "success": False,
            "message": "Invalid OTP. Please check the code and try again."
        }), 400

    session['tracking_verified_application_id'] = application_id
    session.pop('tracking_otp', None)
    session.pop('tracking_otp_expires_at', None)
    return jsonify({
        "success": True,
        "message": "OTP verified successfully. Opening application status.",
        "redirect_url": url_for('tracking.tracking_status')
    })


@tracking_bp.route('/track/verify/resend', methods=['POST'])
def resend_tracking_otp_api():
    application_id = session.get('tracking_application_id')
    if not application_id:
        return jsonify({
            "success": False,
            "message": "Tracking session expired. Please start tracking again.",
            "redirect_url": url_for('tracking.track_application')
        }), 400

    application = Application.query.get(application_id)
    if not application:
        return jsonify({
            "success": False,
            "message": "Application could not be found."
        }), 404

    code = generate_verification_code()
    session['tracking_otp'] = code
    session['tracking_otp_expires_at'] = (datetime.utcnow() + timedelta(minutes=10)).isoformat()

    send_verification_code_email(application.customer_name, application.customer_email, code)
    return jsonify({
        "success": True,
        "message": "A new OTP has been sent to the registered email.",
        "cooldown_seconds": 45
    })


@tracking_bp.route('/track/status')
def tracking_status():
    application_id = session.get('tracking_verified_application_id')
    if not application_id:
        return redirect(url_for('tracking.track_application'))

    application = Application.query.get_or_404(application_id)
    tracking_view = build_customer_tracking_view(application)
    return render_template(
        'tracking_status.html',
        application=application,
        public_status=TRACKING_LABELS.get(application.tracking_status, application.tracking_status.title()),
        timeline=tracking_view["steps"],
        latest_update=tracking_view["latest_update"],
        status_tone=tracking_view["status_tone"],
        masked_email=tracking_view["masked_email"],
        event_count=tracking_view["event_count"]
    )
