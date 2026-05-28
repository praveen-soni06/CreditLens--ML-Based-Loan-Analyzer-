import smtplib
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from pathlib import Path
from flask import current_app, render_template
import secrets
import string
from datetime import datetime


def generate_verification_code(length=6):
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def is_smtp_configured():
    return bool(
        current_app.config.get('EMAIL_HOST')
        and current_app.config.get('EMAIL_HOST_USER')
        and current_app.config.get('EMAIL_HOST_PASSWORD')
    )


def get_email_delivery_mode():
    if is_smtp_configured():
        return "SMTP"
    if current_app.config.get('EMAIL_DEV_OUTBOX', True):
        return "Dev outbox"
    return "Not configured"


def get_email_delivery_notice(delivery):
    if not delivery:
        return None
    if delivery.get("mode") == "smtp":
        return "Email sent successfully."
    if delivery.get("mode") == "skipped":
        return "Email already sent for this decision."
    if delivery.get("mode") == "outbox":
        return f"SMTP is not available, so the email was saved to local outbox: {delivery.get('path')}"
    return None


def write_email_to_outbox(message, reason):
    outbox_dir = Path(current_app.instance_path) / "mail_outbox"
    outbox_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    filename = f"{timestamp}.eml"
    outbox_path = outbox_dir / filename
    outbox_path.write_bytes(message.as_bytes())
    current_app.logger.warning("Email saved to dev outbox instead of SMTP: %s", reason)
    return {
        "mode": "outbox",
        "path": str(outbox_path),
        "reason": reason,
    }


def get_sender_identity():
    sender_email = current_app.config.get('EMAIL_SENDER') or current_app.config.get('EMAIL_HOST_USER')
    sender_name = current_app.config.get('EMAIL_SENDER_NAME', 'CreditLens Support')
    if sender_name and sender_email:
        return f"{sender_name} <{sender_email}>"
    return sender_email or "CreditLens Support <noreply@creditlens.com>"


def get_support_contact():
    return {
        "email": current_app.config.get('SUPPORT_EMAIL', current_app.config.get('EMAIL_SENDER') or "support@creditlens.com"),
        "phone": current_app.config.get('SUPPORT_PHONE', "+91-00000-00000"),
        "hours": current_app.config.get('SUPPORT_HOURS', "Mon-Fri, 9:00 AM to 6:00 PM")
    }


def get_portal_url():
    return current_app.config.get('PORTAL_LOGIN_URL', "http://127.0.0.1:5000/login")


def get_loan_tenure_months(application):
    if hasattr(application, "loan_tenure_months") and getattr(application, "loan_tenure_months"):
        return int(getattr(application, "loan_tenure_months"))
    return int(current_app.config.get("DEFAULT_LOAN_TENURE_MONTHS", 36))


def derive_financial_issues(application):
    issues = []
    if application.credit_score < 650:
        issues.append("Credit score is below the preferred threshold for low-risk approval.")
    if application.loan_percent_income > 0.5:
        issues.append("Requested loan amount is high compared to declared income.")
    if application.previous_loan_defaults_on_file == 1:
        issues.append("Previous default history increases repayment risk.")
    if application.person_emp_exp < 1:
        issues.append("Limited employment history impacts income stability assessment.")
    if not issues:
        issues.append("Current financial profile did not meet internal policy thresholds.")
    return issues


def build_rejection_suggestions(suggestions):
    baseline = [
        "Increase your credit score through timely repayments and lower credit utilization.",
        "Reduce existing debt obligations before reapplying.",
        "Maintain a consistent repayment history across active credit accounts.",
        "Strengthen income stability with verifiable employment continuity."
    ]
    combined = []
    for item in baseline + list(suggestions or []):
        if item not in combined:
            combined.append(item)
    return combined


def build_decision_email_payload(application, result, reasons, suggestions):
    normalized = (result or "").strip().lower()
    is_approved = normalized == "approved"
    support = get_support_contact()
    payload = {
        "customer_name": application.customer_name,
        "customer_email": application.customer_email,
        "result": "Approved" if is_approved else "Rejected",
        "approved_loan_amount": application.loan_amnt,
        "interest_rate": application.loan_int_rate,
        "loan_tenure_months": get_loan_tenure_months(application),
        "loan_intent": application.loan_intent,
        "reasons": list(reasons or []),
        "financial_issues": derive_financial_issues(application),
        "suggestions": build_rejection_suggestions(suggestions),
        "portal_url": get_portal_url(),
        "support_email": support["email"],
        "support_phone": support["phone"],
        "support_hours": support["hours"],
        "brand_name": "CreditLens"
    }
    return payload


def send_email(subject, recipient, plain_text, html_text=None):
    message = EmailMessage()
    message['Subject'] = subject
    message['From'] = get_sender_identity()
    message['To'] = recipient
    message['Date'] = formatdate(localtime=True)
    message['Message-ID'] = make_msgid(domain="creditlens.com")
    message['X-Mailer'] = "CreditLens Notification Service"
    message['Reply-To'] = get_support_contact()["email"]
    message.set_content(plain_text)
    if html_text:
        message.add_alternative(html_text, subtype='html')

    host = current_app.config.get('EMAIL_HOST')
    port = current_app.config.get('EMAIL_PORT')
    username = current_app.config.get('EMAIL_HOST_USER')
    password = current_app.config.get('EMAIL_HOST_PASSWORD')
    use_ssl = current_app.config.get('EMAIL_USE_SSL', True)

    if not host or not username or not password:
        if current_app.config.get('EMAIL_DEV_OUTBOX', True):
            return write_email_to_outbox(
                message,
                'Email service is not configured. Set EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD.'
            )
        raise RuntimeError('Email service is not configured. Set EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD.')

    smtp = None

    try:
        if use_ssl:
            smtp = smtplib.SMTP_SSL(host, port, timeout=20)
        else:
            smtp = smtplib.SMTP(host, port, timeout=20)
            smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(message)
        return {"mode": "smtp"}
    except Exception as exc:
        if current_app.config.get('EMAIL_FALLBACK_TO_OUTBOX', True):
            return write_email_to_outbox(message, f"SMTP delivery failed: {exc}")
        raise
    finally:
        if smtp:
            try:
                smtp.quit()
            except Exception:
                pass


def build_verification_email(name, code):
    plain_text = (
        f"Hello {name},\n\n"
        f"Welcome to CreditLens. Please use the verification code below to confirm your email address and continue with your loan application:\n\n"
        f"Verification Code: {code}\n\n"
        "This code expires in 15 minutes. If you did not request this, please ignore this message.\n\n"
        "Regards,\nCreditLens Underwriting Team"
    )

    html_text = (
        f"<html><body>"
        f"<p>Hello {name},</p>"
        f"<p>Welcome to <strong>CreditLens</strong>. Please use the verification code below to confirm your email address and continue with your loan application:</p>"
        f"<h2 style=\"color:#2a6ebb;\">{code}</h2>"
        f"<p>This code expires in <strong>15 minutes</strong>. If you did not request this, no action is required.</p>"
        f"<p>Regards,<br>CreditLens Underwriting Team</p>"
        f"</body></html>"
    )

    subject = "CreditLens Email Verification Code"
    return subject, plain_text, html_text


def build_decision_email(customer_name, result, reasons, suggestions):
    # Backward-compatible fallback method used only if decision payload template path is unavailable.
    subject = f"CreditLens loan update: {result}"
    plain_text = (
        f"Hello {customer_name},\n\n"
        f"Your loan decision status is {result}.\n\n"
        "Reasons:\n"
    )
    for reason in reasons:
        plain_text += f"- {reason}\n"
    plain_text += "\nSuggestions:\n"
    for suggestion in suggestions:
        plain_text += f"- {suggestion}\n"
    plain_text += "\nRegards,\nCreditLens Support"
    html_text = (
        "<html><body>"
        f"<p>Hello {customer_name},</p>"
        f"<p>Your loan decision status is <strong>{result}</strong>.</p>"
        "<p>Regards,<br>CreditLens Support</p>"
        "</body></html>"
    )
    return subject, plain_text, html_text


def build_application_status_email(customer_name, application_ref, status_label, message):
    subject = f"CreditLens application update: {application_ref}"
    support = get_support_contact()
    plain_text = (
        f"Hello {customer_name},\n\n"
        f"Application ID: {application_ref}\n"
        f"Status: {status_label}\n\n"
        f"{message}\n\n"
        f"For support, contact {support['email']}.\n\n"
        "Regards,\nCreditLens Support"
    )
    html_text = (
        "<html><body style=\"margin:0;background:#f3f6fb;font-family:Arial,sans-serif;color:#1e293b;\">"
        "<table role=\"presentation\" width=\"100%\" style=\"padding:24px 0;\"><tr><td>"
        "<table role=\"presentation\" width=\"100%\" style=\"max-width:640px;margin:auto;background:#ffffff;border:1px solid #dbe5f2;border-radius:12px;overflow:hidden;\">"
        "<tr><td style=\"background:#102a5c;color:#ffffff;padding:20px 24px;\">"
        "<h1 style=\"margin:0;font-size:22px;\">CreditLens</h1>"
        "<p style=\"margin:6px 0 0;font-size:14px;opacity:.9;\">Application Lifecycle Update</p>"
        "</td></tr>"
        "<tr><td style=\"padding:24px;font-size:15px;line-height:1.6;\">"
        f"<p>Hello {customer_name},</p>"
        f"<p>{message}</p>"
        "<table role=\"presentation\" width=\"100%\" style=\"border:1px solid #dbe5f2;border-radius:10px;margin:18px 0;\">"
        f"<tr><td style=\"padding:12px;color:#475569;\">Application ID</td><td style=\"padding:12px;font-weight:700;\">{application_ref}</td></tr>"
        f"<tr><td style=\"padding:12px;color:#475569;\">Current Status</td><td style=\"padding:12px;font-weight:700;\">{status_label}</td></tr>"
        "</table>"
        f"<p style=\"color:#475569;font-size:14px;\">Support: {support['email']} | {support['hours']}</p>"
        "</td></tr>"
        "<tr><td style=\"padding:16px 24px 24px;color:#64748b;font-size:12px;text-align:center;\">"
        "This is a service message from CreditLens. Please keep your Application ID private."
        "</td></tr>"
        "</table></td></tr></table></body></html>"
    )
    return subject, plain_text, html_text


def send_verification_code_email(customer_name, customer_email, code):
    subject, plain_text, html_text = build_verification_email(customer_name, code)
    return send_email(subject, customer_email, plain_text, html_text)


def send_application_status_email(customer_name, customer_email, application_ref, status_label, message):
    subject, plain_text, html_text = build_application_status_email(
        customer_name,
        application_ref,
        status_label,
        message
    )
    return send_email(subject, customer_email, plain_text, html_text)


def send_decision_notification_email(application, prediction, result, reasons, suggestions, explanation_data=None, force=False):
    if prediction and int(getattr(prediction, "email_sent", 0)) == 1 and not force:
        return {"mode": "skipped", "reason": "already_sent"}

    payload = build_decision_email_payload(application, result, reasons, suggestions)
    if explanation_data:
        analysis_line = explanation_data.get("financial_analysis", "")
        payload["reasons"] = ([analysis_line] if analysis_line else []) + list(payload.get("reasons", []))
        payload["suggestions"] = list(explanation_data.get("suggestions", [])) or payload["suggestions"]
        payload["email_preview"] = explanation_data.get("email_preview", payload.get("email_preview"))
    is_approved = payload["result"] == "Approved"

    if is_approved:
        subject = (explanation_data or {}).get("email_subject") or "CreditLens loan update: application approved"
        plain_text = render_template("emails/decision_approved.txt", **payload)
        html_text = render_template("emails/decision_approved.html", **payload)
    else:
        subject = (explanation_data or {}).get("email_subject") or "CreditLens loan update: application status"
        plain_text = render_template("emails/decision_rejected.txt", **payload)
        html_text = render_template("emails/decision_rejected.html", **payload)

    return send_email(subject, application.customer_email, plain_text, html_text)
