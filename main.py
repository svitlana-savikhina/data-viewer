from fastapi import FastAPI, UploadFile, File

from table_explorer.data_handler import (
    preview_file,
    list_sheets,
)
from table_explorer.file_handler import handle_archive, list_files

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/upload", description="Upload a ZIP archive.")
def upload_archive(file: UploadFile = File(...)):
    return handle_archive(file)


@app.get("/files", description="Retrieve a list of all files available in the data directory.")
def get_files():
    return list_files()


@app.get("/data/{file_name}/sheets", description="List all sheet names in an Excel file.")
def get_sheets(file_name: str):
    return list_sheets(file_name)


@app.get("/data/{file_name}", description="Preview the contents of a file.")
def preview_data(file_name: str, rows: int = 10, sheet_name=None):
    return preview_file(file_name, rows, sheet_name)
