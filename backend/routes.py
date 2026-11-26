
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Path,
    Query,
    Response,
    status
)

from sqlalchemy.orm import Session

from database import get_db

from schemas import (
    StudentCreate,
    StudentUpdate,
    StudentResponse
)

import service


router = APIRouter(
    prefix="/api/students",
    tags=["Students"]
)


# Database dependency
DBSession = Annotated[Session, Depends(get_db)]

StudentID = Annotated[int, Path(gt=0)]


# CREATE student
@router.post(
    "",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_student(
    data: StudentCreate,
    db: DBSession
):

    return service.create_student(db, data)


# READ all students
@router.get(
    "",
    response_model=list[StudentResponse]
)
def get_students(
    db: DBSession,
    search: Annotated[str, Query(max_length=100)] = ""
):

    return service.list_students(
        db,
        search.strip()
    )


# READ student by ID
@router.get(
    "/{student_id}",
    response_model=StudentResponse
)
def get_student(
    student_id: StudentID,
    db: DBSession
):

    return service.get_student(db, student_id)


# UPDATE student
@router.put(
    "/{student_id}",
    response_model=StudentResponse
)
def update_student(
    student_id: StudentID,
    data: StudentUpdate,
    db: DBSession
):

    return service.update_student(
        db,
        student_id,
        data
    )


# DELETE student
@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_student(
    student_id: StudentID,
    db: DBSession
):

    service.delete_student(db, student_id)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
