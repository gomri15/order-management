# order-management

Order management system for an e-commerce platform. It handles user-authenticated orders,
and transactional integrity for digital purchases. Built with FastAPI and
PostgresSQL, and designed to integrate easily with tools like Retool.
Has a simple and clean frontend for users to manage their orders.

---

## TODO

- Add more integration tests
    - User API
- Add MCP support
- Add billing logic
    - Track user funds
    - Only allow purchase if user has enough funds
    - Prevent purchase if insufficient balance
- Add more custom errors
    - InsufficientFundsError
    - ProductUnavailableError
- Improve logging
    - Logging to external source (Grafana/Prometheus)
    - Improve log formatting and structure
    - Add external logging configuration support
- IAAS - terraform
- Cloud deployment
    - Support development and production mode
    - automate migration if needed
- Https support

---

## How to Set up

### Prerequisites

- Docker and Docker Compose
- Python 3.11+

### Steps

1. Clone the repository:
   ```bash
   git clone git@github.com:gomri15/order-management.git
   cd order-management
   ```

2. Create `order-app.env` files:
   ```bash
   cp .env.example order-app.env
   ```

3. Start services:
   ```bash
   docker compose up --build
   ```

4. Run Alembic migrations:
   ```bash
   docker exec -it order-app alembic upgrade head
   ```

5. Optional: Seed the database
   ```bash
   docker exec -it order-app python seed_database.py
   ```

---

## Environment Variables

| File            | Variable                      | Description                        |
|-----------------|-------------------------------|------------------------------------|
| `order-app.env` | `POSTGRES_DB`                 | Name of the DB used by the app     |
|                 | `POSTGRES_USER`               | Database user                      |
|                 | `POSTGRES_PASSWORD`           | Database password                  |
|                 | `POSTGRES_HOST`               | Hostname of the Postgres container |
|                 | `POSTGRES_PORT`               | Postgres port                      |
|                 | `SECRET_KEY`                  | Key for JWT generation             |


---

## Architecture Overview

- FastAPI app handles business logic and exposes REST endpoints
- PostgresSQL stores users, products, orders, and transactions
- Docker Compose manages multi-container orchestration
- Nginx serves as a reverse proxy for the FastAPI app and frontend

---

### Swagger

http://127.0.0.1/api/docs

---
## Testing

Run all tests:

#### Unit tests

```bash
docker exec -it orders-backend pytest app/tests/unit/
```

#### Integration tests

> ⚠️ These tests clear the DB. Use with caution.

```bash
docker exec -it orders-backend pytest app/tests/integration/
```

#### Coverage report

```bash
docker exec -it orders-backend pytest --cov=app --cov-report=term-missing app/tests/
```

---

### Contact

For questions or contributions, please open an issue or submit a PR.