from sqlalchemy import Column, Integer, String, Enum
from app.helpers.database import Base
from app.models.enums import Role


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_name = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)
    role = Column(Enum(Role, name="role_name"), nullable=False)




