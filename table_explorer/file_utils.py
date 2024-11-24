import os
import shutil
import zipfile

from fastapi import HTTPException


def save_file(file, directory):
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return file_path


def extract_archive(archive_path, extract_to):
    os.makedirs(extract_to, exist_ok=True)
    if not zipfile.is_zipfile(archive_path):
        raise HTTPException(
            status_code=400,
            detail=f"The file {archive_path} is not a valid ZIP archive"
        )
    with zipfile.ZipFile(archive_path, "r") as z:
        z.extractall(extract_to)
