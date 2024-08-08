Here's a `README.md` for your FastAPI project called **File Exchanger**:

---

# File Exchanger

File Exchanger is a FastAPI-based application that allows you to upload and download files via simple API endpoints. The application is designed to be easily configurable, with database connections, file storage, logging, and Google Cloud API integration all set through a configuration file.

## Features

- **Upload Files:** Upload files to the server with the `/api/upload-file/` endpoint.
- **Download Files:** Download files from the server using the `/api/download-file/{uuid}` endpoint.
- **Configurable Settings:** Easily configure database connections, file storage paths, logging, and more through a single configuration file.
- **Google Cloud API Integration:** Supports file operations with Google Cloud through an API key.

## Configuration

Before running the application, you need to provide configuration settings in a `config.json` file located in the `settings` directory. Below is an example configuration file:

```json
{
    "postgre_connection_str": "postgresql+psycopg2://user:password@host:port/db_name",
    "sqlite_connection_str": "sqlite:///db_name",
    "database": "db_name",
    "files_dir_path": "relative path to files folder",
    "google_api_key_path": "relative path to google api key.json",
    "logs_dir_path": "relative path to logs folder",
    "logs_file_name": "name of the log file",
    "max_file_size": max file size in bytes
}
```

- **postgre_connection_str**: Connection string for the PostgreSQL database.
- **sqlite_connection_str**: Connection string for the SQLite database.
- **database**: The name of the database to use.
- **files_dir_path**: Path to the directory where files will be stored.
- **google_api_key_path**: Path to the Google API key JSON file.
- **logs_dir_path**: Path to the directory where logs will be stored.
- **logs_file_name**: Name of the log file.
- **max_file_size**: Maximum file size allowed for uploads (in bytes).

**Important**: Ensure that the Google API key JSON file is placed in the specified path.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your_username/file_exchanger.git
    cd file_exchanger
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

1. Ensure that the `config.json` file is properly configured and that the Google API key JSON file is in the specified location.

2. Start the FastAPI application:
    ```bash
    uvicorn main:app --reload
    ```

   The application will be available at `http://127.0.0.1:8000`.

## Running Tests

To run the tests:

1. Ensure the FastAPI application is stopped.
2. Run the test script:
    ```bash
    python testmain.py
    ```

## Endpoints

### 1. `/api/upload-file/`
   - **Method**: POST
   - **Description**: Upload a file to the server.
   - **Request**: Multipart/form-data with the file to be uploaded.
   - **Response**: Returns a success message and file uuid.

### 2. `/api/download-file/{uuid}/`
   - **Method**: GET
   - **Description**: Download a file from the server.
   - **Request**: Query parameter specifying the file name.
   - **Response**: Returns the requested file.
