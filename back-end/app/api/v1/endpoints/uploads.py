from typing import Any

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
import shutil
import os
import uuid

from app.core.config import settings
from app.api import deps

router = APIRouter()

@router.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)) -> Any:
    try:
        # Create the upload directory if it doesn't exist
        upload_dir = settings.UPLOAD_DIR
        os.makedirs(upload_dir, exist_ok=True)

        # Generate a unique filename to prevent overwrites
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)

        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Return the URL to access the file
        # Assuming files are served statically from /static/uploads
        return {"filename": unique_filename, "url": f"/static/uploads/{unique_filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not upload file: {e}")
