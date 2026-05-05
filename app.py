import pandas as pd
import qrcode
from fpdf import FPDF
from flask import Flask, render_template_string, request, send_file
import os

app = Flask(__name__)

DISCLAIMER = "Note: This is a private verification portal. Not an official Government website."

# All fields as per your provided image
COLUMNS_TO_SHOW = [
    ('Transit Pass No', 'Rawana No'),
    ('Generated on', 'Date & Time of Confirmation'),
    ('Source Name', 'Source Name'),
    ('Location', 'Location'),
    ('Mineral', 'Mineral Type'),
    ('Net Mineral Weight', 'Net Mineral Weight'),
    ('Consignee Name', 'Consignee Name'),
    ('Consignee Address', 'Consignee Address'),
    ('Vehicle No', 'Vehicle No')
]

def generate_pdf(row):
    qr_text = f"TP No: {row['Rawana No']}\nVehicle: {row['Vehicle No']}\nDate: {row['Date & Time of Confirmation']}"
    qr_img = qrcode.make(qr_text)
    qr_path = "temp_qr.png"
    qr_img.save(qr_path)

    pdf = FPDF()
    pdf.add_page()
    pdf.rect(5, 5, 200, 287) # Border

    # Header Left: Logo
    if os.path.exists('logo.jpeg'):
        pdf.image('logo.jpeg', x=10, y=10, w=25)
    
    # Header Right: QR Code
    if os.path.exists(qr_path):
        pdf.image(qr_path, x=170, y=10, w=25)

    # Center Titles
    pdf.set_y(15)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="RAJASTHAN", ln=True, align='C')
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, txt="DEPARTMENT OF MINING & GEOLOGY", ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="TRANSIT PASS STATUS", border=1, ln=True, align='C', fill=True)

    # Data Table
    pdf.set_font("Arial", '', 10)
    for label, key in COLUMNS_TO_SHOW:
        val = str(row.get(key, 'N/A'))
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(70, 9, txt=f" {label}", border=1)
        pdf.set_font("Arial", '', 10)
        pdf.cell(120, 9, txt=f" {val}", border=1, ln=True)

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
                    error_msg = f"Record not found for: {royalty_no}"
            except Exception as e:
                error_msg = f"Error: {str(e)}"
        else:
            error_msg = "data.xlsx not found."

    html_content = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Royalty Portal</title>
    <style>
        body { font-family: sans-serif; background: #f4f7f6; padding: 20px; display: flex; justify-content: center; }
        .card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); width: 100%; max-width: 600px; }
        .header { text-align: center; border-bottom: 2px solid #2980b9; margin-bottom: 20px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; }
        .btn { width: 100%; padding: 12px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; }
        .btn-view { background: #2980b9; color: white; }
        .btn-down { background: #27ae60; color: white; margin-top: 20px; }
        .table { width: 100%; margin-top: 15px; border-collapse: collapse; font-size: 14px; }
        .table td { padding: 10px; border: 1px solid #eee; }
        .label { font-weight: bold; background: #f9f9f9; width: 40%; }
        .footer { font-size: 10px; text-align: center; color: #999; margin-top: 30px; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header"><h2>RAJASTHAN</h2><p>Mining & Geology Department</p></div>
        <form method="post">
            <input type="text" name="royalty_no" placeholder="Enter Transit Pass No..." required>
            <button type="submit" class="btn btn-view">Check Status</button>
        </form>
        {% if error %} <p style="color:red; text-align:center;">{{ error }}</p> {% endif %}
        {% if data %}
        <table class="table">
            {% for label, key in columns %}
            <tr><td class="label">{{ label }}</td><td>{{ data[key] }}</td></tr>
            {% endfor %}
        </table>
        <form method="post">
            <input type="hidden" name="royalty_no" value="{{ data['Rawana No'] }}">
            <input type="hidden" name="download" value="true">
            <button type="submit" class="btn btn-down">Download PDF Receipt</button>
        </form>
        {% endif %}
        <div class="footer">{{ disclaimer }}</div>
    </div>
</body>
</html>
'''
    return render_template_string(html_content, data=data, error=error_msg, disclaimer=DISCLAIMER, columns=COLUMNS_TO_SHOW)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
