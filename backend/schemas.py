
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator
)


# Common student fields
class StudentBase(BaseModel):

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )

    name: str = Field(
        min_length=1,
        max_length=100
    )

    email: EmailStr

    mobile: str = Field(
        pattern=r"^[0-9]{10}$"
    )

    course: Literal[
        "HTML",
        "CSS",
        "JavaScript",
        "Python",
        "Django"
    ]


    # Normalize email for duplicate checking
    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:

        email = value.lower()

        if len(email) > 254:
            raise ValueError(
                "Email cannot exceed 254 characters"
            )

        return email


# Request schema for creating a student
class StudentCreate(StudentBase):
    pass


# Request schema for updating a student
class StudentUpdate(StudentBase):
    pass


# Response schema
class StudentResponse(StudentBase):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
