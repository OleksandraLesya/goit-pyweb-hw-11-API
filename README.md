# FastAPI Contact Book with a secure authentication system.

A modern RESTful API service built with FastAPI and PostgreSQL to manage a contact book. 
It supports full CRUD operations, advanced filtering, and birthday reminders with a secure authentication system.

## Features

- FastAPI with automatic interactive Swagger documentation
- PostgreSQL database via SQLAlchemy ORM
- Alembic for database migrations
- Pydantic validation with email and date parsing
- Search contacts by name, surname, email
- Enhanced contact update flexibility (partial updates are now supported)
- Robust birthday calculation, including proper handling of February 29th in non-leap years.
- Get contacts with upcoming birthdays
- Environment-based configuration with `.env`
- Poetry for dependency management

## Authentication & Authorization
- Authentication: User registration and login with JWT tokens. 
- Authorization: Protected routes using JWT tokens. 
- Contact Ownership: Users can only manage their own contacts. 
- Password Hashing: Secure password storage. 
- Gravatar Integration: User avatars based on email.

## Project Structure
HWPW11/
├── app/
│   ├── __init__.py
│   ├── conf/
│   │   └── config.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── db.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── users.py
│   │   └── contact.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── users.py
│   │   └── contact.py
│   ├── services/
│   │   └── auth.py
│   ├── repository/
│   │   ├── __init__.py
│   │   ├── users.py
│   │   └── contact.py
│   └── routes/
│       ├── __init__.py
│       ├── auth.py
│       └── contacts.py
├── main.py
├── README.md
├── .env
├── .gitignore
├── docker-compose.yml
├── alembic.ini
├── alembic/ 
│   └── versions/
│       ├── 524c86f1d584_add_users_table_and_link_contacts_to_.py
│   │   └── b0f14953ec69_initial_database_schema.py
│   ├── env.py
│   ├── README
│   └── script.py.mako
├── poetry.lock
└── pyproject.toml

## Setup Instructions

1. Clone the repository:
`git clone https://github.com/YourUsername/your-repo-name.git
cd your-repo-name`

2. Install dependencies using Poetry:
`poetry install`

3. Set up the PostgreSQL database using Docker:
`docker run --name contacts-db -e POSTGRES_USER=postgres -e 
POSTGRES_PASSWORD=mysecretpassword -e POSTGRES_DB=contacts_db -p 5432:5432 -d postgres`

4. Configure environment variables in .env file:
`DATABASE_URL=postgresql://postgres:mysecretpassword@localhost:5432/contacts_db`

5. Run Alembic migrations:
`poetry run alembic upgrade head`

6. Start the server:
`poetry run uvicorn app.main:app --reload`

7. Visit the documentation:
Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc

## Example Requests
POST /api/auth/login - Log in and get JWT tokens
GET /api/contacts/ — List all contacts (requires authentication)
POST /api/contacts/ — Create a new contact (requires authentication)
GET /api/contacts/search/?query=John — Search by name, surname or email (requires authentication)
GET /api/contacts/birthdays/ — Contacts with birthdays in the next 7 days (requires authentication)

## Requirements
Python 3.11+
Poetry
PostgreSQL (via Docker or local installation)
Additional Python libraries: python-jose, passlib, bcrypt, libgravatar
