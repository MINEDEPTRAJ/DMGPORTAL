import pandas as pd
import json
from flask import Flask, render_template_string, request, os

app = Flask(__name__)

# --- COMPLETE DATA FROM EXCEL ---
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

RAJASTHAN_TOTAL = {"major": 3003, "minor": 13800, "quarry": 12396, "stp": 3515, "rawanna": 1062754, "transit": 508391, "revenue": 673.42, "dmf": 135.31}

@app.route('/')
def index():
    html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DMG Rajasthan - Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f0f4f7; margin: 0; }
        .nav { background: #003366; color: white; padding: 15px; text-align: center; font-weight: bold; }
        .container { max-width: 1200px; margin: 20px auto; padding: 0 20px; }
        
        .slide { background: #008080; color: white; border-radius: 12px; padding: 25px; margin-bottom: 25px; box-shadow: 0 8px 16px rgba(0,0,0,0.1); }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; margin-top: 15px; }
        .stat-card { background: rgba(255,255,255,0.2); padding: 12px; border-radius: 6px; text-align: center; border: 1px solid rgba(255,255,255,0.3); }
        .stat-card span { display: block; font-size: 11px; text-transform: uppercase; }
        .stat-card b { font-size: 20px; }

        .visual-container { display: flex; gap: 20px; margin-bottom: 25px; flex-wrap: wrap; }
        .visual-card { background: white; border-radius: 12px; padding: 15px; flex: 1; min-width: 45%; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
        .visual-card img { width: 100%; border-radius: 5px; max-height: 500px; object-fit: contain; }
        
        .select-dist { background: #004d4d; color: white; padding: 10px; border-radius: 5px; font-size: 16px; margin-bottom: 15px; width: 100%; max-width: 300px; }
    </style>
</head>
<body>

<div class="nav">MINES & GEOLOGY DEPARTMENT - RAJASTHAN</div>

<div class="container">

    <div class="slide">
        <h2 style="margin:0;">RAJASTHAN (TOTAL)</h2>
        <div class="stats-grid">
            <div class="stat-card"><span>Major Leases</span><b>3003</b></div>
            <div class="stat-card"><span>Minor Leases</span><b>13800</b></div>
            <div class="stat-card"><span>Quarry Licence</span><b>12396</b></div>
            <div class="stat-card"><span>STP/Permits</span><b>3515</b></div>
            <div class="stat-card"><span>E-Rawanna</span><b>10,62,754</b></div>
            <div class="stat-card"><span>E-Transit Pass</span><b>5,08,391</b></div>
            <div class="stat-card"><span>Revenue (Cr)</span><b>673.42</b></div>
            <div class="stat-card"><span>DMF (Cr)</span><b>135.31</b></div>
        </div>
    </div>

    <div class="visual-container">
        <div class="visual-card">
            <h3 style="color:#003366;">DISTRIBUTION MAP</h3>
            <img src="/static/rajasthan_map.png" alt="Map">
        </div>
        <div class="visual-card">
            <h3 style="color:#003366;">DMF COLLECTION ANALYSIS</h3>
            <img src="/static/dmf_graph.png" alt="Graph">
        </div>
    </div>

    <div class="slide" style="background:#005a5a;">
        <h2 style="margin:0 0 15px 0;">DISTRICT WISE DASHBOARD</h2>
        <select class="select-dist" id="distSelect" onchange="updateStats()">
            {% for dist in dist_list %}
            <option value="{{ dist }}">{{ dist }}</option>
            {% endfor %}
        </select>
        
        <div class="stats-grid" id="districtStats">
            <div class="stat-card"><span>Major Leases</span><b>643</b></div>
            <div class="stat-card"><span>Minor Leases</span><b>196</b></div>
            <div class="stat-card"><span>Quarry Licence</span><b>3</b></div>
            <div class="stat-card"><span>STP/Permits</span><b>75</b></div>
            <div class="stat-card"><span>E-Rawanna</span><b>15309</b></div>
            <div class="stat-card"><span>E-Transit Pass</span><b>4697</b></div>
            <div class="stat-card"><span>Revenue (Cr)</span><b>18.06</b></div>
            <div class="stat-card"><span>DMF (Cr)</span><b>3.42</b></div>
        </div>
    </div>

</div>

<script>
    const allData = {{ json_data | safe }};
    function updateStats() {
        const d = document.getElementById('distSelect').value;
        const s = allData[d];
        document.getElementById('districtStats').innerHTML = `
            <div class="stat-card"><span>Major Leases</span><b>${s.major}</b></div>
            <div class="stat-card"><span>Minor Leases</span><b>${s.minor}</b></div>
            <div class="stat-card"><span>Quarry Licence</span><b>${s.quarry}</b></div>
            <div class="stat-card"><span>STP/Permits</span><b>${s.stp}</b></div>
            <div class="stat-card"><span>E-Rawanna</span><b>${s.rawanna}</b></div>
            <div class="stat-card"><span>E-Transit Pass</span><b>${s.transit}</b></div>
            <div class="stat-card"><span>Revenue (Cr)</span><b>${s.revenue}</b></div>
            <div class="stat-card"><span>DMF (Cr)</span><b>${s.dmf}</b></div>
        `;
    }
</script>

</body>
</html>
'''
    return render_template_string(html_content, 
                                 dist_list=sorted(DISTRICT_DATA.keys()), 
                                 json_data=json.dumps(DISTRICT_DATA))

if __name__ == '__main__':
    app.run(debug=True)
