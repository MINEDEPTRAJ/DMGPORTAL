import pandas as pd
import qrcode
from fpdf import FPDF
from flask import Flask, render_template, request, send_file
import os

app = Flask(__name__)

def generate_pdf(row):
    # QR Code data with local details (No online link)
    qr_text = (
        f"Generated Date: {row['Date & Time of Confirmation']}\n"
        f"Source Name: {row['Source Name']}\n"
        f"Location: {row['Address']}\n"
        f"Mineral: {row['Mineral Type']}\n"
        f"Weight: {row['Net Mineral Weight']}\n"
        f"Consignee: {row['Consignee Name']}\n"
        f"Address: {row['Consignee Address']}"
    )
    
    qr_img = qrcode.make(qr_text)
    qr_img.save("temp_qr.png")

    pdf = FPDF()
    pdf.add_page()
    
    # Header: Government of Rajasthan
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 8, txt="Government of Rajasthan", ln=True, align='C')
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(200, 8, txt="DEPARTMENT OF MINING & GEOLOGY, RAJASTHAN", ln=True, align='C')
    pdf.ln(5)
    
    # Title Section
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(190, 10, txt="TRANSIT PASS STATUS", ln=True, align='C', fill=True)
    pdf.ln(5)

    # Status Line
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(190, 8, txt=f"Transit Pass No. {row['Rawana No']} (Confirmed)", align='L')
    pdf.ln(2)

    # Table Layout
    def add_row(label, value):
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(70, 8, txt=f" {label}", border=1)
        pdf.set_font("Arial", '', 9)
        pdf.cell(120, 8, txt=f" {value}", border=1, ln=True)

    add_row("Generated on", str(row['Date & Time of Confirmation']))
    add_row("Confirmed on", str(row['Date & Time of Confirmation']))
    add_row("Source Name", str(row['Source Name']))
    add_row("Location", str(row['Address']))
    add_row("Mineral", str(row['Mineral Type']))
    add_row("Net Mineral Weight", str(row['Net Mineral Weight']))
    add_row("Consignee Name", str(row['Consignee Name']))
    add_row("Consignee Address", str(row['Consignee Address']))

    # QR Position: Side mein hi, table se sirf 5mm niche
    current_y = pdf.get_y()
    pdf.image("temp_qr.png", x=145, y=current_y + 5, w=45) 
    
    pdf.set_y(current_y + 55) 
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(200, 10, txt="Scan this QR code to verify Rawana details.", ln=True, align='L')

    output_name = f"TransitPass_{row['Rawana No']}.pdf"
    pdf.output(output_name)
    return output_name

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_val = request.form.get('search_val')
        if os.path.exists('data.xlsx'):
            df = pd.read_excel('data.xlsx') 
            match = df[df['Rawana No'].astype(str) == str(search_val)]
            if not match.empty:
                pdf_path = generate_pdf(match.iloc[0])
                return send_file(pdf_path, as_attachment=True)
            return f"Rawana No {search_val} nahi mila!"
        return "Excel file (data.xlsx) nahi mili!"

    return '''
        <div style="text-align: center; margin-top: 100px; font-family: sans-serif;">
            <h2 style="color: #2c3e50;">DMG Rajasthan: Rawana Portal</h2>
            <form method="post">
                <input type="text" name="search_val" placeholder="Enter Rawana No..." style="padding: 10px; width: 250px;" required>
                <br><br>
                <input type="submit" value="Download Transit Pass" style="padding: 10px 20px; background-color: #2c3e50; color: white; border: none; cursor: pointer;">
            </form>
        </div>
    '''

if __name__ == '__main__':
    app.run(debug=True)