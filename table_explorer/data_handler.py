import pandas as pd
import numpy as np
from fastapi import HTTPException

from table_explorer.file_handler import find_file


def list_sheets(file_name):
    file_path = find_file(file_name)

    if not file_name.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="File is not an Excel file")

    try:
        excel_file = pd.ExcelFile(file_path)
        return {"sheets": excel_file.sheet_names}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error reading Excel file: {str(e)}"
        )


def load_table(file_name, sheet_name=None):
    file_path = find_file(file_name)

    if file_name.endswith(".csv"):
        return pd.read_csv(file_path)

    if file_name.endswith(".xlsx"):
        excel_file = pd.ExcelFile(file_path)
        if not sheet_name:
            sheet_name = excel_file.sheet_names[0]
        if sheet_name not in excel_file.sheet_names:
            raise HTTPException(
                status_code=400, detail=f"Sheet '{sheet_name}' not found in {file_name}"
            )
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        if df is None or df.empty:
            raise HTTPException(
                status_code=400,
                detail=f"Sheet '{sheet_name}' is empty or could not be loaded",
            )
        return df

    if file_name.endswith(".sas7bdat"):
        return pd.read_sas(file_path)

    if file_name.endswith(".xpt"):
        try:
            return pd.read_sas(file_path, format="xport")
        except ValueError as e:
            try:
                new_file_path = file_path.replace(".xpt", ".cpt")
                return pd.read_sas(new_file_path, format="cpt")
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error reading .xpt or .cpt file: {str(e)}. The file may be corrupted or not in the "
                    f"expected SAS format.",
                )

    raise HTTPException(status_code=400, detail="Unsupported file format")


def sanitize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.replace([np.inf, -np.inf], None)
    df = df.fillna(value="")
    return df


def format_data(df, rows, file_name=None):
    if file_name and file_name.endswith((".xls", ".xlsx")):
        df = pd.read_excel(file_name, header=0)
    else:
        df = pd.DataFrame(df)
    return {
        "columns": list(df.columns),
        "data": df.head(rows).to_dict(orient="records"),
    }


def preview_file(file_name: str, rows: int = 10, sheet_name=None):
    df_or_dict = load_table(file_name, sheet_name)

    df_or_dict = sanitize_dataframe(df_or_dict)

    if df_or_dict is None:
        raise HTTPException(
            status_code=500, detail="Data could not be loaded, received None"
        )

    if isinstance(df_or_dict, dict):
        return {
            "sheets": {sheet: format_data(df, rows) for sheet, df in df_or_dict.items()}
        }
    else:
        return format_data(df_or_dict, rows)
