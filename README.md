# Cloud OS (Browser In The Cloud)
## Project Documentation
[Cloud OS API Docs](http://cloudos.us.to/api/docs)
### Project Overview

This is an open-source project built with FastAPI, which provides a REST API for managing containers on a cloud infrastructure. The project allows users to create, manage, and delete containers on a cloud server. Users can create containers with custom images and passwords, and the project will handle the provisioning and management of the cloud server.

### Project Dependencies

The project uses several Python libraries to implement its functionality. These libraries can be installed via pip and are listed in the `requirements.txt` file:

- `fastapi`: A modern, fast, web framework for building APIs with Python.
- `uvicorn`: ASGI server for running the FastAPI application.
- `python-dotenv`: For loading environment variables from a `.env` file.
- `paramiko`: A library to enable SSH connection and execution of commands on remote servers.
- `asyncio`: For handling asynchronous operations.
- `jose`: JSON Web Token (JWT) library for token-based authentication.
- `passlib`: For password hashing and verification.
- `pymongo`: For interacting with MongoDB database.
- `python-dotenv`: For loading environment variables from a `.env` file.

### Project Structure

The project consists of the following main components:

- `main.py`: The main script containing the FastAPI application and API endpoints.
- `models.py`: Definition of data models using Pydantic for request and response validation.
- `pydo.py`: A module for interacting with a DigitalOcean Droplet (cloud server) using the DigitalOcean API.
- `timer.sh`: A shell script used to start a container and manage its uptime.
- `.env`: Environment configuration file containing the required environment variables.

### Environment Variables

Before running the application, make sure to create a `.env` file in the project's root directory and define the following environment variables:

```
SECRET_KEY=your_secret_key
DB_CRED=your_db_credentials
DIGITALOCEAN_AUTH=your_digital_ocean_token
DB_URL=your_mongodb_connection_string
EMAIL_HOST_USER=your_email_address
EMAIL_HOST_PASSWORD=your_email_password
EMAIL_HOST=your_email_smtp_server
EMAIL_PORT=your_email_smtp_port
URL=your_website_url
```

### API Endpoints

The API exposes the following endpoints:

- `POST /token`: Endpoint for user authentication. It provides an access token for accessing protected endpoints.
- `GET /user`: Retrieves the current user's information.
- `POST /users/container`: Creates a new container on the cloud server for the current user.
- `DELETE /users/container`: Deletes a container from the cloud server for the current user.
- `GET /users/containers`: Retrieves a list of containers associated with the current user.
- `DELETE /container/{name}`: Deletes a server/container by its name. Only allowed with a specific `delete_key` provided as query parameter.
- `POST /register`: Endpoint for user registration. It creates a new user account and sends a verification email.

### Running the Application

To run the application, follow these steps:

1. Install the required dependencies by running: `pip install -r requirements.txt`.
2. Set up the required environment variables in the `.env` file.
3. Run the FastAPI application using Uvicorn: `uvicorn main:app --host 0.0.0.0 --port 8000`.

### Contributing

This project is open to contributions. If you find any bugs, have suggestions, or want to add new features, please feel free to submit pull requests or raise issues on the GitHub repository.

### Disclaimer

Please note that this project is intended for educational and demonstrational purposes. Deploying applications in a production environment requires careful security considerations, and it is advised to use appropriate security measures to protect sensitive data and resources.
