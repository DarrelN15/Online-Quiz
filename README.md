# Online Quiz Project

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Future Work](#future-work)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

## Overview

This project is a Django-based online quiz application that allows users to participate in quizzes, view their results, and manage quizzes through an admin interface. The project is built using Django 5.0.7 and has been configured to use a PostgreSQL database for data management.

## Features

* **User Authentication:**

  - Users can register, log in, and log out.
  - Passwords are securely managed using Django's built-in authentication system.

* **Quizzes:**

  - Admins can create, update, and delete quizzes through the Django admin interface.
  - Each quiz consists of multiple questions, which can be single or multiple-choice.
  
* **Results Management:**

  - User quiz attempts are recorded, and scores are calculated.
  - Admins can view results for all users in a dedicated admin results page.

* **Database Management:**
  - Initially, the project used SQLite, but it was later migrated to PostgreSQL for better performance and scalability.
  
# Installation

 **Prerequisites**
*   Python 3.10
*   Django 5.0.7
*   PostgreSQL 14

  **Setup**

1.   Clone the repository:

     * bash
     * Copy code
     * git clone https://github.com/DarrelN15/Online-Quiz.git
     * cd Online-Quiz
     
2. Create and activate a virtual environment:

    * bash
    * Copy code
    * python3 -m venv .venv
    * source .venv/bin/activate
       
3. Install the required packages:

   * bash
   * Copy code
   * pip install -r requirements.txt

4. Configure PostgreSQL:

    * Create a PostgreSQL database and user.
    * Update DATABASES in settings.py with your PostgreSQL credentials.
   
5. Apply migrations:

   * bash
   * Copy code
   * python manage.py migrate
   
6. Load initial data:

    * bash
    * Copy code
    * python manage.py loaddata db.json
   
7. Create a superuser:

   * bash
   * Copy code
   * python manage.py createsuperuser
   
8. Run the development server:

   * bash
   * Copy code
   * python manage.py runserver

**Usage**

*    Access the application at http://127.0.0.1:8000/.
*    Access the admin interface at http://127.0.0.1:8000/admin/.


**Troubleshooting**

*    Admin Results Page Redirects to Home: Ensure that the user accessing the admin results page is a staff member with the correct permissions.
*    Database Connection Issues: Confirm that your PostgreSQL database is running and that the credentials in settings.py are correct.
   
**Future Work**

*    Continued Maintenance of web application

## Author

- **Darrel Nitereka** - https://github.com/DarrelN15/Online-Quiz.git

