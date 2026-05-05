import pandas as pd
import qrcode
from fpdf import FPDF
from flask import Flask, render_template_string, request, send_file
import os

app = Flask(__name__)

# Basic App Information Text
APP_INFO_TEXT = """This is a personal royalty verification portal. Data is managed through a local database. Please ensure you are using correct royalty numbers."""

def generate_pdf(row):
    # PIL must be installed for qrcode.make to work
    try:
        qr_text = (
            f"TP No: {row['Rawana No']}\n"
            f"Generated: {row['Date & Time of Confirmation']}\n"
            f"Vehicle: {row['Vehicle No']}\n"
            f"Source: {row['Source Name']}\n"
            f"Mineral: {row['Mineral Type']}\n"
            f"Weight: {row['Net Mineral Weight']}"
        )
        qr_img = qrcode.make(qr_text)
        qr_path = "temp_qr.png"
        qr_img.save(qr_path)
    except ImportError:
        print("Error: Pillow library missing. Install it to enable QR codes.")
        qr_path = None

    pdf = FPDF()
    pdf.add_page()
    
    # PDF Content with dynamic data (using actual column names from image 3)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Transit Pass Verification", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(70, 8, txt="TP No (Rawana No):", border=1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(120, 8, txt=str(row['Rawana No']), border=1, ln=True)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(70, 8, txt="Source Name:", border=1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(120, 8, txt=str(row['Source Name']), border=1, ln=True)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(70, 8, txt="Vehicle No:", border=1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(120, 8, txt=str(row['Vehicle No']), border=1, ln=True)
    
    # Add QR code if PIL was available
    if qr_path and os.path.exists(qr_path):
        pdf.image(qr_path, x=80, y=pdf.get_y() + 10, w=50)

    output_name = f"Verify_{row['Rawana No']}.pdf"
    pdf.output(output_name)
    return output_name

@app.route('/', methods=['GET', 'POST'])
def index():
    error_msg = ""
    if request.method == 'POST':
        royalty_no = request.form.get('royalty_no')
        file_path = 'data.xlsx'
        
        if os.path.exists(file_path):
            try:
                df = pd.read_excel(file_path)
                # Verify column name match from image 3: 'Rawana No'
                match = df[df['Rawana No'].astype(str) == str(royalty_no)]
                if not match.empty:
                    pdf_path = generate_pdf(match.iloc[0])
                    return send_file(pdf_path, as_attachment=True)
                else:
                    error_msg = f"No record found for TP No {royalty_no}."
            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
        else:
            error_msg = "Critical error: Database file (data.xlsx) not found on server."

    html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DMG Rajasthan: Royalty Verification</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; margin: 0; padding: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; }
        .container { background-color: #fff; padding: 40px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); text-align: center; max-width: 500px; width: 90%; }
        h1 { color: #2c3e50; margin-bottom: 30px; font-weight: 600; }
        p.state { color: #34495e; font-size: 1.1em; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 1px;}
        input[type="text"] { padding: 15px; width: 100%; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; margin-bottom: 20px; font-size: 1em; }
        button { padding: 15px 30px; background-color: #34495e; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1.1em; transition: background-color 0.3s; }
        button:hover { background-color: #2c3e50; }
        .info-box { border-top: 1px solid #ddd; margin-top: 40px; padding-top: 20px; text-align: left; }
        .info-title { color: #7f8c8d; font-size: 0.9em; font-weight: bold; margin-bottom: 10px; text-transform: uppercase;}
        .info-text { color: #95a5a6; font-size: 0.85em; line-height: 1.6; }
        .error-message { color: #e74c3c; margin-bottom: 20px; font-weight: bold;}
    </style>
</head>
<body>
    <div class="container">
        <p class="state">Rajasthan</p>
        <h1>Royalty Verification Status</h1>
        {% if error %}
            <p class="error-message">{{ error }}</p>
        {% endif %}
        <form method="post">
            <input type="text" name="royalty_no" placeholder="Enter Royalty No (Rawana No)..." required>
            <button type="submit">Download Verification PDF</button>
        </form>
        <div class="info-box">
            <div class="info-title">App Information</div>
            <div class="info-text">{{ app_info }}</div>
        </div>
    </div>
</body>
</html>
    '''
    return render_template_string(html_content, app_info=APP_INFO_TEXT, error=error_msg)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
