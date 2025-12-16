# ClipVault Backend

FastAPI service that manages clipboard history, user auth, and a local SQLite database. The Electron frontend calls these HTTP endpoints.

## Prerequisites

- Python 3.11+ 
- Windows PowerShell

## Setup (Windows)

From the `backend` folder, create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

If you see a ModuleNotFoundError (e.g., `passlib`), ensure you activated the venv and installed from `requirements.txt`.

## Run the server

```powershell
# In the backend folder with venv activated
python main.py
```

The API will be available at http://127.0.0.1:8000.

## Tests

```powershell
python -m pytest tests -v
```

Note: JavaScript tests (Jest + jsdom) are used in the frontend; backend tests use pytest only.

## Data files

- `clipboard_history.db`: SQLite database (encrypted entries)

## Dependencies

Installed via `requirements.txt`:

- fastapi: API framework
- uvicorn[standard]: ASGI server
- pyperclip: system clipboard access
- passlib[bcrypt]: password hashing
- python-jose[cryptography]: JWT tokens
- python-multipart: form data for OAuth2PasswordRequestForm
- pytest: test runner