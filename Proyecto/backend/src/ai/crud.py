from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models import Users, ExcelInformation
from openpyxl.styles import Border, Side
from io import BytesIO
import pandas as pd



def generate_excel(user_email, db: Session):
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
                except:
                    pass
            adjusted_width = max_length + 2  
            worksheet.column_dimensions[column].width = adjusted_width

        
        for row in worksheet.iter_rows(min_row=2, max_row=len(df)+1, min_col=1, max_col=worksheet.max_column):  # Empieza desde la fila 2 si tienes encabezados
            for cell in row:
                cell.border = thin_border

    output.seek(0)
    return output