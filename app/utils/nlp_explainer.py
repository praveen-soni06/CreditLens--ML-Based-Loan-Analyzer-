import json
from datetime import datetime
from urllib import request as urllib_request
from urllib.error import URLError, HTTPError

from flask import current_app

from app.database.db import LoanDecisionExplanation, db


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _join_lines(items):
    cleaned = [str(item).strip() for item in (items or []) if str(item).strip()]
    return "\n".join(cleaned)


def _split_lines(text):
    return [line.strip() for line in (text or "").splitlines() if line.strip()]


def _build_prompt_payload(application, prediction, result, risk_level, confidence_score, language_code):
    monthly_income = _safe_float(getattr(application, "person_income", 0.0)) / 12.0
    requested_loan = _safe_float(getattr(application, "loan_amnt", 0.0))
    existing_debt_estimate = requested_loan * max(_safe_float(getattr(application, "loan_percent_income", 0.0)), 0.0)
    dti_ratio = _safe_float(getattr(application, "loan_percent_income", 0.0))

    return {
        "applicant_name": getattr(application, "customer_name", "Applicant"),
        "credit_score": _safe_int(getattr(application, "credit_score", 0)),
        "monthly_income": round(monthly_income, 2),
        "existing_debt_estimate": round(existing_debt_estimate, 2),
        "employment_status": "Employed" if _safe_int(getattr(application, "person_emp_exp", 0)) > 0 else "Limited employment history",
        "emi_history": "No previous default observed" if _safe_int(getattr(application, "previous_loan_defaults_on_file", 0)) == 0 else "Past default observed",
        "debt_to_income_ratio": round(dti_ratio, 4),
        "loan_amount_requested": requested_loan,
        "ml_prediction_result": result,
        "risk_score_category": risk_level,
        "confidence_score": round(_safe_float(confidence_score, 0.0), 4),
        "language_code": language_code,
    }


def _build_prompt_text(input_payload):
    return (
        "You are a senior banking communications analyst for CreditLens.\n"
        "Generate a clear, respectful, and professional customer-facing explanation.\n"
        "Keep tone trustworthy and concise. Avoid spam words and excessive marketing phrases.\n"
        "Return strict JSON only with keys:\n"
        "explanation_text, financial_analysis, suggestions, risk_explanation, confidence_summary, smart_tips, email_subject, email_preview.\n"
        "Rules:\n"
        "1) suggestions and smart_tips must be arrays of short bullet points.\n"
        "2) email_subject must be professional and inbox-friendly.\n"
        "3) Mention user strengths for approval and practical improvement plan for rejection.\n"
        "4) Do not include markdown.\n"
        "Input profile:\n"
        f"{json.dumps(input_payload, ensure_ascii=True)}"
    )


def _extract_json_from_text(raw_text):
    if not raw_text:
        return None
    raw_text = raw_text.strip()
    if raw_text.startswith("{") and raw_text.endswith("}"):
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            return None
    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = raw_text[start:end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            return None
    return None


def _gemini_generate(prompt_text):
    api_key = current_app.config.get("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    configured_model = current_app.config.get("GEMINI_MODEL_NAME", "gemini-1.5-flash")
    model_candidates = [configured_model, "gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-2.0-flash"]
    seen = []
    unique_models = []
    for model in model_candidates:
        if model and model not in seen:
            unique_models.append(model)
            seen.append(model)

    payload = {
        "contents": [
            {"parts": [{"text": prompt_text}]}
        ],
        "generationConfig": {
            "temperature": 0.4,
            "topP": 0.9,
            "maxOutputTokens": 900
        }
    }
    last_error = None
    for model_name in unique_models:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
            f"?key={api_key}"
        )
        data = json.dumps(payload).encode("utf-8")
        req = urllib_request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib_request.urlopen(req, timeout=25) as response:
                body = response.read().decode("utf-8")
                parsed = json.loads(body)
        except (HTTPError, URLError, TimeoutError) as exc:
            last_error = exc
            continue

        candidates = parsed.get("candidates") or []
        if not candidates:
            last_error = RuntimeError("Gemini API returned empty candidates.")
            continue
        content = candidates[0].get("content", {})
        parts = content.get("parts") or []
        if not parts:
            last_error = RuntimeError("Gemini API returned empty text parts.")
            continue

        text = "".join(str(part.get("text", "")) for part in parts).strip()
        if text:
            return text
        last_error = RuntimeError("Gemini API returned blank text.")

    raise RuntimeError(f"Gemini API request failed: {last_error}")


def _huggingface_generate(prompt_text):
    token = current_app.config.get("HUGGINGFACEHUB_API_TOKEN", "")
    if not token:
        raise RuntimeError("HUGGINGFACEHUB_API_TOKEN is not configured.")

    model_name = current_app.config.get("HF_MODEL_NAME", "mistralai/Mistral-7B-Instruct-v0.2")
    url = f"https://api-inference.huggingface.co/models/{model_name}"
    payload = {
        "inputs": prompt_text,
        "parameters": {"max_new_tokens": 700, "temperature": 0.35, "return_full_text": False},
    }
    req = urllib_request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST"
    )

    try:
        with urllib_request.urlopen(req, timeout=30) as response:
            body = response.read().decode("utf-8")
            parsed = json.loads(body)
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"HuggingFace API request failed: {exc}") from exc

    if isinstance(parsed, dict) and parsed.get("error"):
        raise RuntimeError(f"HuggingFace API error: {parsed.get('error')}")
    if not isinstance(parsed, list) or not parsed:
        raise RuntimeError("HuggingFace API returned invalid response.")
    generated = parsed[0].get("generated_text", "").strip()
    if not generated:
        raise RuntimeError("HuggingFace generated empty text.")
    return generated


def _rule_based_explanation(input_payload):
    result = str(input_payload.get("ml_prediction_result", "Rejected"))
    approved = result.lower() == "approved"
    score = _safe_int(input_payload.get("credit_score"), 0)
    dti = _safe_float(input_payload.get("debt_to_income_ratio"), 0.0)
    income = _safe_float(input_payload.get("monthly_income"), 0.0)
    emi_history = input_payload.get("emi_history", "")
    risk_level = input_payload.get("risk_score_category", "Medium")
    confidence = _safe_float(input_payload.get("confidence_score"), 0.0)

    if approved:
        strengths = []
        if score >= 700:
            strengths.append("your credit score is within a healthy approval range")
        if income >= 50000:
            strengths.append("your monthly income supports repayment commitments")
        if "No previous default" in emi_history:
            strengths.append("your repayment history appears consistent")
        if dti <= 0.4:
            strengths.append("your debt-to-income ratio remains manageable")
        if not strengths:
            strengths.append("your profile aligns with current underwriting policy")

        explanation_text = (
            "Based on our review, your application meets the current eligibility criteria. "
            f"This decision reflects {', '.join(strengths)}."
        )
        financial_analysis = (
            f"Your profile was assessed with a {risk_level.lower()} risk category and confidence of {confidence:.0%}. "
            "Income stability, repayment behavior, and credit discipline supported the positive outcome."
        )
        suggestions = [
            "Complete document verification in the secure portal to move to final processing.",
            "Maintain on-time repayments to preserve strong credit standing.",
            "Keep debt utilization balanced while the loan is active."
        ]
        risk_explanation = (
            f"Risk category: {risk_level}. The model indicates strong repayment capacity for the requested obligation."
        )
        confidence_summary = f"Model confidence for this outcome is {confidence:.0%}."
        smart_tips = [
            "Set repayment reminders to protect your score.",
            "Keep emergency savings for at least 3 months of EMI obligations.",
            "Review credit reports periodically for accuracy."
        ]
        email_subject = "CreditLens loan update: application approved"
        email_preview = "Your application has been approved based on current eligibility checks."
    else:
        explanation_text = (
            "After reviewing your financial profile, we found that your current repayment capacity and credit behavior "
            "do not meet eligibility requirements at this time."
        )
        financial_analysis = (
            f"The model categorized this request as {risk_level.lower()} risk with confidence of {confidence:.0%}. "
            f"Key drivers include credit score level, debt-to-income ratio ({dti:.2f}), and recent repayment indicators."
        )
        suggestions = [
            "Increase your credit score through consistent on-time payments.",
            "Reduce existing debt to improve debt-to-income ratio.",
            "Build stronger repayment history across active credit accounts.",
            "Improve income stability with verifiable continuity."
        ]
        risk_explanation = (
            f"Risk category: {risk_level}. Current profile signals a higher probability of repayment stress."
        )
        confidence_summary = f"Model confidence for this outcome is {confidence:.0%}."
        smart_tips = [
            "Avoid new high-limit debt before reapplying.",
            "Maintain low credit utilization for multiple billing cycles.",
            "Reapply after measurable improvement in liabilities and repayment trend."
        ]
        email_subject = "CreditLens loan update: application status"
        email_preview = "Your current application was not approved. Review improvement guidance for future eligibility."

    return {
        "provider": "rule_based",
        "explanation_text": explanation_text,
        "financial_analysis": financial_analysis,
        "suggestions": suggestions,
        "risk_explanation": risk_explanation,
        "confidence_summary": confidence_summary,
        "smart_tips": smart_tips,
        "email_subject": email_subject,
        "email_preview": email_preview,
    }


def _normalize_llm_output(parsed_json):
    suggestions = parsed_json.get("suggestions") or []
    smart_tips = parsed_json.get("smart_tips") or []
    if isinstance(suggestions, str):
        suggestions = _split_lines(suggestions)
    if isinstance(smart_tips, str):
        smart_tips = _split_lines(smart_tips)

    return {
        "explanation_text": str(parsed_json.get("explanation_text", "")).strip(),
        "financial_analysis": str(parsed_json.get("financial_analysis", "")).strip(),
        "suggestions": [str(item).strip() for item in suggestions if str(item).strip()],
        "risk_explanation": str(parsed_json.get("risk_explanation", "")).strip(),
        "confidence_summary": str(parsed_json.get("confidence_summary", "")).strip(),
        "smart_tips": [str(item).strip() for item in smart_tips if str(item).strip()],
        "email_subject": str(parsed_json.get("email_subject", "")).strip(),
        "email_preview": str(parsed_json.get("email_preview", "")).strip(),
    }


def _is_complete_output(output):
    required = [
        "explanation_text",
        "financial_analysis",
        "risk_explanation",
        "confidence_summary",
        "email_subject",
    ]
    return all(bool(str(output.get(key, "")).strip()) for key in required)


def _generate_with_provider(provider_name, prompt_text):
    if provider_name == "gemini":
        return _gemini_generate(prompt_text), "gemini"
    if provider_name == "huggingface":
        return _huggingface_generate(prompt_text), "huggingface"
    raise RuntimeError(f"Unsupported provider: {provider_name}")


def generate_loan_decision_explanation(application, prediction, result, risk_level, confidence_score, language_code="en"):
    input_payload = _build_prompt_payload(
        application=application,
        prediction=prediction,
        result=result,
        risk_level=risk_level,
        confidence_score=confidence_score,
        language_code=language_code,
    )
    prompt_text = _build_prompt_text(input_payload)
    provider_mode = (current_app.config.get("NLP_PROVIDER", "auto") or "auto").strip().lower()

    if provider_mode == "none":
        return _rule_based_explanation(input_payload)

    provider_chain = []
    if provider_mode == "gemini":
        provider_chain = ["gemini"]
    elif provider_mode == "huggingface":
        provider_chain = ["huggingface"]
    else:
        provider_chain = ["gemini", "huggingface"]

    for provider_name in provider_chain:
        try:
            raw_text, provider = _generate_with_provider(provider_name, prompt_text)
            parsed_json = _extract_json_from_text(raw_text)
            if not parsed_json:
                raise RuntimeError("Model response could not be parsed as JSON.")
            normalized = _normalize_llm_output(parsed_json)
            if not _is_complete_output(normalized):
                raise RuntimeError("Model response missing required fields.")
            normalized["provider"] = provider
            return normalized
        except Exception as exc:
            current_app.logger.warning("NLP provider %s failed: %s", provider_name, exc)

    return _rule_based_explanation(input_payload)


def save_decision_explanation(application, prediction, decision_result, language_code, explanation_data):
    if not explanation_data:
        return None

    record = LoanDecisionExplanation(
        application_id=application.id,
        prediction_id=prediction.id if prediction else None,
        decision_result=decision_result.lower(),
        language_code=language_code or "en",
        provider=explanation_data.get("provider", "rule_based"),
        explanation_text=explanation_data.get("explanation_text", ""),
        financial_analysis=explanation_data.get("financial_analysis", ""),
        suggestions_text=_join_lines(explanation_data.get("suggestions")),
        risk_explanation=explanation_data.get("risk_explanation", ""),
        confidence_summary=explanation_data.get("confidence_summary", ""),
        smart_tips=_join_lines(explanation_data.get("smart_tips")),
        email_subject=explanation_data.get("email_subject", ""),
        email_preview=explanation_data.get("email_preview", ""),
        created_at=datetime.utcnow(),
    )
    db.session.add(record)
    db.session.commit()
    return record


def get_latest_decision_explanation(application_id, decision_result=None, language_code=None):
    query = LoanDecisionExplanation.query.filter_by(application_id=application_id)
    if decision_result:
        query = query.filter_by(decision_result=str(decision_result).lower())
    if language_code:
        query = query.filter_by(language_code=language_code)
    return query.order_by(LoanDecisionExplanation.created_at.desc(), LoanDecisionExplanation.id.desc()).first()


def explanation_record_to_payload(record):
    if not record:
        return None
    return {
        "id": record.id,
        "application_id": record.application_id,
        "decision_result": record.decision_result,
        "language_code": record.language_code,
        "provider": record.provider,
        "explanation_text": record.explanation_text,
        "financial_analysis": record.financial_analysis,
        "suggestions": _split_lines(record.suggestions_text),
        "risk_explanation": record.risk_explanation,
        "confidence_summary": record.confidence_summary,
        "smart_tips": _split_lines(record.smart_tips),
        "email_subject": record.email_subject,
        "email_preview": record.email_preview,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    }
