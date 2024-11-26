# Data viewer
The application provides functionality for uploading and previewing files in various data formats, including Excel, CSV, SAS, and archives, with the ability to retrieve information about the files and their contents through a user-friendly API.
##  Installation:
Python3 must be already installed

### 1.Clone the Repository:
```shell
git clone https://github.com/svitlana-savikhina/data-viewer.git
cd data-viewer
```
### 2.Activate venv:
```shell
python -m venv venv
source venv/bin/activate (Linux/Mac)
venv\Scripts\activate (Windows)
```
### 3.Install Dependencies:
```shell
pip install -r requirements.txt
```

### 4.Run:
```shell
uvicorn main:app --reload
```
This will start the FastAPI server and make the application available at http://127.0.0.1:8000.

Automatic API documentation generation for http://127.0.0.1:8000/docs