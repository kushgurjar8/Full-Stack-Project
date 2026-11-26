
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Student


# Retrieve all students
def get_students(db: Session, search: str = ""):

    query = select(Student)

    if search:

        query = query.where(
            Student.name.icontains(
                search,
                autoescape=True
            )
        )

    query = query.order_by(Student.id)

    return db.scalars(query).all()


# Retrieve student by ID
def get_student_by_id(db: Session, student_id: int):

    return db.get(Student, student_id)


# Retrieve student by email
def get_student_by_email(db: Session, email: str):

    query = select(Student).where(
        Student.email == email
    )

    return db.scalar(query)


# Add student to session
def create_student(db: Session, student_data: dict):

    student = Student(**student_data)

    db.add(student)

    return student


# Update an existing student
def update_student(
    student: Student,
    student_data: dict
):

    for key, value in student_data.items():

        setattr(student, key, value)

    return student


# Delete student
def delete_student(db: Session, student: Student):

    db.delete(student)
