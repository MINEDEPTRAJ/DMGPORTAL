import pandas as pd
import qrcode
from fpdf import FPDF
from flask import Flask, render_template_string, request, send_file, send_from_directory
import os

app = Flask(__name__)

DISCLAIMER = "Note: This is a private verification portal. Not an official Government website."

# Vehicle No ko list se hata diya gaya hai
COLUMNS_TO_SHOW = [
    ('Transit Pass No', 'Rawana No'),
    ('Generated on', 'Date & Time of Confirmation'),
    ('Source Name', 'Source Name'),
    ('Location', 'Location'),
    ('Mineral', 'Mineral Type'),
    ('Net Mineral Weight', 'Net Mineral Weight'),
    ('Consignee Name', 'Consignee Name'),
    ('Consignee Address', 'Consignee Address')
]

def mask_consignee_name(name):
    """
    Example: 'SHRI KRISHNA' -> 'SXXX XXXXXXXA'
    Example: 'AAI MAA CONSTRUCTION' -> 'AXX XXX XXXXXXXXXXXN'
    """
    if not isinstance(name, str) or not name.strip():
        return name
    
    name = name.strip()
    if len(name) <= 1:
        return name
        
    first_char = name[0]
    last_char = name[-1]
    
    middle_part = ""
    for char in name[1:-1]:
        if char == " ":
            middle_part += " "
        else:
            middle_part += "X"
            
    return first_char + middle_part + last_char

def generate_pdf(row):
    # QR Code generation
    qr_text = f"TP No: {row['Rawana No']}\nDate: {row['Date & Time of Confirmation']}"
    qr_img = qrcode.make(qr_text)
    qr_path = "temp_qr.png"
    qr_img.save(qr_path)

    pdf = FPDF()
    pdf.add_page()
    pdf.rect(5, 5, 200, 287) 

    if os.path.exists('logo.jpeg'):
        pdf.image('logo.jpeg', x=10, y=10, w=25)
    
    if os.path.exists(qr_path):
        pdf.image(qr_path, x=170, y=10, w=25)

    pdf.set_y(15)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="RAJASTHAN", ln=True, align='C')
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, txt="DEPARTMENT OF MINING & GEOLOGY", ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="TRANSIT PASS STATUS", border=1, ln=True, align='C', fill=True)

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
                    row = match.iloc[0].copy()
                    if 'Consignee Name' in row:
                        row['Consignee Name'] = mask_consignee_name(str(row['Consignee Name']))
                    
                    if download == "true":
                        pdf_file = generate_pdf(row)
                        return send_file(pdf_file, as_attachment=True)
                    
                    data = row.to_dict()
                else:
                    error_msg = f"Record not found for: {royalty_no}"
            except Exception as e:
                error_msg = f"Error: {str(e)}"
        else:
            error_msg = "Database file (data.xlsx) missing."

    html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GMDRAJSER</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #eef2f3; margin: 0; display: flex; align-items: center; justify-content: center; min-height: 100vh; }
        .card { background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); width: 100%; max-width: 550px; border-top: 5px solid #2980b9; margin: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h2 { color: #2c3e50; margin: 0; letter-spacing: 2px; text-transform: uppercase; }
        .header p { color: #7f8c8d; margin: 5px 0; font-weight: 500; }
        .input-group { margin-bottom: 20px; }
        input[type="text"] { width: 100%; padding: 14px; border: 2px solid #ddd; border-radius: 8px; font-size: 16px; transition: border-color 0.3s; box-sizing: border-box; }
        input[type="text"]:focus { border-color: #2980b9; outline: none; }
        .btn { width: 100%; padding: 14px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; transition: background 0.3s; }
        .btn-view { background: #2980b9; color: white; margin-top: 10px; }
        .btn-view:hover { background: #1f6391; }
        .btn-down { background: #27ae60; color: white; margin-top: 25px; }
        .btn-down:hover { background: #219150; }
        .error { color: #e74c3c; background: #fdeaea; padding: 12px; border-radius: 5px; text-align: center; margin-top: 15px; font-size: 14px; border: 1px solid #f5c2c2; }
        .table-container { margin-top: 30px; border: 1px solid #eee; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        .table { width: 100%; border-collapse: collapse; background: #fff; }
        .table td { padding: 12px 15px; border-bottom: 1px solid #f1f1f1; font-size: 14px; }
        .label { background: #f8f9fa; color: #34495e; font-weight: 600; width: 45%; }
        .value { color: #2c3e50; }
        .footer { font-size: 11px; text-align: center; color: #95a5a6; margin-top: 40px; line-height: 1.5; border-top: 1px solid #eee; padding-top: 15px; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <h2>RAJASTHAN</h2>
            <p>GEOMINEDEP</p>
        </div>
        
        <form method="post">
            <div class="input-group">
                <input type="text" name="royalty_no" placeholder="Enter Transit Pass No..." required autofocus autocomplete="off">
            </div>
            <button type="submit" class="btn btn-view">Check Status</button>
        </form>

        {% if error %}
            <div class="error">⚠️ {{ error }}</div>
        {% endif %}

        {% if data %}
        <div class="table-container">
            <table class="table">
                {% for label, key in columns %}
                <tr>
                    <td class="label">{{ label }}</td>
                    <td class="value">{{ data[key] }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        <form method="post">
            <input type="hidden" name="royalty_no" value="{{ data['Rawana No'] }}">
            <input type="hidden" name="download" value="true">
            <button type="submit" class="btn btn-down">⬇️ Download PDF Receipt</button>
        </form>
        {% endif %}

        <div class="footer">
            {{ disclaimer }}<br>
            © 2026 All Rights Reserved.
        </div>
    </div>
</body>
</html>
'''
    return render_template_string(html_content, data=data, error=error_msg, disclaimer=DISCLAIMER, columns=COLUMNS_TO_SHOW)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    # ... aapka baaki purana code ...

# Naya code yahan paste karein
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(os.getcwd(), 'sitemap.xml')

# Ye hamesha sabse aakhiri mein hona chahiye
if __name__ == "__main__":
    app.run()
