# order-management

Order management system for an e-commerce platform. It handles user-authenticated orders, inventory, and transactional integrity for digital purchases. Built with FastAPI and PostgreSQL, and designed to integrate easily with tools like Retool and monitoring platforms.

---

## TODO

-  Add more integration tests
   - User API
-  Add MCP support
-  Add billing logic
    - Track user funds
    - Only allow purchase if user has enough funds
    - Prevent purchase if insufficient balance
-  Add more custom errors
    - InsufficientFundsError
    - ProductUnavailableError
- Improve logging
    - Logging to external source (Grafana/Prometheus)
    - Improve log formatting and structure
    - Add external logging configuration support
- CI CD
- IAAS - terraform 
- Cloud deployment
   - Support development and production mode
   - logic to run migration if needed

---

## How to Setup

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

3. Create retool `.env` files:
   ```bash
   ./install.sh
   ```
   3.1 If working locally and want to use retool
   Go to https://docs.retool.com/self-hosted/tutorials/docker?temporal=local
   Log in to Retool and get your license_key from https://my.retool.com/
   Paste your license key into `docker.env` at the License key section

4. Start services:
   ```bash
   docker compose up --build
   ```

5. Run Alembic migrations:
   ```bash
   docker exec -it order-app alembic upgrade head
   ```

6. Optional: Seed the database
   ```bash
   docker exec -it order-app python seed_database.py
   ```

7. Optional: Open Retool UI
   Connect to http://127.0.0.1:3000

---

## Environment Variables

| File             | Variable                      | Description                          |
|------------------|-------------------------------|--------------------------------------|
| `order-app.env`  | `POSTGRES_DB`                 | Name of the DB used by the app       |
|                  | `POSTGRES_USER`               | Database user                        |
|                  | `POSTGRES_PASSWORD`           | Database password                    |
|                  | `POSTGRES_HOST`               | Hostname of the Postgres container   |
|                  | `POSTGRES_PORT`               | Postgres port                        |
|                  | `SECRET_KEY`                  | Key for JWT generation               |
|                  | `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration in minutes          |
| `docker.env`     | `RETOOL_LICENSE_KEY`          | License key for Retool               |

---

## Architecture Overview

- FastAPI app handles business logic and exposes REST endpoints
- PostgreSQL stores users, products, orders, and transactions
- Retool is used as an admin UI on top of the API
- Docker Compose manages multi-container orchestration

---

## Important Endpoints

### Swagger
http://127.0.0.1:8000/docs

### Orders
- `POST /orders/` – Create an order
- `GET /orders/user` – Get orders by authenticated user
- `GET /orders` – Admin: Get all orders with filters
- `GET /orders/{order_id}/items` – Get items for a specific order

### Products
- `POST /products/` – Add a product
- `GET /products/` – List products
- `PUT /products/{product_id}` – Update product details

### Auth
- `POST /auth/register` – Register a user
- `POST /auth/login` – Log in and receive a JWT

---

## Usage

### Testing

Run all tests:

#### Unit tests
```bash
docker exec -it order-app pytest app/tests/unit/
```

#### Integration tests
> ⚠️ These tests clear the DB. Use with caution.
```bash
docker exec -it order-app pytest app/tests/integration/
```

#### Coverage report
```bash
docker exec -it order-app pytest --cov=app --cov-report=term-missing app/tests/
```

### Local Development
- Order app server is in debug mode so changes are hot reloaded
- Admin portal at http://localhost:3000/signin

### Working with Retool
- Retool connects to the API using JWT auth
- Retool services share the Docker network with the app
- Endpoints are authenticated and support filtered queries per user

---

### Contact
For questions or contributions, please open an issue or submit a PR.