from enum import Enum


class Role(Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class BookingStatus(Enum):
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"


class PassengerStatus(Enum):
    CNF = "CNF"
    RAC = "RAC"
    WL = "WL"
    CANCELLED = "CANCELLED"


class CoachClass(Enum):
    FIRST_AC = "1A"
    SECOND_AC = "2A"
    THIRD_AC = "3A"
    SLEEPER = "SL"
    CHAIR_CAR = "CC"
