# LLM Pioneer Project Overview for Gemini

This document provides an overview of the LLM Pioneer project, intended to serve as instructional context for the Gemini AI agent.

## Project Overview

The LLM Pioneer project is an intelligent assistant system built with Python 3.10, FastAPI, and SQLAlchemy. Its primary purpose is to provide large language model (LLM) powered Q&A chat services and leverage LLM reasoning and generation capabilities to assist users in creating and optimizing industrial investment analysis reports.

**Key Technologies:**

*   **Backend Framework:** FastAPI
*   **Database ORM:** SQLAlchemy (with MySQL)
*   **Data Validation:** Pydantic
*   **Authentication:** JWT
*   **Application Server:** Gunicorn + Uvicorn
*   **Language:** Python 3.10

**Architecture Highlights:**

The project follows a layered architecture, with clear separation of concerns:

*   `app/api`: Handles routing and API endpoints.
*   `app/core`: Contains core logic, including LLM integration, security, and background tasks (Celery).
*   `app/db`: Manages database interactions, including models and repositories.
*   `app/schemas`: Defines data models for API requests and responses.
*   `app/services`: Implements business logic.
*   `app/utils`: Provides utility functions.

## Building and Running

### Prerequisites

*   Python 3.10
*   Git

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone <repository-url> # Replace with actual repository URL if available
    cd LLMPioneer
    ```
2.  **Create and activate a virtual environment:**
    *   **Linux/macOS:**
        ```bash
        python -m venv venv
        source venv/bin/activate
        ```
    *   **Windows:**
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
3.  **Install dependencies:**
    *   For development:
        ```bash
        pip install -r requirements/dev.txt
        ```
    *   For production:
        ```bash
        pip install -r requirements/prod.txt
        ```
4.  **Configure environment variables:**
    ```bash
    cp .env.example .env
    # Edit the .env file to set necessary environment variables (e.g., database connection, JWT secrets).
    ```

### Running the Application

*   **Development Mode (with auto-reload):**
    ```bash
    uvicorn app.main:app --reload
    ```
*   **Production Mode (using Gunicorn and Uvicorn workers):**
    ```bash
    gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
    ```

### Accessing API Documentation

Once the server is running, you can access the API documentation at:

*   **Swagger UI:** `http://localhost:8000/docs`
*   **ReDoc:** `http://localhost:8000/redoc`

## Testing

To run the project's tests:

```bash
pytest
```

## Development Conventions

*   **Language:** Python 3.10
*   **Frameworks:** FastAPI for API development, SQLAlchemy for ORM.
*   **Code Structure:** Follows a modular structure with clear separation of concerns (API, services, database, core logic).
*   **Testing:** Unit and integration tests are written using `pytest`.
*   **Configuration:** Environment variables are managed via `.env` files.
*   **Logging:** Configured in `app/config/logger.py`.
*   **Security:** JWT-based authentication is implemented.
