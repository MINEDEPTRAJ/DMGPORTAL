import os
import json
import pandas as pd
import qrcode
import requests
from io import StringIO
from fpdf import FPDF
from flask import Flask, render_template_string, request, send_file, jsonify

app = Flask(__name__)

# --- CONFIGURATION ---
DISCLAIMER = "Note: This is a private verification portal. Not an official Government website."
# Aapka Google Sheet CSV Link
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaWMgwd6zRTDTHqu8yQ1n9S1HsXWiy2h2Qw2OotyTAxG45pSnnyTWPRLQoNyjm_4o8AWmWIj7Fawp0/pub?output=csv"

# --- DATA LOADING FUNCTION ---
def load_live_data():
    try:
        response = requests.get(SHEET_URL)
        if response.status_code == 200:
            new_csv = StringIO(response.text)
            df = pd.read_csv(new_csv)
            # Column names se extra space hatane ke liye
            df.columns = df.columns.str.strip()
            return df
        return None
    except Exception as e:
        print(f"Error loading sheet: {e}")
        return None

# District list aur stats ke liye (Fallback data agar sheet load na ho)
DEFAULT_DISTRICT_DATA = {
    "Ajmer": {"major": 467, "minor": 440, "revenue": 14.33, "dmf": 5.03},
    # ... baki data sheet se automatically aayega
}

# --- VERIFICATION CONFIG ---
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
    if not isinstance(name, str) or not name.strip() or len(name) <= 1:
        return name
    return name[0] + "".join([" " if char == " " else "X" for char in name[1:-1]]) + name[-1]

def generate_pdf(row):
    qr_text = f"TP No: {row['Rawana No']}\nDate: {row['Date & Time of Confirmation']}"
    qr_img = qrcode.make(qr_text); qr_path = "temp_qr.png"; qr_img.save(qr_path)
    pdf = FPDF(); pdf.add_page(); pdf.rect(5, 5, 200, 287)
    if os.path.exists('logo.jpeg'): pdf.image('logo.jpeg', x=10, y=10, w=25)
    if os.path.exists(qr_path): pdf.image(qr_path, x=170, y=10, w=25)
    pdf.set_y(15); pdf.set_font("Arial", 'B', 16); pdf.cell(0, 10, txt="RAJASTHAN", ln=True, align='C')
    pdf.set_font("Arial", 'B', 11); pdf.cell(0, 8, txt="DEPARTMENT OF MINING & GEOLOGY", ln=True, align='C')
    pdf.ln(10); pdf.set_fill_color(240, 240, 240); pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, txt="TRANSIT PASS STATUS", border=1, ln=True, align='C', fill=True)
    pdf.set_font("Arial", '', 10)
    for label, key in COLUMNS_TO_SHOW:
        val = str(row.get(key, 'N/A'))
        pdf.set_font("Arial", 'B', 10); pdf.cell(70, 9, txt=f" {label}", border=1)
        pdf.set_font("Arial", '', 10); pdf.cell(120, 9, txt=f" {val}", border=1, ln=True)
    output_name = f"TransitPass_{row['Rawana No']}.pdf"; pdf.output(output_name); return output_name

@app.route('/', methods=['GET', 'POST'])
def index():
    data = None; error_msg = ""
    df = load_live_data()
    
    # District stats prepare karein sheet se
    dist_stats = {}
    if df is not None:
        try:
            # Maan lete hain sheet mein 'District', 'major', 'minor', 'revenue', 'dmf' columns hain
            for _, r in df.iterrows():
                d_name = str(r.get('District', 'Unknown'))
                dist_stats[d_name] = {
                    "major": r.get('major', 0),
                    "minor": r.get('minor', 0),
                    "revenue": r.get('revenue', 0),
                    "dmf": r.get('dmf', 0)
                }
        except:
            dist_stats = DEFAULT_DISTRICT_DATA
    else:
        dist_stats = DEFAULT_DISTRICT_DATA

    if request.method == 'POST':
        royalty_no = request.form.get('royalty_no')
        download = request.form.get('download')
        
        if df is not None:
            try:
                match = df[df['Rawana No'].astype(str) == str(royalty_no)]
                if not match.empty:
                    row = match.iloc[0].copy()
                    if 'Consignee Name' in row: row['Consignee Name'] = mask_consignee_name(str(row['Consignee Name']))
                    if download == "true":
                        pdf_file = generate_pdf(row); return send_file(pdf_file, as_attachment=True)
                    data = row.to_dict()
                else: error_msg = f"Record not found for: {royalty_no}"
            except Exception as e: error_msg = f"Processing Error: {str(e)}"
        else: error_msg = "Could not connect to Google Sheets database."

    html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GMDRAJ</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #f0f4f7; margin: 0; }
        .nav { background: #003366; color: white; padding: 15px; text-align: center; font-weight: bold; display: flex; justify-content: space-between; align-items: center; padding: 10px 20px; }
        .switch-btn { background: #ff9800; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; font-weight: bold; }
        .container { max-width: 1100px; margin: 20px auto; padding: 0 20px; }
        .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .slide { background: #008080; color: white; border-radius: 12px; padding: 20px; margin-bottom: 20px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin-top: 15px; }
        .stat-box { background: rgba(255,255,255,0.2); padding: 10px; border-radius: 6px; text-align: center; border: 1px solid rgba(255,255,255,0.3); }
        .stat-box span { font-size: 11px; display: block; text-transform: uppercase; }
        .stat-box b { font-size: 18px; }
        .v-input { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 16px; margin-bottom: 15px; box-sizing: border-box; }
        .btn-blue { background: #2980b9; color: white; border: none; width: 100%; padding: 12px; border-radius: 8px; font-weight: bold; cursor: pointer; }
        .table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        .table td { padding: 10px; border: 1px solid #eee; font-size: 14px; }
        .label { background: #f8f9fa; font-weight: bold; width: 40%; }
        .hidden { display: none; }
    </style>
</head>
<body>
<div class="nav">
    <span>GMDRAJASTHAN</span>
    <button class="switch-btn" onclick="toggleInterface()">🔄 Switch Interface</button>
</div>

<div class="container">
    <div id="dashboard-ui">
        <div class="slide">
            <h2 style="margin:0;">RAJASTHAN STATE OVERVIEW</h2>
            <div class="stats-grid">
                <div class="stat-box"><span>Major Leases</span><b>3003</b></div>
                <div class="stat-box"><span>Minor Leases</span><b>13800</b></div>
                <div class="stat-box"><span>Rawanna</span><b>10.6L</b></div>
                <div class="stat-box"><span>Revenue</span><b>673.4Cr</b></div>
            </div>
        </div>
        <div class="card">
            <h3>District Specific Data</h3>
            <select style="width:100%; padding:10px;" id="distSelect" onchange="updateDistStats()">
                {% for dist in dist_list %}<option value="{{ dist }}">{{ dist }}</option>{% endfor %}
            </select>
            <div class="stats-grid" id="distDisplay" style="color: #333; margin-top:20px;"></div>
        </div>
    </div>

    <div id="verification-ui" class="hidden">
        <div class="card">
            <h2 style="text-align:center; color:#2c3e50;">Transit Pass Verification</h2>
            <form method="post">
                <input type="text" class="v-input" name="royalty_no" placeholder="Enter TP No (e.g. 2024...)" required>
                <button type="submit" class="btn-blue">Verify Now</button>
            </form>
            {% if error %}<div style="color:red; text-align:center; margin-top:10px;">{{ error }}</div>{% endif %}
            {% if data %}
            <div style="margin-top:20px;">
                <table class="table">
                    {% for label, key in columns %}
                    <tr><td class="label">{{ label }}</td><td>{{ data[key] }}</td></tr>
                    {% endfor %}
                </table>
                <form method="post">
                    <input type="hidden" name="royalty_no" value="{{ data['Rawana No'] }}">
                    <input type="hidden" name="download" value="true">
                    <button type="submit" style="background:#27ae60;" class="btn-blue">⬇️ Download PDF</button>
                </form>
            </div>
            {% endif %}
        </div>
    </div>
    <div style="text-align:center; font-size:12px; color:#95a5a6; margin-top:20px;">{{ disclaimer }}</div>
</div>

<script>
    const allData = {{ json_data | safe }};
    function toggleInterface() {
        const d = document.getElementById('dashboard-ui');
        const v = document.getElementById('verification-ui');
        d.classList.toggle('hidden');
        v.classList.toggle('hidden');
    }
    function updateDistStats() {
        const d = document.getElementById('distSelect').value;
        const s = allData[d];
        if(!s) return;
        document.getElementById('distDisplay').innerHTML = `
            <div class="stat-box" style="background:#f1f1f1"><span>Major</span><b>${s.major}</b></div>
            <div class="stat-box" style="background:#f1f1f1"><span>Minor</span><b>${s.minor}</b></div>
            <div class="stat-box" style="background:#f1f1f1"><span>Revenue</span><b>${s.revenue}Cr</b></div>
            <div class="stat-box" style="background:#f1f1f1"><span>DMF</span><b>${s.dmf}Cr</b></div>
        `;
    }
    window.onload = function() {
        {% if data or error %} toggleInterface(); {% endif %}
        updateDistStats();
    };
</script>
</body>
</html>
'''
    return render_template_string(html_content, data=data, error=error_msg, disclaimer=DISCLAIMER, 
                                 columns=COLUMNS_TO_SHOW, dist_list=sorted(dist_stats.keys()), 
                                 json_data=json.dumps(dist_stats))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
