from datetime import date, time
from enum import StrEnum
from uuid import uuid4, UUID

from sqlalchemy import Enum
from sqlalchemy import Index
from sqlalchemy import String, Date, Time, Integer, UUID as SQL_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BookingStatus(StrEnum):
    ACTIVE = "active"
    CANCELLED = "cancelled"


class Base(DeclarativeBase):
    id: Mapped[UUID] = mapped_column(SQL_UUID, primary_key=True, default=uuid4)


class Booking(Base):
    __tablename__ = "bookings"

    name: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(12))
    booking_date: Mapped[date] = mapped_column(Date)
    booking_time: Mapped[time] = mapped_column(Time)
    guests: Mapped[int] = mapped_column(Integer)
    status: Mapped[BookingStatus] = mapped_column(
        Enum(
            BookingStatus,
            values_callable=lambda statuses: [status.value for status in statuses],
            create_constraint=True,
            validate_strings=True,
            name="ck_bookings_status",
        ),
        nullable=False,
        default=BookingStatus.ACTIVE,
    )


Index(
    "uq_bookings_active_slot",
    Booking.booking_date,
    Booking.booking_time,
    unique=True,
    sqlite_where=(Booking.status == "active")
)