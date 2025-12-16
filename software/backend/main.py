from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import logging
import time
import os

from clipboard import ClipboardManager
from database import ClipboardDB
from clipboard_crypto import clipboard_crypto
from secure_storage import key_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

clipboard = ClipboardManager()
db = ClipboardDB()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting ClipVault backend")

    if not clipboard_crypto.verify_encryption():
        raise RuntimeError("Encryption verification failed")

    logger.info("Encryption system verified")

    if os.getenv("CLIPVAULT_DISABLE_CLIPBOARD") != "1":
        clipboard.start_monitoring(db)
        logger.info("Clipboard monitoring started")

    yield

    logger.info("Shutting down ClipVault backend")
    clipboard.stop_monitoring()


app = FastAPI(
    lifespan=lifespan,
    title="ClipVault Secure API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"status": "ok", "service": "ClipVault"}


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "timestamp": time.time(),
        "encryption": clipboard_crypto.verify_encryption(),
        "key_present": key_manager.get_key_info()["clipboard_key_exists"],
    }


@app.get("/clipboard/current")
async def get_clipboard():
    return {"content": clipboard.get_clipboard_content()}


@app.get("/clipboard/history")
async def get_history(limit: int = 10):
    return {"history": db.get_history(limit)}


@app.delete("/clipboard/history")
async def clear_history():
    db.clear_history()
    return {"cleared": True}


@app.delete("/clipboard/history/{entry_id}")
async def delete_entry(entry_id: int):
    if not db.delete_entry(entry_id):
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"deleted": True}


@app.post("/admin/rotate-key")
async def rotate_key():
    clipboard_crypto.rotate_key()
    return {
        "message": "Clipboard encryption key rotated",
        "warning": "Existing data is no longer decryptable"
    }


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
    )
