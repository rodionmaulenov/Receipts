# Receipts API Service

The Receipts API Service is designed to streamline financial transactions for small businesses and entrepreneurs by offering a robust and secure platform for creating and managing receipts. This REST API allows users to register, authenticate, and interact with the system to generate, retrieve, and organize their transactional records effectively. It is ideal for business owners, financial accountants, and developers looking for a reliable solution to automate receipt generation and management.

## Prerequisites

Before you begin installation, ensure your system meets these requirements:
- **Python 3.8+**: Make sure Python 3.8 or newer is installed.
- **PostgreSQL**: A running PostgreSQL database is required.

## Installation

To install the project, follow these steps:

Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
git clone https://your-repository-url
pip install -r requirements.txt
```

## Create postgresql database for project and separately for testing. 
```bash
CREATE DATABASE test_db;
CREATE USER test_user WITH PASSWORD test_pass;
GRANT ALL PRIVILEGES on DATABASE test_db TO test_user;
ALTER DATABASE db_name OWNER TO test_user;
```

## API Endpoints

This service offers several endpoints for managing receipts and users:

- **POST /users/**: Register a new user.
- **POST /token**: Authenticate a user and retrieve a JWT token.
- **POST /receipts/**: Create a new receipt record.
- **GET /receipts/**: Retrieves a list of receipts for the authenticated user, with optional filtering by date, total, and payment type.
- **GET /receipts/{user_id}**: Retrieves a specific receipt by the user ID, including detailed product and payment information.

