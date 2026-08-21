# DevOS

DevOS is a backend API for a developer productivity application. I'm building it as a way to practice backend development with Python, FastAPI, and PostgreSQL while working with a real relational database and automated tests.

The project is currently under active development.

## Current Features

- Create, retrieve, update, and delete users
- PostgreSQL database integration
- Email validation and duplicate email handling
- HTTP error handling
- Request logging
- Automated API tests with pytest

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- psycopg2
- Pydantic
- pytest

## Planned Features

The next phase of DevOS will expand beyond user management into developer project tracking, including:

- User authentication
- Projects
- Coding sessions
- Project notes and tasks
- Basic activity statistics

## Running Locally

Clone the repository and install the required dependencies.

Create a `.env` file in the project directory with your PostgreSQL connection string:

DATABASE_URL=your_postgresql_connection_string

Start the API with Uvicorn:

uvicorn main:app --reload

FastAPI's interactive API documentation is available at:

http://127.0.0.1:8000/docs

## Testing

Run the test suite with:

pytest

## Status

DevOS is a work in progress. The current version establishes the API and database foundation that the project will build on.
