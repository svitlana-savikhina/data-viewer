from fastapi import FastAPI, UploadFile, File

from table_explorer.convert_TLF_Shells import split_tlf_shells
from table_explorer.data_handler import list_sheets, preview_file
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
    if file_name == "ADAM_spec.xlsx" and sheet_name == "_TLF_Shells":
        return split_tlf_shells(file_name)
    return preview_file(file_name, rows, sheet_name)

