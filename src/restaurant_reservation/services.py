from datetime import date as dt
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_async_session
from models import Booking, BookingStatus
from schemas import BookingCreate, BookingOut
from exceptions import SlotAlreadyBookedError, BookingNotFoundError


async def create_booking(
        data: BookingCreate,
        async_session: AsyncSession = Depends(get_async_session)
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
        date: dt | None = None,
        async_session: AsyncSession = Depends(get_async_session)
) -> list[BookingOut]:
    """Возвращает список броней с необязательным фильтром по дате."""
    if date is not None:
        bookings = await async_session.execute(select(Booking).where(Booking.booking_date == date))
    else:
        bookings = await async_session.execute(select(Booking))

    return list(bookings.scalars().all())


async def get_booking_by_id(
        id: UUID,
        async_session: AsyncSession = Depends(get_async_session)
) -> Booking | None:
    """Возвращает бронь по идентификатору или None, если её нет."""
    booking = await async_session.execute(select(Booking).where(Booking.id == id))
    return booking.scalar_one_or_none()


async def delete_booking(
        id: UUID,
        async_session: AsyncSession = Depends(get_async_session)
) -> Booking:
    """Отменяет бронь по идентификатору, сохраняя запись в базе."""
    booking = await get_booking_by_id(id, async_session)
    if booking is None:
        raise BookingNotFoundError("Booking not found")
    booking.status = BookingStatus.CANCELLED
    return booking
