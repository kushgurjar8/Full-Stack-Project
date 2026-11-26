
from sqlalchemy import (
    String,
    Integer,
    UniqueConstraint,
    CheckConstraint
)

from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Student(Base):

    __tablename__ = "students"

    __table_args__ = (

        UniqueConstraint(
            "email",
            name="uq_students_email"
        ),

        CheckConstraint(
            "mobile ~ '^[0-9]{10}$'",
            name="ck_students_mobile"
        ),

        CheckConstraint(
            "course IN ('HTML', 'CSS', 'JavaScript', "
            "'Python', 'Django')",
            name="ck_students_course"
        ),

        CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_students_name"
        ),

        CheckConstraint(
            "email = lower(email)",
            name="ck_students_email_lowercase"
        )
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(254),
        nullable=False
    )

    mobile: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    course: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
