import os
import json
import pandas as pd
import qrcode
from fpdf import FPDF
from flask import Flask, render_template_string, request, send_file, jsonify

app = Flask(__name__)

DISCLAIMER = "Note: This is a private verification portal. Not an official Government website."

# --- DISTRICT DATA ---
DISTRICT_DATA = {
    "Ajmer": {"major": 467, "minor": 440, "quarry": 91, "stp": 368, "rawanna": 26920, "transit": 22012, "revenue": 14.33, "dmf": 5.03},
    "Alwar": {"major": 3, "minor": 321, "quarry": 0, "stp": 106, "rawanna": 25770, "transit": 14546, "revenue": 10.26, "dmf": 0.52},
    "Banswara": {"major": 6, "minor": 149, "quarry": 0, "stp": 25, "rawanna": 21793, "transit": 904, "revenue": 7.05, "dmf": 0.94},
    "Baran": {"major": 0, "minor": 45, "quarry": 0, "stp": 3, "rawanna": 8523, "transit": 11740, "revenue": 0.33, "dmf": 0.02},
    "Barmer": {"major": 15, "minor": 538, "quarry": 0, "stp": 97, "rawanna": 33312, "transit": 15284, "revenue": 6.37, "dmf": 2.24},
    "Beawar": {"major": 41, "minor": 136, "quarry": 0, "stp": 0, "rawanna": 27085, "transit": 1344, "revenue": 9.00, "dmf": 8.37},
    "Bharatpur": {"major": 0, "minor": 674, "quarry": 0, "stp": 40, "rawanna": 70008, "transit": 48437, "revenue": 8.26, "dmf": 0.14},
    "Bhilwara": {"major": 759, "minor": 700, "quarry": 1108, "stp": 43, "rawanna": 43961, "transit": 11386, "revenue": 145.8, "dmf": 6.78},
    "Bikaner": {"major": 5, "minor": 462, "quarry": 27, "stp": 438, "rawanna": 26630, "transit": 17, "revenue": 19.15, "dmf": 1.65},
    "Bundi": {"major": 2, "minor": 594, "quarry": 0, "stp": 12, "rawanna": 12331, "transit": 5436, "revenue": 4.96, "dmf": 0.14},
    "Chittorgarh": {"major": 224, "minor": 118, "quarry": 27, "stp": 12, "rawanna": 45353, "transit": 3865, "revenue": 33.72, "dmf": 5.48},
    "Churu": {"major": 0, "minor": 161, "quarry": 361, "stp": 105, "rawanna": 5957, "transit": 3266, "revenue": 1.94, "dmf": 0.19},
    "Dausa": {"major": 0, "minor": 204, "quarry": 2, "stp": 62, "rawanna": 12891, "transit": 10078, "revenue": 4.22, "dmf": 0.38},
    "Deedwana-Kuchaman": {"major": 0, "minor": 154, "quarry": 0, "stp": 0, "rawanna": 1406, "transit": 0, "revenue": 0.69, "dmf": 0.08},
    "Deeg": {"major": 0, "minor": 751, "quarry": 31, "stp": 33, "rawanna": 14812, "transit": 12423, "revenue": 4.54, "dmf": 0.33},
    "Dholpur": {"major": 0, "minor": 44, "quarry": 791, "stp": 270, "rawanna": 14467, "transit": 13327, "revenue": 6.84, "dmf": 0.44},
    "Dungarpur": {"major": 32, "minor": 305, "quarry": 0, "stp": 36, "rawanna": 11623, "transit": 12052, "revenue": 4.57, "dmf": 0.81},
    "Hanumangarh": {"major": 0, "minor": 3, "quarry": 0, "stp": 0, "rawanna": 1121, "transit": 0, "revenue": 0.17, "dmf": 0.01},
    "Jaisalmer": {"major": 30, "minor": 131, "quarry": 0, "stp": 138, "rawanna": 39589, "transit": 14101, "revenue": 17.59, "dmf": 4.61},
    "Jaipur": {"major": 0, "minor": 514, "quarry": 0, "stp": 144, "rawanna": 43577, "transit": 12151, "revenue": 12.18, "dmf": 1.25},
    "Jalore": {"major": 3, "minor": 801, "quarry": 0, "stp": 105, "rawanna": 23519, "transit": 20436, "revenue": 24.36, "dmf": 3.79},
    "Jhalawar": {"major": 0, "minor": 251, "quarry": 2529, "stp": 5, "rawanna": 22283, "transit": 23565, "revenue": 9.48, "dmf": 1.22},
    "Jhunjhunu": {"major": 22, "minor": 444, "quarry": 0, "stp": 113, "rawanna": 17565, "transit": 12836, "revenue": 26.24, "dmf": 2.21},
    "Jodhpur": {"major": 0, "minor": 470, "quarry": 3615, "stp": 128, "rawanna": 81046, "transit": 53046, "revenue": 25.04, "dmf": 4.14},
    "Karauli": {"major": 0, "minor": 30, "quarry": 2389, "stp": 272, "rawanna": 17409, "transit": 13978, "revenue": 7.15, "dmf": 0.44},
    "Kota": {"major": 0, "minor": 117, "quarry": 1362, "stp": 10, "rawanna": 23687, "transit": 12433, "revenue": 13.91, "dmf": 2.50},
    "Kotputli-Behror": {"major": 3, "minor": 257, "quarry": 0, "stp": 62, "rawanna": 45145, "transit": 31317, "revenue": 15.11, "dmf": 2.76},
    "Nagaur": {"major": 13, "minor": 511, "quarry": 0, "stp": 204, "rawanna": 37243, "transit": 13914, "revenue": 106.84, "dmf": 48.91},
    "Pali": {"major": 34, "minor": 412, "quarry": 0, "stp": 12, "rawanna": 25301, "transit": 10928, "revenue": 37.99, "dmf": 14.77},
    "Phalodi": {"major": 0, "minor": 414, "quarry": 0, "stp": 64, "rawanna": 33177, "transit": 0, "revenue": 1.34, "dmf": 0.35},
    "Pratapgarh": {"major": 1, "minor": 51, "quarry": 0, "stp": 13, "rawanna": 15993, "transit": 913, "revenue": 2.05, "dmf": 0.35},
    "Rajsamand": {"major": 637, "minor": 2221, "quarry": 60, "stp": 62, "rawanna": 105658, "transit": 25292, "revenue": 41.51, "dmf": 6.84},
    "Salumbar": {"major": 15, "minor": 40, "quarry": 0, "stp": 13, "rawanna": 2697, "transit": 3617, "revenue": 2.45, "dmf": 0.50},
    "Sawai Madhopur": {"major": 0, "minor": 25, "quarry": 0, "stp": 27, "rawanna": 4545, "transit": 3939, "revenue": 1.13, "dmf": 0.05},
    "Sikar": {"major": 4, "minor": 508, "quarry": 0, "stp": 126, "rawanna": 31393, "transit": 30292, "revenue": 12.35, "dmf": 1.76},
    "Sirohi": {"major": 0, "minor": 194, "quarry": 0, "stp": 16, "rawanna": 13352, "transit": 9110, "revenue": 4.54, "dmf": 0.63},
    "Tonk": {"major": 43, "minor": 363, "quarry": 0, "stp": 222, "rawanna": 33502, "transit": 15488, "revenue": 8.01, "dmf": 0.81},
    "Udaipur": {"major": 643, "minor": 196, "quarry": 3, "stp": 75, "rawanna": 15309, "transit": 4697, "revenue": 18.06, "dmf": 3.42}
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
                    if 'Consignee Name' in row: row['Consignee Name'] = mask_consignee_name(str(row['Consignee Name']))
                    if download == "true":
                        pdf_file = generate_pdf(row); return send_file(pdf_file, as_attachment=True)
                    data = row.to_dict()
                else: error_msg = f"Record not found for: {royalty_no}"
            except Exception as e: error_msg = f"Error: {str(e)}"
        else: error_msg = "Database file (data.xlsx) missing."

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
        
        /* Dashboard Styles */
        .slide { background: #008080; color: white; border-radius: 12px; padding: 20px; margin-bottom: 20px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin-top: 15px; }
        .stat-box { background: rgba(255,255,255,0.2); padding: 10px; border-radius: 6px; text-align: center; border: 1px solid rgba(255,255,255,0.3); }
        .stat-box span { font-size: 11px; display: block; text-transform: uppercase; }
        .stat-box b { font-size: 18px; }
        
        /* Verification Styles */
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
    <span>MINES & GEOLOGY DEPARTMENT</span>
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

    // Preserve UI state after post
    window.onload = function() {
        {% if data or error %}
            toggleInterface();
        {% endif %}
        updateDistStats();
    };
</script>
</body>
</html>
'''
    return render_template_string(html_content, data=data, error=error_msg, disclaimer=DISCLAIMER, 
                                 columns=COLUMNS_TO_SHOW, dist_list=sorted(DISTRICT_DATA.keys()), 
                                 json_data=json.dumps(DISTRICT_DATA))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
