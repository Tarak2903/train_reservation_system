class SeatRepository:
    def __init__(self,db):
        self.db=db

    async def add_seat(self, seats):
        self.db.add_all(seats)
        await self.db.flush()
        return seats