from fastapi import HTTPException
import pandas as pd

from table_explorer.data_handler import sanitize_dataframe
from table_explorer.file_handler import find_file


def extract_metadata_and_data(df: pd.DataFrame):
    df = sanitize_dataframe(df)
    metadata = {
        "Project": df.iloc[0, 0] if pd.notna(df.iloc[0, 0]) else None,
        "Protocol": df.iloc[1, 0] if pd.notna(df.iloc[1, 0]) else None,
        "Page": df.iloc[0, 3] if pd.notna(df.iloc[0, 3]) else None,
        "Timestamp": df.iloc[1, 3] if pd.notna(df.iloc[1, 3]) else None,
        "Table": df.iloc[2, 1] if pd.notna(df.iloc[2, 1]) else None,
        "Title": df.iloc[3, 1] if pd.notna(df.iloc[3, 1]) else None,
        "Set": df.iloc[4, 1] if pd.notna(df.iloc[4, 1]) else None,
        "Note": None,
    }
    # Search for the row that starts with "Note" in the first column
    note_row_index = None
    for idx, row in df.iterrows():
        note_text = str(row[0]).strip()
        if note_text.startswith("Note"):
            note_row_index = idx
            metadata["Note"] = row[0]
            break

    # If "Note" wasn't found, set a default message
    if metadata["Note"] is None:
        metadata["Note"] = "No Note field found"

    # Remove the "Note" row from the data and proceed with data extraction
    if note_row_index is not None:
        df = df.drop(note_row_index)

    # Start of table data
    data_start_row = 5
    data = df.iloc[data_start_row:].reset_index(drop=True)

    # Removing empty rows and columns
    data = data.dropna(how="all").dropna(axis=1, how="all")
    data_dict = data.to_dict(orient="records")
    return {"metadata": metadata, "data": data_dict}


def split_tlf_shells(file_name: str):
    file_path = find_file(file_name)

    if not file_name.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="File is not an Excel file")

    try:
        excel_file = pd.ExcelFile(file_path)
        if "_TLF_Shells" not in excel_file.sheet_names:
            raise HTTPException(
                status_code=400,
                detail="Sheet '_TLF_Shells' not found in the Excel file",
            )

        df = pd.read_excel(file_path, sheet_name="_TLF_Shells", header=None)
        df = df.applymap(lambda x: x.replace("\xa0", " ") if isinstance(x, str) else x)

        # Find row indexes where the first cell contains "Test Project"
        split_indices = df[
            df.iloc[:, 0].str.contains("Test Project", na=False)
        ].index.tolist()
        split_indices.append(len(df))

        if len(split_indices) <= 1:
            raise HTTPException(
                status_code=400, detail="No 'Test Project' rows found for splitting"
            )

        # Split DataFrame into parts
        metadata_list = []
        data_list = []
        for i in range(len(split_indices) - 1):
            start, end = split_indices[i], split_indices[i + 1]
            chunk = df.iloc[start:end]

            # Remove columns where all values are null
            chunk = chunk.dropna(axis=0, how="all")
            chunk = chunk.dropna(axis=1, how="all")

            # Metadata and data extraction
            extracted = extract_metadata_and_data(chunk)
            metadata_list.append(extracted["metadata"])
            data_list.append(extracted["data"])

        response_data = [
            {"metadata": metadata_list[i], "data": data_list[i]}
            for i in range(len(metadata_list))
        ]

        return response_data

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing the file: {str(e)}"
        )
