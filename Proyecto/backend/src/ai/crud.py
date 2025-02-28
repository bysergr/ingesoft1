"""
CRUD operations for handling user data and Excel file generation.

This module provides functions to:
- Retrieve data from a database and generate an Excel file.
- Extract relevant product data using OpenAI's GPT-4o-mini model.
- Save extracted data into the database.

Dependencies:
- SQLAlchemy for database interactions.
- FastAPI's HTTPException for error handling.
- OpenAI's API for data extraction.
- Pandas and OpenPyXL for Excel file processing.
"""

import os
from io import BytesIO
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models import Users, ExcelInformation
from openpyxl.styles import Border, Side
import pandas as pd
import requests


def generate_excel(user_email: str, db: Session) -> BytesIO:
    """
    Generates an Excel file containing product information associated with a user.

    This function retrieves product data from the database based on the user's email 
    and creates an Excel file formatted with borders and column width adjustments.

    Args:
        user_email (str): The email of the user whose data should be retrieved.
        db (Session): The database session.

    Returns:
        BytesIO: An in-memory Excel file.

    Raises:
        HTTPException: If the user or associated data is not found in the database.
    """
    
    user_record = db.query(Users).filter(Users.email == user_email).first()
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")
    
    excel_data = db.query(ExcelInformation).filter(ExcelInformation.user_id == user_record.id).all()

    if not excel_data:
        raise HTTPException(status_code=404, detail="No data found for this user")

    data = {
        "Nombre del Producto": [],
        "Código HS": [],
        "Origen del País": [],
        "Impuestos IGI (Tasa Máxima)": [],
        "Impuestos IGI (Reducciones aplicables)": [],
        "IVA (%)": [],
        "DTA (%)": [],
        "NOMs": [],
        "COFEPRIS": [],
    }

    seen_hs_codes = set()

    for record in excel_data:
        hs_code = str(record.hs_code).replace("{", "").replace("}", "").replace('"', '')
        
        if hs_code not in seen_hs_codes:
            data["Nombre del Producto"].append(record.product_name)
            data["Código HS"].append(hs_code)
            data["Origen del País"].append(record.from_country)
            data["Impuestos IGI (Tasa Máxima)"].append(record.igi_max)
            data["Impuestos IGI (Reducciones aplicables)"].append(record.igi_reductions)
            data["IVA (%)"].append(record.iva)
            data["DTA (%)"].append(record.dta)
            data["NOMs"].append(record.noms)
            data["COFEPRIS"].append(record.cofepris)
            
            seen_hs_codes.add(hs_code)

    df = pd.DataFrame(data)
    output = BytesIO()

    thin_border = Border(left=Side(style='thin'), 
                         right=Side(style='thin'), 
                         top=Side(style='thin'), 
                         bottom=Side(style='thin'))

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, header=True)
        worksheet = writer.sheets['Sheet1']

        for col in worksheet.columns:
            max_length = 0
            column = col[0].column_letter  
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except TypeError:
                    pass
            adjusted_width = max_length + 2  
            worksheet.column_dimensions[column].width = adjusted_width

        for row in worksheet.iter_rows(min_row=2, max_row=len(df)+1, min_col=1, max_col=worksheet.max_column):
            for cell in row:
                cell.border = thin_border

    output.seek(0)
    return output


def get_data(search_text: str, noms: list, cofepris: str) -> dict:
    """
    Extracts structured product information from a text using OpenAI's GPT-4o-mini model.

    The function sends a request to OpenAI's API, providing a text search query and 
    regulatory information (NOMs and COFEPRIS). It expects the API to return a dictionary 
    containing details such as product name, HS Code, country of origin, and tax details.

    Args:
        search_text (str): The text input containing product details.
        noms (list): A list of NOMs applicable to the product.
        cofepris (str): COFEPRIS status for the product.

    Returns:
        dict: Extracted product information including tax details and regulatory data.

    Raises:
        requests.RequestException: If the API request fails.
        KeyError: If the API response structure is unexpected.
    """

    data_dict = {
        "NOMs": noms,
        "COFEPRIS": cofepris,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "You will give me a dict with the following keys: Nombre del Producto, HS Code, Origen del País, Impuestos IGI (Tasa Máxima), Impuestos IGI (Reducciones aplicables), IVA (%), DTA (%) and the values you will find in the search text. Please write the dict in the following format: {'Nombre del Producto': 'value', 'HS Code': 'value', 'Origen del País': 'value', 'Impuestos IGI (Tasa Máxima)': 'value', 'Impuestos IGI (Reducciones aplicables)': 'value', 'IVA (%)': 'value', 'DTA (%)': 'value'} and write the values in the search_text language if it is in English, write the values in English if it is in Spanish write the values in Spanish.",
                    },
                    {
                        "type": "text",
                        "text": search_text,
                    },
                ],
            }
        ],
        "max_tokens": 300,
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=30
    )

    data = response.json()

    agent_response = eval((data['choices'][0]['message']['content']).replace("```", "").replace("python", ""))

    data_dict.update(agent_response)

    return data_dict


def save_data_into_db(user_email: str, data: dict, db: Session) -> None:
    """
    Saves extracted product data into the database.

    This function associates the extracted product details with a user in the database
    and stores relevant information, such as HS Code, country of origin, and tax details.

    Args:
        user_email (str): The email of the user to associate the data with.
        data (dict): The structured product data to be saved.
        db (Session): The database session.

    Raises:
        HTTPException: If the user is not found in the database.
    """

    user_record = db.query(Users).filter(Users.email == user_email).first()
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")
    
    excel_data = ExcelInformation(
        user_id=user_record.id,
        product_name=data["Nombre del Producto"],
        hs_code=data["HS Code"],
        from_country=data["Origen del País"],
        igi_max=data["Impuestos IGI (Tasa Máxima)"],
        igi_reductions=data["Impuestos IGI (Reducciones aplicables)"],
        iva=data["IVA (%)"],
        dta=data["DTA (%)"],
        noms=data["NOMs"],
        cofepris=data["COFEPRIS"],
    )

    db.add(excel_data)
    db.commit()
