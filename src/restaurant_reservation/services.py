from datetime import date as dt
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import SlotAlreadyBookedError, BookingNotFoundError
from models import Booking, BookingStatus
from schemas import BookingCreate


async def create_booking(
        async_session: AsyncSession,
        data: BookingCreate
) -> Booking:
    """Создаёт бронь на свободный слот и добавляет её в сессию."""
    check_exists = await async_session.execute(select(Booking)
        .where(and_(Booking.booking_date == data.booking_date,
                    Booking.booking_time == data.booking_time)))
    check_exists = check_exists.scalars().all()
    if len(check_exists) > 0:
        for booking in check_exists:
            if booking.status == BookingStatus.ACTIVE:
                raise SlotAlreadyBookedError("Slot is already booked")
    booking = Booking(**data.model_dump())
    async_session.add(booking)

    return booking


async def get_list_booking(
        async_session: AsyncSession,
        date: dt | None = None
) -> list[Booking]:
    """Возвращает список броней с необязательным фильтром по дате."""
    stmt = select(Booking)
    if date is not None:
        stmt = stmt.where(Booking.booking_date == date)

    bookings = await async_session.scalars(stmt)
    return list(bookings.all())


async def get_booking_by_id(
        async_session: AsyncSession,
        id: UUID
) -> Booking | None:
    """Возвращает бронь по идентификатору или None, если её нет."""
    booking = await async_session.execute(select(Booking).where(Booking.id == id))
    return booking.scalar_one_or_none()


async def delete_booking(
        async_session: AsyncSession,
        id: UUID
) -> Booking:
    """Отменяет бронь по идентификатору, сохраняя запись в базе."""
    booking = await get_booking_by_id(async_session, id)
    if booking is None:
        raise BookingNotFoundError("Booking not found")
    booking.status = BookingStatus.CANCELLED
    return booking
