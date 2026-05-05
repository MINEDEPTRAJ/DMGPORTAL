import pandas as pd
import qrcode
from fpdf import FPDF
from flask import Flask, render_template, request, send_file
import os

app = Flask(__name__)

def generate_pdf(row):
    # QR Code data creation
    qr_text = (
        f"Generated Date: {row['Date & Time of Confirmation']}\n"
        f"Vehicle No: {row['Vehicle No']}\n"
        f"Source Name: {row['Source Name']}\n"
        f"Mineral: {row['Mineral Type']}\n"
        f"Weight: {row['Net Mineral Weight']}\n"
        f"Consignee: {row['Consignee Name']}"
    )
    
    qr_img = qrcode.make(qr_text)
    # Render par temp file seedha folder mein save hogi
    qr_path = "temp_qr.png"
    qr_img.save(qr_path)

    pdf = FPDF()
    pdf.add_page()
    
    # 1. Outer Border
    pdf.rect(5, 5, 200, 287) 
    
    # 3. Header Text
    pdf.set_font("Arial", 'B', 12)
    pdf.set_y(12)
    pdf.cell(200, 8, txt="Government of Rajasthan", ln=True, align='C')
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(200, 8, txt="DEPARTMENT OF MINING & GEOLOGY, RAJASTHAN", ln=True, align='C')
    
    # 4. Right Side QR Code
    pdf.image(qr_path, x=170, y=10, w=30)
    
    pdf.ln(18)
    
    # Title Section
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(190, 10, txt="TRANSIT PASS STATUS", ln=True, align='C', fill=True)
    pdf.ln(5)

    # Details Table
    def add_row(label, value):
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(70, 8, txt=f" {label}", border=1)
        pdf.set_font("Arial", '', 9)
        pdf.cell(120, 8, txt=f" {value}", border=1, ln=True)

    add_row("Transit Pass No", str(row['Rawana No']))
    add_row("Generated on", str(row['Date & Time of Confirmation']))
    add_row("Source Name", str(row['Source Name']))
    add_row("Location", str(row['Address']))
    add_row("Mineral", str(row['Mineral Type']))
    add_row("Net Mineral Weight", str(row['Net Mineral Weight']))
    add_row("Consignee Name", str(row['Consignee Name']))
    add_row("Consignee Address", str(row['Consignee Address']))
    add_row("Vehicle No", str(row['Vehicle No']))

    output_name = f"TransitPass_{row['Rawana No']}.pdf"
    pdf.output(output_name)
    return output_name

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        royalty_no = request.form.get('royalty_no')
        # Render par file seedha folder mein honi chahiye
        file_path = 'data.xlsx'
        
        if os.path.exists(file_path):
            df = pd.read_excel(file_path) 
            match = df[df['Rawana No'].astype(str) == str(royalty_no)]
            if not match.empty:
                pdf_path = generate_pdf(match.iloc[0])
                return send_file(pdf_path, as_attachment=True)
            return f"Royalty Number {royalty_no} nahi mila!"
        return "Data file (data.xlsx) nahi mili!"

    return '''
        <div style="text-align: center; margin-top: 100px; font-family: sans-serif;">
            <h2>DMG Rajasthan: Royalty Portal</h2>
            <form method="post">
                <input type="text" name="royalty_no" placeholder="Enter Royalty No..." style="padding: 10px; width: 300px;" required>
                <br><br>
                <input type="submit" value="Download Receipt" style="padding: 10px 20px; background-color: #2c3e50; color: white; border: none; cursor: pointer;">
            </form>
        </div>
    '''

if __name__ == '__main__':
    # Render ke liye port aur host define karna zaroori hai
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
