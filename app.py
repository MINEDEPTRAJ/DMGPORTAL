import pandas as pd
import qrcode
from fpdf import FPDF
from flask import Flask, render_template_string, request, send_file
import os

app = Flask(__name__)

# Disclaimer text for safety
DISCLAIMER = "Note: This is a private verification portal for document processing. Not an official Government website."

def generate_pdf(row):
    qr_text = f"TP No: {row['Rawana No']}\nVehicle: {row['Vehicle No']}\nDate: {row['Date & Time of Confirmation']}"
    qr_img = qrcode.make(qr_text)
    qr_path = "temp_qr.png"
    qr_img.save(qr_path)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Royalty Verification Pass", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 10)
    columns = ['Rawana No', 'Source Name', 'Vehicle No', 'Date & Time of Confirmation', 'Mineral Type', 'Net Mineral Weight']
    for col in columns:
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(70, 8, txt=f"{col}:", border=1)
        pdf.set_font("Arial", '', 10)
        pdf.cell(120, 8, txt=str(row[col]), border=1, ln=True)

    pdf.ln(10)
    if os.path.exists(qr_path):
        pdf.image(qr_path, x=75, y=pdf.get_y(), w=50)

    output_name = f"Verify_{row['Rawana No']}.pdf"
    pdf.output(output_name)
    return output_name

@app.route('/', methods=['GET', 'POST'])
def index():
    data = None
    error_msg = ""
    
    if request.method == 'POST':
        royalty_no = request.form.get('royalty_no')
        download = request.form.get('download')
        file_path = 'data.xlsx'
        
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            match = df[df['Rawana No'].astype(str) == str(royalty_no)]
            
            if not match.empty:
                row = match.iloc[0]
                # Agar user ne Download button dabaya hai
                if download == "true":
                    pdf_file = generate_pdf(row)
                    return send_file(pdf_file, as_attachment=True)
                # Agar sirf search kiya hai toh data show karein
                data = row.to_dict()
            else:
                error_msg = "No record found for this number."
        else:
            error_msg = "Database file missing."

    html_content = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Royalty Verification</title>
    <style>
        body { font-family: sans-serif; background: #f0f2f5; display: flex; justify-content: center; padding: 20px; }
        .card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); width: 100%; max-width: 500px; }
        h2 { color: #1a73e8; text-align: center; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; }
        .btn { width: 100%; padding: 12px; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; font-weight: bold; }
        .btn-search { background: #1a73e8; color: white; }
        .btn-download { background: #34a853; color: white; margin-top: 20px; }
        .result-table { width: 100%; margin-top: 20px; border-collapse: collapse; }
        .result-table td { padding: 10px
