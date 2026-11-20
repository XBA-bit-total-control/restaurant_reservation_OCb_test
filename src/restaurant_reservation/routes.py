import sqlite3
from datetime import date as dt
from uuid import UUID

from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import services
from db import get_async_session
from exceptions import SlotAlreadyBookedError, BookingNotFoundError
from schemas import BookingCreate, BookingOut


router = APIRouter()


@router.post(
    "/bookings",
    response_model=BookingOut,
    status_code=201
)
async def create_booking(
        data: BookingCreate,
        async_session: AsyncSession = Depends(get_async_session)
) -> BookingOut:
    """Создаёт и возвращает бронь на свободный слот."""
    try:
        booking = await services.create_booking(async_session, data)
        await async_session.commit()

    except SlotAlreadyBookedError as error:
        await async_session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Slot is already booked"
        ) from error

    except IntegrityError as error:
        await async_session.rollback()
        original = error.orig
        if getattr(original, "sqlite_errorcode", None) == sqlite3.SQLITE_CONSTRAINT_UNIQUE:
            if str(original) == "UNIQUE constraint failed: bookings.booking_date, bookings.booking_time":
                raise HTTPException(
                    status_code=409,
                    detail="Slot is already booked",
                ) from error

        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        ) from error

    except Exception:
        await async_session.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

    return booking


@router.get(
    "/bookings",
    response_model=list[BookingOut],
    status_code=200
)
async def get_bookings(
        date: dt | None = None,
        async_session: AsyncSession = Depends(get_async_session)
):
    """Возвращает список броней с необязательным фильтром по дате."""
    try:
        bookings = await services.get_list_booking(async_session, date)
    except Exception:
        await async_session.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

    return bookings


@router.get(
    "/bookings/{id}",
    response_model=BookingOut,
    status_code=200
)
async def get_booking_by_id(
        id: UUID,
        async_session: AsyncSession = Depends(get_async_session)
) -> BookingOut:
    """Возвращает бронь по идентификатору."""
    try:
        booking = await services.get_booking_by_id(async_session, id)

    except Exception:
        await async_session.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")

    return booking


@router.delete(
    "/bookings/{id}",
    response_model=BookingOut,
    status_code=200
)
async def delete_booking(
        id: UUID,
        async_session: AsyncSession = Depends(get_async_session)
) -> BookingOut:
    """Отменяет бронь по идентификатору и возвращает обновлённую запись."""
    try:
        booking = await services.delete_booking(async_session, id)
        await async_session.commit()

    except BookingNotFoundError as error:
        await async_session.rollback()
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        ) from error

    except Exception:
        await async_session.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

    return booking
