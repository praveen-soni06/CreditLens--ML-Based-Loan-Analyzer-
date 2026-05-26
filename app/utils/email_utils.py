import smtplib
from email.message import EmailMessage
from flask import current_app
import random


def generate_verification_code(length=6):
    return ''.join(str(random.randint(0, 9)) for _ in range(length))


def send_email(subject, recipient, plain_text, html_text=None):
    message = EmailMessage()
    message['Subject'] = subject
    message['From'] = current_app.config.get('EMAIL_SENDER')
    message['To'] = recipient
    message.set_content(plain_text)
    if html_text:
        message.add_alternative(html_text, subtype='html')

    host = current_app.config.get('EMAIL_HOST')
    port = current_app.config.get('EMAIL_PORT')
    username = current_app.config.get('EMAIL_HOST_USER')
    password = current_app.config.get('EMAIL_HOST_PASSWORD')
    use_ssl = current_app.config.get('EMAIL_USE_SSL', True)

    if not host or not username or not password:
        raise RuntimeError('Email service is not configured. Set EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD.')

    if use_ssl:
        smtp = smtplib.SMTP_SSL(host, port, timeout=20)
    else:
        smtp = smtplib.SMTP(host, port, timeout=20)
        smtp.starttls()

    try:
        smtp.login(username, password)
        smtp.send_message(message)
    finally:
        smtp.quit()


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
    subject = f"CreditLens Loan Decision: {result}"
    plain_text = (
        f"Hello {customer_name},\n\n"
        f"Thank you for submitting your loan request to CreditLens. Our underwriting analysis has completed and the result is:\n\n"
        f"Loan Decision: {result}\n\n"
        "Why this decision was made:\n"
    )
    for reason in reasons:
        plain_text += f"- {reason}\n"
    plain_text += "\nHow you can improve your profile:\n"
    for suggestion in suggestions:
        plain_text += f"- {suggestion}\n"
    plain_text += (
        "\nWe recommend updating your financial profile and applying again after making these improvements. "
        "If you have questions, please reach out to your loan officer.\n\n"
        "Regards,\nCreditLens Underwriting Team"
    )

    html_text = (
        f"<html><body>"
        f"<p>Hello {customer_name},</p>"
        f"<p>Thank you for submitting your loan request to <strong>CreditLens</strong>. Our underwriting analysis has completed and the result is:</p>"
        f"<p><strong>Loan Decision:</strong> {result}</p>"
        f"<h3>Why this decision was made</h3>"
        f"<ul>"
    )
    for reason in reasons:
        html_text += f"<li>{reason}</li>"
    html_text += "</ul><h3>How you can improve your profile</h3><ul>"
    for suggestion in suggestions:
        html_text += f"<li>{suggestion}</li>"
    html_text += (
        "</ul><p>We recommend updating your financial profile and applying again after making these improvements. "
        "If you have questions, please reach out to your loan officer.</p>"
        "<p>Regards,<br>CreditLens Underwriting Team</p>"
        "</body></html>"
    )

    return subject, plain_text, html_text


def send_verification_code_email(customer_name, customer_email, code):
    subject, plain_text, html_text = build_verification_email(customer_name, code)
    send_email(subject, customer_email, plain_text, html_text)


def send_decision_notification_email(customer_name, customer_email, result, reasons, suggestions):
    subject, plain_text, html_text = build_decision_email(customer_name, result, reasons, suggestions)
    send_email(subject, customer_email, plain_text, html_text)
