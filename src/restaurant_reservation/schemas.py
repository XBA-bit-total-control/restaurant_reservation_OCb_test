import re
from datetime import date, time, datetime, timedelta
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


booking_create_example = {
    "name": "Анна",
    "phone": "+79991234567",
    "booking_date": "2026-12-16",
    "booking_time": "15:00:00",
    "guests": 4,
}


class BookingCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    phone: str = Field(pattern=r'^\+7\d{10}$', max_length=12)
    booking_date: date
    booking_time: time
    guests: int = Field(ge=1, le=10)

    @field_validator('phone')
    def validate_phone(cls, value: str) -> str:
        """Отклоняет номера с десятью одинаковыми цифрами после +7."""
        if re.fullmatch(r"\+7(\d)\1{9}", value):
            raise ValueError("The ten digits after +7 cannot all be the same")
        return value

    @field_validator('booking_date')
    def validate_booking_date(cls, value: date) -> date:
        """Проверяет, что дата брони входит в диапазон от сегодня до 30 дней вперёд."""
        now = datetime.today()
        date_limit = now + timedelta(days=30)
        if value > date_limit.date():
            raise ValueError("Booking date cannot be more than 30 days in the future")
        if value < now.date():
            raise ValueError("Booking date cannot be in the past")
        return value

    @field_validator('booking_time')
    def validate_booking_time(cls, value: time) -> time:
        """Проверяет, что час в диапазоне от 12 до 22, а минуты равны нулю."""
        if value.hour not in range(12, 23):
            raise ValueError("Booking time must be between 12:00 and 22:00")
        if value.minute != 0:
            raise ValueError("Booking time must have zero minutes. Use the HH:00 format")
        # Проверку second решил опустить так как посчитал незначительной
        return value

    model_config = ConfigDict(
        json_schema_extra={"examples": [booking_create_example]},
    )


class BookingOut(BaseModel):
    id: UUID
    name: str
    phone: str
    booking_date: date
    booking_time: time
    guests: int
    status: Literal['active', 'cancelled']

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    **booking_create_example,
                    "id": "0ab082fc-3d56-443f-9e42-aeea5a8df1e4",
                    "status": "active",
                },
            ],
        },
    )
