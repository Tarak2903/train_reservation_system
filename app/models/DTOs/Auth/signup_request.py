from pydantic import BaseModel, EmailStr


class SignupRequest(BaseModel):
    name: str
    user_name: EmailStr
    password: str
