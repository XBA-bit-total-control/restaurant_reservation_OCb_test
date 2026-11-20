class SlotAlreadyBookedError(Exception):
    """Слот уже забронирован."""
    pass


class BookingNotFoundError(Exception):
    """Забронированного слота не найдено."""
    pass
