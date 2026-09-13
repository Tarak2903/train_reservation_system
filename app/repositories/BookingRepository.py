from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.schemas.booking import Booking, BookingPassenger
from app.models.schemas.coach import Coach
from app.models.schemas.seat import Seat
from app.models.schemas.user import User
from app.models.schemas.train_schedule import TrainSchedule
from app.models.enums import BookingStatus, PassengerStatus, CoachClass


class BookingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_booking(self, booking_id):
        result = await self.db.execute(
            select(Booking)
            .options(
                selectinload(Booking.passengers).selectinload(
                    BookingPassenger.passenger
                ),
                selectinload(Booking.passengers)
                .selectinload(BookingPassenger.seat)
                .selectinload(Seat.coach),
            )
            .where(Booking.id == booking_id)
        )
        return result.scalar_one_or_none()

    async def find_user(self, user_id):
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def find_schedule(self, train_id, journey_date):
        result = await self.db.execute(
            select(TrainSchedule).where(
                TrainSchedule.train_id == train_id,
                TrainSchedule.journey_date == journey_date,
            )
        )
        return result.scalar_one_or_none()

    async def add_booking(self, booking):
        self.db.add(booking)
        await self.db.flush()
        return booking

    async def add_passenger(self, passenger):
        self.db.add(passenger)

    async def find_active_passenger_on_journey(
        self,
        passenger_id,
        train_id,
        journey_date,
    ):
        result = await self.db.execute(
            select(BookingPassenger)
            .join(Booking)
            .where(
                BookingPassenger.passenger_id == passenger_id,
                Booking.train_id == train_id,
                Booking.journey_date == journey_date,
                Booking.status == BookingStatus.ACTIVE,
                BookingPassenger.status != PassengerStatus.CANCELLED,
            )
        )
        return result.scalar_one_or_none()



    async def get_seats(self, train_id, class_type):
        result = await self.db.execute(
            select(Seat)
            .join(Coach)
            .where(
                Coach.train_id == train_id,
                Coach.class_type == class_type,
            )
            .order_by(Coach.id, Seat.seat_number)
        )
        return result.scalars().all()

    async def get_occupied_seat_ids(self, train_id, journey_date, class_type):
        result = await self.db.execute(
            select(BookingPassenger.seat_id)
            .join(Booking)
            .where(
                Booking.train_id == train_id,
                Booking.journey_date == journey_date,
                Booking.class_type == class_type,
                Booking.status == BookingStatus.ACTIVE,
                BookingPassenger.status == PassengerStatus.CNF,
                BookingPassenger.seat_id.is_not(None),
            )
        )
        return {row[0] for row in result.all()}



    async def get_active_queue(self, train_id, journey_date, class_type, status):
        result = await self.db.execute(
            select(BookingPassenger)
            .options(
                selectinload(BookingPassenger.passenger),
                selectinload(BookingPassenger.booking),
            )
            .join(Booking)
            .where(
                Booking.train_id == train_id,
                Booking.journey_date == journey_date,
                Booking.class_type == class_type,
                Booking.status == BookingStatus.ACTIVE,
                BookingPassenger.status == status,
            )
            .order_by(BookingPassenger.queue_sequence.asc())
        )
        return result.scalars().all()

    async def get_next_sequence(self, schedule_id, class_type, status):
        result = await self.db.execute(
            select(func.max(BookingPassenger.queue_sequence))
            .join(Booking)
            .where(
                Booking.schedule_id == schedule_id,
                Booking.class_type == class_type,
                BookingPassenger.status == status,
            )
        )
        last = result.scalar()
        return (last or 0) + 1

    async def get_queue_count(self, schedule_id, class_type, status):
        result = await self.db.execute(
            select(func.count(BookingPassenger.id))
            .join(Booking)
            .where(
                Booking.schedule_id == schedule_id,
                Booking.class_type == class_type,
                Booking.status == BookingStatus.ACTIVE,
                BookingPassenger.status == status,
            )
        )
        return result.scalar_one()

    async def get_confirmed_count(self, schedule_id, class_type):
        result = await self.db.execute(
            select(func.count(BookingPassenger.id))
            .join(Booking)
            .where(
                Booking.schedule_id == schedule_id,
                Booking.class_type == class_type,
                Booking.status == BookingStatus.ACTIVE,
                BookingPassenger.status == PassengerStatus.CNF,
            )
        )
        return result.scalar_one()

    async def get_total_seat_count(self, train_id, class_type):
        result = await self.db.execute(
            select(func.sum(Coach.total_seat_capacity)).where(
                Coach.train_id == train_id,
                Coach.class_type == class_type,
            )
        )
        return result.scalar() or 0

    async def get_total_rac_capacity(self, train_id, class_type):
        result = await self.db.execute(
            select(func.sum(Coach.rac_capacity)).where(
                Coach.train_id == train_id,
                Coach.class_type == class_type,
            )
        )
        return result.scalar() or 0

    async def find_top_k_status_passengers(self,booking,k,status):
        result=await  self.db.execute(
            select(BookingPassenger)
            .join(Booking)
            .where(
                Booking.train_id==booking.train_id,
                Booking.schedule_id==booking.schedule_id,
                Booking.class_type==booking.class_type,
                BookingPassenger.status==status
            ).order_by(BookingPassenger.queue_sequence)
            .limit(k)
        )
        return result.scalars().all()


    async def commit(self):
        await self.db.commit()

    async def refresh(self, obj):
        await self.db.refresh(obj)

    async def rollback(self):
        await self.db.rollback()
