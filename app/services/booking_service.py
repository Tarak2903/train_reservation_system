import secrets
from datetime import date

from app.exceptions.forbidden_exception import ForbiddenException
from app.exceptions.resource_already_exists_exception import ResourceAlreadyExistsException
from app.models.enums import BookingStatus, PassengerStatus
from app.exceptions.booking_exceptions import (
    BookingOperationException,
)
from app.exceptions.resource_not_found_execption import ResourceNotFoundException
from app.models.schemas.booking import Booking, BookingPassenger


class BookingService:
    def __init__(self, booking_repo, train_repo,journey_repo):
        self.booking_repo = booking_repo
        self.train_repo = train_repo
        self.journey_repo=journey_repo


    @staticmethod
    def generate_pnr():
        return str(secrets.randbelow(900000000) + 100000000)

    async def _get_available_seats(
            self,
            train_id,
            journey_date,
            class_type,
            group_size,
    ):
        occupied = await self.booking_repo.get_occupied_seat_ids(
            train_id,
            journey_date,
            class_type,
        )

        seats = await self.booking_repo.get_seats(
            train_id,
            class_type,
        )

        selected_seats = []

        for seat in seats:

            if seat.id in occupied:
                continue

            locked = await self.booking_repo.try_lock_seat(
                journey_date,
                seat.id,
            )

            if not locked:
                continue

            occupied_now = await self.booking_repo.get_occupied_seat_ids(
                train_id,
                journey_date,
                class_type,
            )

            if seat.id in occupied_now:
                continue

            selected_seats.append(seat)

            if len(selected_seats) == group_size:
                break

        return selected_seats

    async def _next_sequence(self, schedule_id, class_type, status):
        return await self.booking_repo.get_next_sequence(schedule_id,class_type,status)


    async def validate_cancellation_request(self, booking_id, user_id):
        booking = await self.booking_repo.find_booking(booking_id)

        if not booking:
            raise ResourceNotFoundException("Booking Not found")

        if booking.status == BookingStatus.CANCELLED:
            raise ResourceNotFoundException(
                "Booking already inactive"
            )

        if booking.user_id != user_id:
            raise  ForbiddenException(
                "You can only cancel ur own ticket"
            )
        return booking


    async def validate_train_by_id(self,train_id):
        train=await self.train_repo.find_train_by_id(train_id)
        if not train :
            raise ResourceNotFoundException("Train doesnt exists")
        return train


    async def validate_journey(self,train_id,journey_date):
        if journey_date<date.today():
            raise ValueError
        journey=await self.journey_repo.find_schedule(train_id, journey_date)
        if not journey:
            raise BookingOperationException("Journey date is not available")
        return journey


    async def validate_booking_request(self,request):
        passenger_ids = list(dict.fromkeys(request.passenger_ids))
        if len(passenger_ids) != len(request.passenger_ids):
            raise BookingOperationException("Duplicate passenger in group booking")

        for passenger_id in passenger_ids:
            if not await self.booking_repo.find_user(passenger_id):
                raise ResourceNotFoundException(
                    f"Passenger {passenger_id} doesnt exists"
                )

            if await self.booking_repo.find_active_passenger_on_journey(
                passenger_id,
                request.train_id,
                request.journey_date,
            ):
                raise ResourceAlreadyExistsException(
                    f"Passenger {passenger_id} already has an active booking"
                )
        return passenger_ids

    @staticmethod
    def validate_booking_availability(request,confirmed_available,group_size,current_rac,rac_capacity):
        if request.booking_status == PassengerStatus.CNF and confirmed_available<group_size:
                raise BookingOperationException("Not enough confirmed seats available for the entire group")

        elif request.booking_status == PassengerStatus.RAC:
            if confirmed_available > 0:
                raise BookingOperationException("RAC booking is not allowed while confirmed seats are available")
            if current_rac + group_size > rac_capacity:
                raise BookingOperationException("Not enough RAC capacity available for the entire group")

        elif request.booking_status == PassengerStatus.WL:
            if confirmed_available > 0:
                raise BookingOperationException("Waitlist booking is not allowed while confirmed seats are available")
            if current_rac < rac_capacity:
                raise BookingOperationException("Waitlist booking is not allowed while RAC capacity is available")



    async def book_ticket(self, request, user_id):
        train=await self.validate_train_by_id(request.train_id)
        schedule=await self.validate_journey(request.train_id,request.journey_date)
        passenger_ids=await self.validate_booking_request(request)

        group_size = len(passenger_ids)
        class_type = request.class_type
        available_seats = await self._get_available_seats(request.train_id,request.journey_date,class_type,group_size)
        confirmed_available = len(available_seats)
        current_rac = await self.booking_repo.get_queue_count(schedule.id,class_type,PassengerStatus.RAC)
        rac_capacity = await self.booking_repo.get_total_rac_capacity(request.train_id,class_type)

        self.validate_booking_availability(request,confirmed_available,group_size,current_rac,rac_capacity)

        booking = Booking(pnr=self.generate_pnr(),user_id=user_id,train_id=request.train_id,schedule_id=schedule.id,
            journey_date=request.journey_date,class_type=class_type, status=BookingStatus.ACTIVE,
        )
        await self.booking_repo.add_booking(booking)

        if request.booking_status == PassengerStatus.CNF:
            message= await self.book_confirm_ticket(booking,passenger_ids,available_seats)

        elif request.booking_status == PassengerStatus.RAC:
            message=await self.book_rac_ticket(booking,schedule,class_type,passenger_ids)

        else:
            message=await self.book_waiting_ticket(booking, schedule, class_type, passenger_ids)

        await self.booking_repo.commit()
        booking = await self.booking_repo.find_booking(booking.id)
        return booking, message

    async def book_confirm_ticket(self,booking,passenger_ids,available_seats):
        for passenger_id, seat in zip(passenger_ids, available_seats):
            await self.booking_repo.add_passenger(
                BookingPassenger(
                    booking_id=booking.id,
                    passenger_id=passenger_id,
                    status=PassengerStatus.CNF,
                    seat_id=seat.id,
                )
            )
        return "Ticket booked successfully"

    async def book_waiting_ticket(self,booking,schedule,class_type,passenger_ids):
        next_sequence = await self._next_sequence(
            schedule.id,
            class_type,
            PassengerStatus.WL,
        )
        for passenger_id in passenger_ids:
            await self.booking_repo.add_passenger(
                BookingPassenger(
                    booking_id=booking.id,
                    passenger_id=passenger_id,
                    status=PassengerStatus.WL,
                    queue_sequence=next_sequence,
                )
            )
            next_sequence += 1
        return "Ticket booked in waitlist"

    async def book_rac_ticket(self,booking,schedule,class_type,passenger_ids):
        next_sequence = await self._next_sequence(
            schedule.id,
            class_type,
            PassengerStatus.RAC,
        )
        for passenger_id in passenger_ids:
            await self.booking_repo.add_passenger(
                BookingPassenger(
                    booking_id=booking.id,
                    passenger_id=passenger_id,
                    status=PassengerStatus.RAC,
                    queue_sequence=next_sequence,
                )
            )
            next_sequence += 1
        return "Ticket booked in RAC"


    async def cancel_ticket(self, booking_id, user_id):
        booking = await self.validate_cancellation_request(booking_id, user_id)
        status = booking.passengers[0].status

        if status == PassengerStatus.CNF:
            await self.cancel_confirm_ticket(booking)
        elif status == PassengerStatus.RAC:
            await self.cancel_rac_ticket(booking)

        booking.status = BookingStatus.CANCELLED
        for passenger in booking.passengers:
            passenger.status = PassengerStatus.CANCELLED
            passenger.seat_id = None
            passenger.queue_sequence = None

        await self.booking_repo.db.commit()
        return booking

    async def cancel_confirm_ticket(self, booking):
        confirmed_seats_no = [passenger.seat_id for passenger in booking.passengers]
        total_confirmed_seats = len(confirmed_seats_no)
        rac_passengers = await self.booking_repo.find_top_k_status_passengers(booking,total_confirmed_seats,PassengerStatus.RAC)
        i = 0
        for passenger in rac_passengers:
            passenger.queue_sequence = None
            passenger.seat_id = confirmed_seats_no[i]
            passenger.status = PassengerStatus.CNF
            i += 1

        remaining_confirmed_seats = total_confirmed_seats - len(rac_passengers)
        waiting_passengers = await self.booking_repo.find_top_k_status_passengers(booking,remaining_confirmed_seats,PassengerStatus.WL)
        i = len(rac_passengers)
        for passenger in waiting_passengers:
            passenger.queue_sequence = None
            passenger.seat_id = confirmed_seats_no[i]
            passenger.status = PassengerStatus.CNF
            i += 1

        await self.booking_repo.db.flush()
        rac_slots = len(rac_passengers)
        waiting_passengers = await self.booking_repo.find_top_k_status_passengers(booking,rac_slots,PassengerStatus.WL)

        for passenger in waiting_passengers:
            passenger.status = PassengerStatus.RAC

        await self.booking_repo.db.flush()


    async def cancel_rac_ticket(self, booking):
        await self.promote_waiting_passengers(booking)

    async def promote_waiting_passengers(self, booking):
        rac_passengers = booking.passengers
        waiting_passenger = await self.booking_repo.find_top_k_status_passengers(booking,len(rac_passengers),PassengerStatus.WL)

        for passenger in waiting_passenger:
            passenger.status = PassengerStatus.RAC

        await self.booking_repo.db.flush()


    async def get_booking_status(self, booking_id, user_id):
        booking =await self.validate_cancellation_request(booking_id,user_id)
        return booking


    async def get_queue(self, train_id, journey_date, class_type, status):
        await self.validate_train_by_id(train_id)
        await  self.validate_journey(train_id,journey_date)

        return await self.booking_repo.get_active_queue(train_id,journey_date,class_type,status)


    async def get_availability(self, train_id, journey_date, class_type):
        await self.validate_train_by_id(train_id)
        schedule=await self.validate_journey(train_id,journey_date)
        total = await self.booking_repo.get_total_seat_count(train_id, class_type)
        confirmed = await self.booking_repo.get_confirmed_count(schedule.id, class_type)
        rac_capacity = await self.booking_repo.get_total_rac_capacity(train_id, class_type)
        rac = await self.booking_repo.get_queue_count(schedule.id,class_type,PassengerStatus.RAC,)
        waitlist = await self.booking_repo.get_queue_count(schedule.id,class_type,PassengerStatus.WL,)
        if total ==0:
            raise ResourceNotFoundException("Coach with this cls doesnt exist")
        return {
            "train_id": train_id,
            "journey_date": journey_date,
            "class_type": class_type.value,
            "total_seats": total,
            "confirmed": confirmed,
            "available": total - confirmed,
            "rac_capacity": rac_capacity,
            "rac": rac,
            "waitlist": waitlist,
        }
    async def get_all_trains_on_journey_date(self,journey_date):
        trains=await self.train_repo.find_all_train_on_journey_date(journey_date)
        if len(trains) == 0:
            raise ResourceNotFoundException("No trains exists on given journey date")
        return trains
