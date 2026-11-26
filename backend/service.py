
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import repository

from schemas import StudentCreate, StudentUpdate


# Retrieve all students
def list_students(db: Session, search: str = ""):

    return repository.get_students(db, search)


# Retrieve a student by ID
def get_student(db: Session, student_id: int):

    student = repository.get_student_by_id(
        db,
        student_id
    )

    if student is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    return student


# Create student
def create_student(db: Session, data: StudentCreate):

    existing_student = repository.get_student_by_email(
        db,
        data.email
    )

    if existing_student is not None:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This email is already registered"
        )

    student = repository.create_student(
        db,
        data.model_dump()
    )

    db.commit()

    return student


# Update student
def update_student(
    db: Session,
    student_id: int,
    data: StudentUpdate
):

    student = get_student(db, student_id)

    existing_student = repository.get_student_by_email(
        db,
        data.email
    )

    if (
        existing_student is not None
        and existing_student.id != student_id
    ):

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This email is already registered"
        )

    updated_student = repository.update_student(
        student,
        data.model_dump()
    )

    db.commit()

    return updated_student


# Delete student
def delete_student(db: Session, student_id: int):

    student = get_student(db, student_id)

    repository.delete_student(db, student)

    db.commit()
