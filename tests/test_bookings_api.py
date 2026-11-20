def test_create_booking(client, booking_payload):
    created = client.post("/bookings", json=booking_payload)
    assert created.status_code == 201, f"Expected 201 when creating the booking. Response body: {created.text}"
    booking = created.json()
    assert booking["booking_date"] == booking_payload["booking_date"], "Booking date differs from the request."
    assert booking["status"] == "active", "New booking should be active."


def test_create_duplicate_booking_returns_conflict(client, booking_payload, created_booking):
    duplicate = client.post("/bookings", json=booking_payload)

    assert duplicate.status_code == 409, f"Expected 409 for an occupied slot. Response body: {duplicate.text}"
    assert duplicate.json()["detail"] == "Slot is already booked", "Unexpected slot conflict message."


def test_cancel_booking_preserves_record(client, created_booking):
    cancelled = client.delete(f"/bookings/{created_booking['id']}")
    assert cancelled.status_code == 200, f"Expected 200 when cancelling the booking. Response body: {cancelled.text}"
    expected_booking = {**created_booking, "status": "cancelled"}
    assert cancelled.json() == expected_booking, "Cancellation response differs from the expected booking."

    bookings = client.get("/bookings")
    assert bookings.status_code == 200, f"Expected 200 when listing bookings. Response body: {bookings.text}"
    assert bookings.json() == [expected_booking], "Booking list should contain only the cancelled booking."
