// Common forbidden characters used in validation
const FORBIDDEN_CHARS = [
    ";",
    "--",
    "'",
    '"',
    "=",
    "<",
    ">",
    "|",
    "&",
    "$",
    "@",
    "%",
    "^",
    "*",
    "(",
    ")",
    "[",
    "]",
    "{",
    "}",
    "`",
    "~",
];

// SQL injection patterns (в верхнем регистре как константа)
const SQL_PATTERNS = [
    /'[\s]*(OR|AND)/i,        // ' OR/AND
    /'\s*;\s*--/i,            // '; --
    /'\s*;\s*\/\*/i,          // '; /*
    /--\s+/i,                 // SQL comment double dash
    /\/\*.*?\*\//i,           // SQL comment /* */
    /;\s*$/i,                 // Statement ending with ;
    /UNION\s+SELECT/i,        // UNION SELECT
    /(ALTER|CREATE|DELETE|DROP|EXEC|INSERT( INTO)?|MERGE|SELECT|UPDATE|UNION)/i  // SQL commands
];

/**
 * Check if email string is valid
 * @param {string} email - Email string to validate
 * @returns {boolean} - True if valid, false otherwise
 */
function isValidEmail(email) {
    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailPattern.test(email);
}

/**
 * Check for potential SQL injection in a string
 * @param {string} inputString - The string to check
 * @returns {boolean} - True if potential SQL injection detected
 */
function hasSqlInjection(inputString) {
    if (!inputString) return false;
    return SQL_PATTERNS.some(pattern => pattern.test(inputString));
}

/**
 * Delete a case by ID
 * @param {HTMLElement} button - The button element that triggered the delete
 */
function deleteCase(button) {
    var caseId = button.getAttribute("data-case-id");
    if (confirm("Are you sure you want to delete this case?")) {
        fetch("/delete-case", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ case_id: caseId }),
        })
        .then((response) => {
            if (response.ok) {
                window.location.href = "/view-cases";
            } else {
                return response.json().then((data) => {
                    alert(data.error || "Failed to delete the case.");
                });
            }
        })
        .catch((error) => {
            alert("Failed to delete the case.");
        });
    }
}

/**
 * Delete a court by ID
 * @param {HTMLElement} button - The button element that triggered the delete
 */
function deleteCourt(button) {
    var courtId = button.getAttribute("data-court-id");
    if (confirm("Are you sure you want to delete this court?")) {
        fetch("/delete-court", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ court_id: courtId }),
        })
        .then((response) => {
            if (response.ok) {
                window.location.href = "/view-courts";
            } else {
                return response.json().then((data) => {
                    alert(data.error || "Failed to delete the court.");
                });
            }
        })
        .catch((error) => {
            alert("Failed to delete the court.");
        });
    }
}

/**
 * Delete a note by ID
 * @param {HTMLElement} button - The button element that triggered the delete
 */
function deleteNote(button) {
    var noteId = button.getAttribute("data-id");
    if (confirm("Are you sure you want to delete this note?")) {
        fetch("/delete-note", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ id: noteId }),
        })
        .then((response) => {
            if (response.ok) {
                window.location.href = "/";
            } else {
                return response.json().then((data) => {
                    alert(data.error || "Failed to delete the note.");
                });
            }
        })
        .catch((error) => {
            alert("Failed to delete the note.");
        });
    }
}

/**
 * Validate login form
 * @returns {boolean} - True if valid, false otherwise
 */
function validateLoginForm() {
    var name = document.getElementById("inputName").value;
    var password = document.getElementById("inputPassword").value;
    
    if (hasSqlInjection(name) || hasSqlInjection(password)) {
        alert("Input contains potentially harmful characters.");
        return false;
    }

    return true;
}

/**
 * Validate user registration form
 * @returns {boolean} - True if valid, false otherwise
 */
function validateUserForm() {
    var username = document.getElementById("inputUsername").value;
    var email = document.getElementById("inputEmail").value;
    var password = document.getElementById("inputPassword").value;
    
    if (!isValidEmail(email)) {
        alert("Invalid email format.");
        return false;
    }
    
    if (hasSqlInjection(username) || hasSqlInjection(password)) {
        alert("Input contains potentially harmful characters.");
        return false;
    }
    
    return true;
}

/**
 * Validate court form
 * @returns {boolean} - True if valid, false otherwise
 */
function validateCourtForm() {
    var title = document.getElementById("exampleInputTitle1").value;
    var address = document.getElementById("exampleInputAddress1").value;
    
    if (hasSqlInjection(title) || hasSqlInjection(address)) {
        alert("Input contains potentially harmful characters.");
        return false;
    }

    if (title.length < 1 || title.length > 100) {
        alert("Title must be between 1 and 100 characters long.");
        return false;
    }

    if (address.length < 1 || address.length > 100) {
        alert("Address must be between 1 and 100 characters long.");
        return false;
    }

    return true;
}

/**
 * Check if date string is valid
 * @param {string} dateString - Date string to validate
 * @returns {boolean} - True if valid, false otherwise
 */
function isValidDate(dateString) {
    var regEx = /^\d{4}-\d{2}-\d{2}$/;
    return dateString.match(regEx) != null;
}

/**
 * Check if time string is valid
 * @param {string} timeString - Time string to validate
 * @returns {boolean} - True if valid, false otherwise
 */
function isValidTime(timeString) {
    var regEx = /^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/;
    return timeString.match(regEx) != null;
}

/**
 * Validate note form
 * @returns {boolean} - True if valid, false otherwise
 */
function validateNoteForm() {
    var caseId = document.getElementById("inlineFormCustomSelectCase").value;
    var courtId = document.getElementById("inlineFormCustomSelectCourt").value;
    var status = document.getElementById("inlineFormCustomSelectStatus").value;
    var details = document.getElementById("exampleInputDetails1").value;
    var date = document.getElementById("exampleInputDate1").value;
    var time = document.getElementById("exampleInputTime1").value;
    
    if (hasSqlInjection(details)) {
        alert("Input contains potentially harmful characters.");
        return false;
    }

    if (!isValidDate(date)) {
        alert("Invalid date format.");
        return false;
    }

    if (!isValidTime(time)) {
        alert("Invalid time format.");
        return false;
    }

    return true;
}

/**
 * Toggle user active status (activate/deactivate)
 * @param {HTMLElement} button - The button element that triggered the toggle
 */
function toggleUserStatus(button) {
    var userId = button.getAttribute("data-user-id");
    fetch('/toggle-user-status', {
        method: 'POST',
        body: JSON.stringify({ user_id: userId }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        if (data.error) {
            alert(data.error);
        } else {
            // Reload page to display changes
            location.reload();
        }
    })
    .catch(function(error) {
        alert("Failed to update user status.");
    });
}

/**
 * Delete a user by ID
 * @param {HTMLElement} button - The button element that triggered the delete
 */
function deleteUser(button) {
    var userId = button.getAttribute("data-user-id");
    if (confirm("Are you sure you want to delete this user? This action cannot be undone.")) {
        fetch('/delete-user', {
            method: 'POST',
            body: JSON.stringify({ user_id: userId }),
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            if (data.error) {
                alert(data.error);
            } else {
                // Reload page to display changes
                location.reload();
            }
        })
        .catch(function(error) {
            alert("Failed to delete the user.");
        });
    }
}