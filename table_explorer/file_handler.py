import os
import zipfile

from fastapi import HTTPException

from table_explorer.file_utils import save_file, extract_archive

UPLOAD_DIR = "uploads"
DATA_DIR = "data"


def handle_archive(file):
    file_path = save_file(file, UPLOAD_DIR)
    if not zipfile.is_zipfile(file_path):
        raise HTTPException(
            status_code=400, detail="Uploaded file is not a valid ZIP archive"
        )
    extract_archive(file_path, DATA_DIR)
    return {"message": "Archive uploaded and extracted successfully"}


def list_files():
    files = []
    for root, dirs, files_in_dir in os.walk(DATA_DIR):
        for file in files_in_dir:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                files.append(file_path)
    return {"files": files}


def find_file(file_name, base_dir):

    for root, dirs, files in os.walk(base_dir):
        if file_name in files:
            return os.path.join(root, file_name)
    raise HTTPException(
        status_code=404,
        detail=f"File {file_name} not found in {base_dir} or its subdirectories",
    )
