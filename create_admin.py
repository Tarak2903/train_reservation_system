import asyncio

from pwdlib import PasswordHash

from app.helpers.database import Base, SessionLocal, engine
from app.models.enums import Role
from app.models.schemas.user import User


async def create_admin():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    password_hash = PasswordHash.recommended()

    async with SessionLocal() as db:
        username = "admin@example.com"


        admin = User(
                name="System Admin",
                user_name=username,
                password=password_hash.hash("admin123"),
                role=Role.ADMIN,
            )
        db.add(admin)
        await db.commit()



if __name__ == "__main__":
    asyncio.run(create_admin())
