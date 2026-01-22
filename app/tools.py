from typing import Dict, Any
import smtplib
from email.mime.text import MIMEText

from db.models import get_or_create_customer, create_booking
from app.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
from app.rag_pipeline import rag_answer


def rag_tool(query: str, vectorstore, llm) -> str:
    """RAG tool: query -> answer using uploaded PDFs + LLM."""
    return rag_answer(query, vectorstore, llm)


def booking_persistence_tool(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Persist a booking and return success + booking_id or error."""
    try:
        customer_id = get_or_create_customer(
            payload["name"],
            payload["email"],
            payload["phone"],
        )
        booking_id = create_booking(
            customer_id,
            payload["booking_type"],
            payload["date"],
            payload["time"],
        )
        return {"success": True, "booking_id": booking_id}
    except Exception as e:
        return {"success": False, "error": str(e)}


def email_tool(to_email: str, subject: str, body: str) -> Dict[str, Any]:
    """Send email via SMTP. Returns success flag and optional error."""
    if not (SMTP_USER and SMTP_PASS):
        return {"success": False, "error": "SMTP credentials not configured"}

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to_email

    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
