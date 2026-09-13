from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas.user import User


class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_user_by_username(self, user_name):
        result = await self.db.execute(
            select(User).where(User.user_name == user_name)
        )
        return result.scalar_one_or_none()

    async def add_user(self, user):
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
