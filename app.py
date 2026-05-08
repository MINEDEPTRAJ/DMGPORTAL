import pandas as pd
import qrcode
from fpdf import FPDF
from flask import Flask, render_template_string, request, send_file
import os

app = Flask(__name__)

DISCLAIMER = "Note: This is a private verification portal. Not an official Government website."

# Columns mapping as per portal style
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
    if not isinstance(name, str) or not name.strip(): return name
    name = name.strip()
    if len(name) <= 1: return name
    middle = "".join([" " if c == " " else "X" for c in name[1:-1]])
    return name[0] + middle + name[-1]

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
                    row['Consignee Name'] = mask_consignee_name(str(row['Consignee Name']))
                    data = row.to_dict()
                else:
                    error_msg = f"Record not found for: {royalty_no}"
            except Exception as e:
                error_msg = f"Error: {str(e)}"

    # Dashboard-style HTML
    html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GMDRAJASTHAN</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f0f4f7; margin: 0; padding: 0; }
        .top-nav { background: #003366; color: white; padding: 10px 20px; text-align: center; font-weight: bold; }
        .dashboard-header { background: #008080; color: white; padding: 20px; text-align: center; }
        .stats-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; padding: 20px; max-width: 1000px; margin: auto; }
        .stat-box { background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.3); padding: 15px; border-radius: 4px; text-align: center; color: white; }
        .stat-box span { display: block; font-size: 20px; font-weight: bold; }
        
        .main-card { background: white; max-width: 600px; margin: 20px auto; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .search-title { border-bottom: 2px solid #008080; padding-bottom: 10px; margin-bottom: 20px; color: #003366; }
        
        input[type="text"] { width: 100%; padding: 12px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; font-size: 16px; }
        .btn-check { background: #003366; color: white; border: none; padding: 12px 20px; width: 100%; border-radius: 4px; margin-top: 10px; cursor: pointer; font-weight: bold; }
        
        .data-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        .data-table td { border: 1px solid #ddd; padding: 10px; font-size: 14px; }
        .label { background: #f9f9f9; font-weight: bold; width: 40%; color: #333; }
        .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="top-nav">GEOMINEDEP</div>
    
    <div class="dashboard-header">
        <div class="stats-container">
            <div class="stat-box">Major Leases <span>3003</span></div>
            <div class="stat-box">Minor Leases <span>13800</span></div>
            <div class="stat-box">E-Rawanna <span>1137480</span></div>
            <div class="stat-box">E-Transit Pass <span>450577</span></div>
        </div>
    </div>

    <div class="main-card">
        <h2 class="search-title">Verify Transit Pass Status</h2>
        <form method="post">
            <input type="text" name="royalty_no" placeholder="Enter eRawanna / Transit Pass No..." required>
            <button type="submit" class="btn-check">VERIFY NOW</button>
        </form>

        {% if error %} <p style="color:red; text-align:center;">{{ error }}</p> {% endif %}

        {% if data %}
        <table class="data-table">
            {% for label, key in columns %}
            <tr>
                <td class="label">{{ label }}</td>
                <td>{{ data[key] }}</td>
            </tr>
            {% endfor %}
        </table>
        <button class="btn-check" style="background:#27ae60;">DOWNLOAD RECEIPT</button>
        {% endif %}
    </div>

    <div class="footer">{{ disclaimer }}</div>
</body>
</html>
'''
    return render_template_string(html_content, data=data, error=error_msg, disclaimer=DISCLAIMER, columns=COLUMNS_TO_SHOW)

if __name__ == '__main__':
    app.run(debug=True)