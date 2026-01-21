from dataclasses import dataclass


@dataclass
class BookingState:
    name: str = ""
    email: str = ""
    phone: str = ""
    booking_type: str = ""
    date: str = ""  # YYYY-MM-DD
    time: str = ""  # HH:MM
    confirmed: bool = False


REQUIRED_FIELDS = ["name", "email", "phone", "booking_type", "date", "time"]


def get_booking_state(session_state) -> BookingState:
    if "booking_state" not in session_state:
        session_state.booking_state = BookingState()
    return session_state.booking_state


def is_complete(state: BookingState) -> bool:
    return all(getattr(state, f) for f in REQUIRED_FIELDS)


def summarize_booking(state: BookingState) -> str:
    return (
        f"Please confirm your booking details:\n\n"
        f"- Name: {state.name}\n"
        f"- Email: {state.email}\n"
        f"- Phone: {state.phone}\n"
        f"- Booking type: {state.booking_type}\n"
        f"- Date: {state.date}\n"
        f"- Time: {state.time}\n\n"
        "Click the confirm button to save, or edit the fields above to change any detail."
    )
