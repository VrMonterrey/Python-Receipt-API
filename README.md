# Receipt Management API

This project is a REST API for managing sales receipts, allowing user registration, authentication, receipt creation, and viewing. The API is built with **FastAPI** and **PostgreSQL** and uses **JWT** for authentication.

## Features

- User registration and authentication (JWT-based)
- Create sales receipts (list of products, payment details, total, etc.)
- View and filter user-specific receipts
- Access and refresh token-based authentication

## Requirements

- Python 3.8+
- PostgreSQL
- `pip` (Python package installer)

## Installation and Setup

### 1. Clone the Repository

```bash
git clone git@github.com:VrMonterrey/Python-Receipt-API.git
cd <project-directory>
```

### 2. Set Up a Virtual Environment

Create and activate a virtual environment using Python:

```bash
python3 -m venv venv
source venv/bin/activate  # For macOS/Linux
venv\Scripts\activate      # For Windows
```

### 3. Install Dependencies

Install the project dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root of the project and set the following environment variables for connecting to the PostgreSQL database and generating JWT tokens:

```env
SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://username:password@localhost/receipt
```

### 5. Set Up the Database

Ensure that PostgreSQL is running on your machine and create the necessary database:

```sql
CREATE DATABASE receipt;
```

Then, run the Alembic migrations to set up the database schema:

```bash
alembic upgrade head
```

### 6. Run the Application

Once everything is set up, you can run the FastAPI application:

```bash
uvicorn app.main:app --reload
```

The app will be available at `http://127.0.0.1:8000/`.

### 7. Access the API Documentation

FastAPI provides automatically generated API documentation. You can access it at:

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

### 8. Testing the API

To test the API, you can use any HTTP client like **Postman** or **curl**. Alternatively, you can test it directly from the **Swagger UI** interface.

### API Endpoints

Here are the key endpoints:

- **User Registration**: `POST /users/register/`
- **User Login (JWT)**: `POST /users/login/`
- **Create a Receipt**: `POST /receipts/`
- **List User Receipts**: `GET /receipts/`
- **Refresh Access Token**: `POST /users/refresh/`

### Example Request for Creating a Receipt

```json
{
  "products": [
    {
      "name": "Product 1",
      "price": 100.50,
      "quantity": 2
    },
    {
      "name": "Product 2",
      "price": 50.00,
      "quantity": 1
    }
  ],
  "payment": {
    "type": "cash",
    "amount": 300
  }
}
```

### Response Example

```json
{
  "id": 1,
  "products": [
    {
      "name": "Product 1",
      "price": 100.50,
      "quantity": 2,
      "total": 201.00
    },
    {
      "name": "Product 2",
      "price": 50.00,
      "quantity": 1,
      "total": 50.00
    }
  ],
  "total": 251.00,
  "rest": 49.00,
  "created_at": "2024-09-19T12:34:56.789Z",
  "payment": {
    "type": "cash",
    "amount": 300.00
  }
}
```

## Running Tests

To run tests using `pytest`, use the following command:

```bash
pytest
```

Make sure to have the necessary test setup and database configuration before running the tests.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for more details.