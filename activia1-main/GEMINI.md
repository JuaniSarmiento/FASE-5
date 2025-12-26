# GEMINI.md - AI-Native MVP

## 🚀 Project Overview

This project is an AI-native educational system designed for teaching programming. It leverages generative AI to provide a comprehensive learning experience with specialized AI agents. The system is built with a modern web stack and is fully containerized for easy deployment and scalability.

### Key Features

- **6 Specialized AI Agents:**
    - **T-IA-Cog:** Cognitive Tutor for pedagogical responses.
    - **E-IA-Proc:** Procedimental Evaluator for code analysis and feedback.
    - **S-IA-X:** Simulators for practicing Git, SQL, and Bash.
    - **AR-IA:** Risk Analysis for detecting plagiarism and bad practices.
    - **GOV-IA:** Governance for auditing and pedagogical policies.
    - **TC-N4:** Traceability for tracking learning history and metrics.
- **Real LLM Integration:** Uses Ollama with the Phi-3 model locally.
- **FastAPI Backend:** A robust backend built with FastAPI, PostgreSQL, and Redis.
- **React Frontend:** A modern and interactive user interface built with React and TypeScript.
- **Dockerized:** The entire application is containerized with Docker Compose for one-command execution.

## 🛠️ Technologies

### Backend

- **Programming Language:** Python 3.11
- **Framework:** FastAPI
- **Database:** PostgreSQL 15
- **Cache:** Redis 7.4.7
- **ORM:** SQLAlchemy 2.0
- **Data Validation:** Pydantic 2.5

### Frontend

- **Framework:** React 18.2
- **Language:** TypeScript
- **Build Tool:** Vite 5.4.21
- **Routing:** React Router 6.28.0
- **API Communication:** Axios

### LLM

- **Server:** Ollama
- **Model:** Phi-3
- **Orchestration:** Langchain (optional)

### Infrastructure

- **Containerization:** Docker + Docker Compose

## 🏗️ Architecture

The system follows a microservices-oriented architecture with a clear separation between the backend, frontend, and AI services.

- **Backend:** A FastAPI application that exposes a REST API for the frontend and handles the business logic.
- **Frontend:** A single-page application (SPA) built with React that consumes the backend API.
- **Database:** A PostgreSQL database for persistent data storage.
- **Cache:** A Redis instance for caching and rate limiting.
- **LLM Service:** An Ollama container that serves the Phi-3 language model.
- **Containers:** The system is composed of 5 Docker containers: `api`, `postgres`, `redis`, `ollama`, and `pgadmin`.

## 🚀 Getting Started

### Prerequisites

- Docker Desktop
- Git

### Installation and Execution

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/JuaniSarmiento/AI-NATIVE.git
    cd AI-NATIVE
    ```

2.  **Run the application:**
    ```bash
    docker-compose up -d
    ```

3.  **Wait for the LLM to download:**
    The first time you run the application, it will download the Phi-3 model (~2GB). You can monitor the progress with:
    ```bash
    docker-compose logs -f ollama
    ```

4.  **Verify that everything is running:**
    ```bash
    docker-compose ps
    ```

### Accessing the Application

- **Frontend:** http://localhost:3001
- **API Docs (Swagger):** http://localhost:8000/docs
- **pgAdmin:** http://localhost:5050 (Credentials: `admin@ai-native.local` / `admin`)

## 💻 Development

### Running Tests

To run the backend tests, use the following command:

```bash
pytest tests/ -v --cov=backend
```

### Development Conventions

- The project uses `pydantic` for data validation and `SQLAlchemy` for database interactions.
- The backend follows the repository pattern for a clean architecture.
- The frontend uses `TypeScript` for static typing.
- All code should be formatted according to the project's linting rules (not explicitly defined in the README, but can be inferred from the code).
- Commit messages should be clear and descriptive.
