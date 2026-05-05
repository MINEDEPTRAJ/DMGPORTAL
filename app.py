import pandas as pd
import qrcode
from fpdf import FPDF
from flask import Flask, render_template_string, request, send_file
import os

app = Flask(__name__)

DISCLAIMER = "Note: This is a private verification portal for document processing. Not an official Government website."

def generate_pdf(row):
    qr_text = f"TP No: {row['Rawana No']}\nVehicle: {row['Vehicle No']}\nDate: {row['Date & Time of Confirmation']}"
    qr_img = qrcode.make(qr_text)
    qr_path = "temp_qr.png"
    qr_img.save(qr_path)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Transit Pass Status", ln=True, align='C')
    pdf.ln(10)
    
    # Matching the structure from your reference image
    columns = [
        ('Transit Pass No', 'Rawana No'),
        ('Source Name', 'Source Name'),
        ('Vehicle No', 'Vehicle No'),
        ('Generated on', 'Date & Time of Confirmation'),
        ('Mineral', 'Mineral Type'),
        ('Net Mineral Weight', 'Net Mineral Weight')
    ]
    
    pdf.set_font("Arial", 'B', 10)
    for label, key in columns:
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(70, 8, txt=f"{label}:", border=1)
        pdf.set_font("Arial", '', 10)
        pdf.cell(120, 8, txt=str(row[key]), border=1, ln=True)

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
                    error_msg = f"No record found for number: {royalty_no}"
            except Exception as e:
                error_msg = f"Error reading Excel: {str(e)}"
        else:
            error_msg = "Database file (data.xlsx) not found."

    html_content = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GMDRAJ: Royalty Verification</title>
    <style>
        body { font-family: sans-serif; background: #f4f7f6; display: flex; justify-content: center; padding: 20px; }
        .container { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); width: 100%; max-width: 600px; }
        h2 { color: #2c3e50; text-align: center; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        input { width: 100%; padding: 12px; margin: 15px 0; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; font-size: 16px; }
        .btn { width: 100%; padding: 14px; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; font-weight: bold; }
        .btn-view { background: #3498db; color: white; }
        .btn-down { background: #27ae60; color: white; margin-top: 20px; }
        .result-table { width: 100%; margin-top: 25px; border-collapse: collapse; background: #fafafa; }
        .result-table td { padding: 12px; border: 1px solid #eee; font-size: 14px; }
        .label { font-weight: bold; color: #34495e; background: #ecf0f1; width: 40%; }
        .error { color: #e74c3c; text-align: center; font-weight: bold; margin-top: 10px; }
        .footer { font-size: 11px; color: #95a5a6; margin-top: 40px; text-align: center; border-top: 1px solid #eee; padding-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Royalty Verification Status</h2>
        <form method="post">
            <input type="text" name="royalty_no" placeholder="Enter Rawana Number (e.g. VNMI...)" required>
            <button type="submit" class="btn btn-view">View Details</button>
        </form>

        {% if error %} <p class="error">{{ error }}</p> {% endif %}

        {% if data %}
        <div id="preview">
            <table class="result-table">
                <tr><td class="label">Transit Pass No</td><td>{{ data['Rawana No'] }}</td></tr>
                <tr><td class="label">Source Name</td><td>{{ data['Source Name'] }}</td></tr>
                <tr><td class="label">Vehicle No</td><td>{{ data['Vehicle No'] }}</td></tr>
                <tr><td class="label">Generated Date</td><td>{{ data['Date & Time of Confirmation'] }}</td></tr>
                <tr><td class="label">Mineral</td><td>{{ data['Mineral Type'] }}</td></tr>
                <tr><td class="label">Net Weight</td><td>{{ data['Net Mineral Weight'] }}</td></tr>
            </table>
            
            <form method="post">
                <input type="hidden" name="royalty_no" value="{{ data['Rawana No'] }}">
                <input type="hidden" name="download" value="true">
                <button type="submit" class="btn btn-down">Download PDF Receipt</button>
            </form>
        </div>
        {% endif %}

        <div class="footer">
            {{ disclaimer }}
        </div>
    </div>
</body>
</html>
    '''
    return render_template_string(html_content, data=data, error=error_msg, disclaimer=DISCLAIMER)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
