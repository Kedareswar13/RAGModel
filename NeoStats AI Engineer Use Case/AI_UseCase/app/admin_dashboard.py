import streamlit as st

from db.models import list_bookings


def render_admin_dashboard():
    st.title("Admin Dashboard - Bookings")

    col1, col2, col3 = st.columns(3)
    with col1:
        name_filter = st.text_input("Filter by name")
    with col2:
        email_filter = st.text_input("Filter by email")
    with col3:
        date_filter = st.text_input("Filter by date (YYYY-MM-DD)")

    rows = list_bookings(
        filter_name=name_filter or None,
        filter_email=email_filter or None,
        filter_date=date_filter or None,
    )

    if not rows:
        st.info("No bookings found.")
        return

    st.dataframe([dict(r) for r in rows])
