import pandas as pd
import qrcode
from fpdf import FPDF
from flask import Flask, render_template_string, request, send_file
import os

app = Flask(__name__)

DISCLAIMER = "Note: This is a private verification portal for document processing. Not an official Government website."

def generate_pdf(row):
    # QR Code generation
    qr_text = f"TP No: {row['Rawana No']}\nVehicle: {row['Vehicle No']}\nDate: {row['Date & Time of Confirmation']}"
    qr_img = qrcode.make(qr_text)
    qr_path = "temp_qr.png"
    qr_img.save(qr_path)

    pdf = FPDF()
    pdf.add_page()
    
    # 1. Professional Border
    pdf.rect(5, 5, 200, 287) 

    # 2. Header: Logo (Left) and QR (Right)
    if os.path.exists('logo.png'):
        pdf.image('logo.png', x=10, y=10, w=25)
    
    if os.path.exists(qr_path):
        pdf.image(qr_path, x=170, y=10, w=25) # QR Code in Header Right Side

    # 3. Center Titles
    pdf.set_y(15)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="RAJASTHAN", ln=True, align='C') # Updated Heading
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, txt="DEPARTMENT OF MINING & GEOLOGY", ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="TRANSIT PASS STATUS", border=1, ln=True, align='C', fill=True)

    # 4. Data Table
    columns = [
        ('Transit Pass No', 'Rawana No'),
        ('Generated on', 'Date & Time of Confirmation'),
        ('Source Name', 'Source Name'),
        ('Mineral', 'Mineral Type'),
        ('Net Mineral Weight', 'Net Mineral Weight'),
        ('Vehicle No', 'Vehicle No')
    ]

    pdf.set_font("Arial", '', 10)
    for label, key in columns:
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(70, 10, txt=f" {label}", border=1)
        pdf.set_font("Arial", '', 10)
        pdf.cell(120, 10, txt=f" {str(row[key])}", border=1, ln=True)

    output_name = f"TransitPass_{row['Rawana No']}.pdf"
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
            try:
                df = pd.read_excel(file_path)
                match = df[df['Rawana No'].astype(str) == str(royalty_no)]
                
                if not match.empty:
                    row = match.iloc[0]
                    if download == "true":
                        pdf_file = generate_pdf(row)
                        return send_file(pdf_file, as_attachment=True)
                    data = row.to_dict()
                else:
                    error_msg = f"No record found for: {royalty_no}"
            except Exception as e:
                error_msg = f"System Error: {str(e)}"
        else:
            error_msg = "Database file missing."

    html_content = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DMG Rajasthan: Portal</title>
    <style>
        body { font-family: sans-serif; background: #f0f2f5; margin: 0; padding: 20px; display: flex; justify-content: center; }
        .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); width: 100%; max-width: 600px; }
        .header-box { text-align: center; border-bottom: 2px solid #2980b9; margin-bottom: 20px; padding-bottom: 10px; }
        h2 { color: #2c3e50; margin: 0; }
        input { width: 100%; padding: 14px; margin: 15px 0; border: 1px solid #ccc; border-radius: 8px; font-size: 16px; box-sizing: border-box; }
        .btn { width: 100%; padding: 14px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; }
        .btn-view { background: #2980b9; color: white; }
        .btn-down { background: #27ae60; color: white; margin-top: 25px; }
        .preview-table { width: 100%; margin-top: 20px; border-collapse: collapse; }
        .preview-table td { padding: 12px; border: 1px solid #eee; font-size: 14px; }
        .label { font-weight: bold; color: #7f8c8d; background: #f9f9f9; width: 40%; }
        .error { color: #e74c3c; text-align: center; margin-top: 15px; font-weight: bold; }
        .footer { font-size: 11px; color: #bdc3c7; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 10px; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header-box">
            <h2>RAJASTHAN</h2>
            <p style="margin:5px 0; font-size:14px; color:#34495e;">Department of Mining & Geology</p>
        </div>
        
        <form method="post">
            <input type="text" name="royalty_no" placeholder="Enter Rawana Number..." required>
            <button type="submit" class="btn btn-view">View Details</button>
        </form>

        {% if error %} <p class="error">{{ error }}</p> {% endif %}

        {% if data %}
        <div id="result">
            <table class="preview-table">
                <tr><td class="label">Transit Pass No</td><td>{{ data['Rawana No'] }}</td></tr>
                <tr><td class="label">Vehicle No</td><td>{{ data['Vehicle No'] }}</td></tr>
                <tr><td class="label">Mineral</td><td>{{ data['Mineral Type'] }}</td></tr>
                <tr><td class="label">Weight</td><td>{{ data['Net Mineral Weight'] }}</td></tr>
            </table>
            
            <form method="post">
                <input type="hidden" name="royalty_no" value="{{ data['Rawana No'] }}">
                <input type="hidden" name="download" value="true">
                <button type="submit" class="btn btn-down">Download PDF Pass</button>
            </form>
        </div>
        {% endif %}

        <div class="footer">{{ disclaimer }}</div>
    </div>
</body>
</html>
'''
    return render_template_string(html_content, data=data, error=error_msg, disclaimer=DISCLAIMER)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
