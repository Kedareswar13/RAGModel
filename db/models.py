from .database import get_connection


def get_or_create_customer(name: str, email: str, phone: str) -> int:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT customer_id FROM customers WHERE email = ?", (email,))
    row = cur.fetchone()

    if row:
        customer_id = row["customer_id"]
    else:
        cur.execute(
            "INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)",
            (name, email, phone),
        )
        customer_id = cur.lastrowid
        conn.commit()

    conn.close()
    return customer_id


def create_booking(customer_id: int, booking_type: str, date: str, time: str) -> int:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO bookings (customer_id, booking_type, date, time) VALUES (?, ?, ?, ?)",
        (customer_id, booking_type, date, time),
    )

    booking_id = cur.lastrowid
    conn.commit()
    conn.close()
    return booking_id


def list_bookings(filter_name=None, filter_email=None, filter_date=None):
    conn = get_connection()
    cur = conn.cursor()

    query = (
        """
        SELECT b.id, b.date, b.time, b.booking_type, b.status,
               c.name, c.email, c.phone, b.created_at
        FROM bookings b
        JOIN customers c ON b.customer_id = c.customer_id
        WHERE 1=1
        """
    )
    params = []

    if filter_name:
        query += " AND c.name LIKE ?"
        params.append(f"%{filter_name}%")
    if filter_email:
        query += " AND c.email LIKE ?"
        params.append(f"%{filter_email}%")
    if filter_date:
        query += " AND b.date = ?"
        params.append(filter_date)

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows
