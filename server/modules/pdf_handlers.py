import os
import shutil
from fastapi import UploadFile

UPLOAD_DIR = "./uploaded_docs"


def save_uploaded_files(files: list[UploadFile]) -> list[str]:
    """Save uploaded PDF files to disk. Returns list of saved file paths."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_paths: list[str] = []

    for file in files:
        dest_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(dest_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        file_paths.append(dest_path)

    return file_paths
