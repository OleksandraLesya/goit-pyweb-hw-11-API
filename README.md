# FastAPI Contact Book

A modern RESTful API service built with FastAPI and PostgreSQL to manage a contact book. 
It supports full CRUD operations, advanced filtering, and birthday reminders.

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

## Project Structure
HWPW11/
├── app/
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── db.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── contact.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── contact.py
│   ├── repository/
│   │   ├── __init__.py
│   │   └── contact.py
│   └── routes/
│       ├── __init__.py
│       └── contacts.py
├── main.py
├── README.md
├── .env
├── .gitignore
├── docker-compose.yml
├── alembic.ini
├── alembic/ 
│   └── versions/
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
GET /api/contacts/ — List all contacts
POST /api/contacts/ — Create a new contact
GET /api/contacts/search/?query=John — Search by name, surname or email
GET /api/contacts/birthdays/ — Contacts with birthdays in the next 7 days

## Requirements
Python 3.11+
Poetry
PostgreSQL (via Docker or local installation)
