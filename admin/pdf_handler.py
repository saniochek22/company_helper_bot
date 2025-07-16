import fitz  
import tempfile
from fastapi import UploadFile
from db import get_connection  

def extract_text_from_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.strip()

def process_pdf_upload(department_id: int, file: UploadFile) -> dict:
    # Сохраняем временно PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name

    # Извлекаем текст
    text = extract_text_from_pdf(tmp_path)

    # Обновляем в БД
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE departments SET description_for_ai = %s WHERE id = %s",
        (text, department_id)
    )
    conn.commit()
    cur.close()
    conn.close()

    return {"status": "ok", "extracted_length": len(text)}
