
console.log("JavaScript connected successfully");


// ==========================================
// 1. API Configuration and Application State
// ==========================================

const API_URL =
    "http://127.0.0.1:8000/api/students";

let students = [];

let editingId = null;

let busy = false;


// ==========================================
// 2. Access HTML Elements
// ==========================================

const studentForm = document.getElementById("studentForm");
const nameInput = document.getElementById("name");
const emailInput = document.getElementById("email");
const mobileInput = document.getElementById("mobile");
const courseInput = document.getElementById("course");
const studentList = document.getElementById("studentList");
const searchInput = document.getElementById("searchInput");
const errorMessage = document.getElementById("errorMessage");
const submitBtn = document.getElementById("submitBtn");
const cancelBtn = document.getElementById("cancelBtn");


// ==========================================
// 3. Error Message Functions
// ==========================================

function showError(message) {

    errorMessage.textContent = message;

}

function clearError() {

    errorMessage.textContent = "";

}


// ==========================================
// 4. Reusable API Request Function
// ==========================================

async function apiRequest(path = "", options = {}) {

    let response;

    try {

        response = await fetch(
            API_URL + path,
            options
        );

    } catch (error) {

        console.error(error);

        throw new Error(
            "Unable to connect to the server. " +
            "Check whether FastAPI is running."
        );

    }


    // Handle unsuccessful HTTP responses
    if (!response.ok) {

        const errorData = await response.json()
            .catch(() => null);

        let message =
            `Request failed (${response.status})`;


        // Pydantic validation errors
        if (Array.isArray(errorData?.detail)) {

            message = errorData.detail.map(function(error) {

                const field = error.loc
                    .slice(1)
                    .join(".");

                return `${field}: ${error.msg}`;

            }).join(" | ");

        }


        // Custom backend errors
        else if (typeof errorData?.detail === "string") {

            message = errorData.detail;

        }

        throw new Error(message);

    }


    // DELETE returns no response body
    if (response.status === 204) {

        return null;

    }


    // Parse successful JSON response
    return await response.json();

}


// ==========================================
// 5. API Operation Wrapper
// ==========================================

async function runRequest(operation) {

    // Prevent simultaneous CRUD operations
    if (busy) {
        return;
    }

    busy = true;

    submitBtn.disabled = true;
    cancelBtn.disabled = true;

    clearError();

    try {

        await operation();

    } catch (error) {

        showError(error.message);

        console.error(error);

    } finally {

        busy = false;

        submitBtn.disabled = false;
        cancelBtn.disabled = false;

    }

}


// ==========================================
// 6. Frontend Form Validation
// ==========================================

function validateForm(name, email, mobile, course) {

    // Mandatory fields
    if (!name || !email || !mobile || !course) {

        showError("All fields are required!");

        return false;

    }


    // Name length
    if (name.length > 100) {

        showError("Name cannot exceed 100 characters!");

        nameInput.focus();

        return false;

    }


    // Email validation
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailPattern.test(email) || email.length > 254) {

        showError("Please enter a valid email address!");

        emailInput.focus();

        return false;

    }


    // Mobile number validation
    const mobilePattern = /^[0-9]{10}$/;

    if (!mobilePattern.test(mobile)) {

        showError(
            "Mobile number must contain exactly 10 digits!"
        );

        mobileInput.focus();

        return false;

    }


    // Allowed courses
    const allowedCourses = [
        "HTML",
        "CSS",
        "JavaScript",
        "Python",
        "Django"
    ];

    if (!allowedCourses.includes(course)) {

        showError("Please select a valid course!");

        return false;

    }


    // Duplicate email validation is now
    // performed by the backend

    return true;

}


// ==========================================
// 7. Load Students — GET API
// ==========================================

async function loadStudents() {

    await runRequest(async function() {

        students = await apiRequest();

        searchStudents();

        console.log(students);

    });

}


// ==========================================
// 8. Add or Update Student — POST / PUT API
// ==========================================

studentForm.addEventListener("submit", async function(event) {

    event.preventDefault();

    if (busy) {
        return;
    }

    clearError();


    // Retrieve form values
    const name = nameInput.value.trim();
    const email = emailInput.value.trim();
    const mobile = mobileInput.value.trim();
    const course = courseInput.value;


    // Validate form
    if (!validateForm(name, email, mobile, course)) {

        return;

    }


    // Prepare request body
    const studentData = {
        name,
        email,
        mobile,
        course
    };


    await runRequest(async function() {


        // ADD MODE
        if (editingId === null) {

            const createdStudent = await apiRequest(
                "",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify(studentData)
                }
            );


            // Update frontend cache
            students.push(createdStudent);

        }


        // EDIT MODE
        else {

            const updatedStudent = await apiRequest(
                `/${editingId}`,
                {
                    method: "PUT",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify(studentData)
                }
            );


            // Update frontend cache
            students = students.map(function(student) {

                if (student.id === updatedStudent.id) {

                    return updatedStudent;

                }

                return student;

            });

        }


        // Refresh table after API success
        searchStudents();


        // Clear registration form
        resetForm();

    });

});


// ==========================================
// 9. Display Students
// ==========================================

function displayStudents(studentArray = students) {

    studentList.innerHTML = "";


    // Handle empty records
    if (studentArray.length === 0) {

        const row = document.createElement("tr");
        const cell = document.createElement("td");

        cell.colSpan = 6;
        cell.textContent = "No students found";
        cell.className = "no-records";

        row.appendChild(cell);
        studentList.appendChild(row);

        return;

    }


    // Iterate over student records
    studentArray.forEach(function(student) {

        const row = document.createElement("tr");


        // Use the actual PostgreSQL student ID
        const values = [
            student.id,
            student.name,
            student.email,
            student.mobile,
            student.course
        ];


        // Create table cells
        values.forEach(function(value) {

            const cell = document.createElement("td");

            cell.textContent = value;

            row.appendChild(cell);

        });


        // Create actions cell
        const actions = document.createElement("td");


        // Edit button
        const editButton = document.createElement("button");

        editButton.textContent = "Edit";
        editButton.className = "edit-btn";
        editButton.type = "button";

        editButton.addEventListener("click", function() {

            editStudent(student.id);

        });


        // Delete button
        const deleteButton = document.createElement("button");

        deleteButton.textContent = "Delete";
        deleteButton.className = "delete-btn";
        deleteButton.type = "button";

        deleteButton.addEventListener("click", function() {

            deleteStudent(student.id);

        });


        actions.appendChild(editButton);
        actions.appendChild(deleteButton);

        row.appendChild(actions);

        studentList.appendChild(row);

    });

}


// ==========================================
// 10. Edit Student — GET by ID API
// ==========================================

async function editStudent(id) {

    await runRequest(async function() {


        // Retrieve latest student details
        const student = await apiRequest(`/${id}`);


        // Populate registration form
        nameInput.value = student.name;
        emailInput.value = student.email;
        mobileInput.value = student.mobile;
        courseInput.value = student.course;


        // Enter Edit Mode
        editingId = student.id;

        submitBtn.textContent = "Update Student";

        cancelBtn.hidden = false;


        // Scroll to registration form
        studentForm.scrollIntoView({

            behavior: "smooth",

            block: "center"

        });

        nameInput.focus({
            preventScroll: true
        });

    });

}


// ==========================================
// 11. Delete Student — DELETE API
// ==========================================

async function deleteStudent(id) {

    if (busy) {
        return;
    }


    const student = students.find(function(student) {

        return student.id === id;

    });

    if (!student) {
        return;
    }


    // Ask for confirmation
    const confirmed = confirm(
        `Are you sure you want to delete ${student.name}?`
    );

    if (!confirmed) {
        return;
    }


    await runRequest(async function() {


        // Delete student from PostgreSQL
        await apiRequest(
            `/${id}`,
            {
                method: "DELETE"
            }
        );


        // Remove student from frontend cache
        students = students.filter(function(student) {

            return student.id !== id;

        });


        // Reset editing state if necessary
        if (editingId === id) {

            resetForm();

        }


        // Refresh table
        searchStudents();

    });

}


// ==========================================
// 12. Reset Form
// ==========================================

function resetForm() {

    studentForm.reset();

    editingId = null;

    submitBtn.textContent = "Add Student";

    cancelBtn.hidden = true;

    clearError();

}


// ==========================================
// 13. Search Students
// ==========================================

function searchStudents() {

    const searchText =
        searchInput.value.trim().toLowerCase();


    // Filter the records retrieved from backend
    const filteredStudents = students.filter(
        function(student) {

            return student.name
                .toLowerCase()
                .includes(searchText);

        }
    );


    displayStudents(filteredStudents);

}


// ==========================================
// 14. Event Listeners
// ==========================================

searchInput.addEventListener(
    "input",
    searchStudents
);

cancelBtn.addEventListener(
    "click",
    resetForm
);


// ==========================================
// 15. Initialize Application
// ==========================================

loadStudents();
