from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Use your actual Excel file name here (or set EXCEL_FILE env var)
EXCEL_FILE = os.environ.get("EXCEL_FILE", "b7ee_Prijslijst delta light.xlsx")

# Load Excel and add a normalized SKU column (on startup)
df = pd.read_excel(EXCEL_FILE)
df['SKU_NORM'] = df['REFERENTIE'].astype(str).str.replace(r'\s+', '', regex=True).str.upper()

@app.route('/lookup', methods=['POST'])
def lookup():
    items = request.json.get('items', [])
    results = []
    for item in items:
        # Normalize the input SKU for matching
        input_sku = str(item.get('SKU', '')).replace(' ', '').upper()
        match = df[df['SKU_NORM'] == input_sku]
        if not match.empty:
            # Merge all Excel columns + original input
            excel_row = match.iloc[0].to_dict()
            # Remove the SKU_NORM helper from output
            excel_row.pop('SKU_NORM', None)
            merged = {**item, **excel_row}
            results.append(merged)
        else:
            # Not found: return original input, flag as not found
            not_found_info = item.copy()
            not_found_info['not_found'] = True
            results.append(not_found_info)
    return jsonify({'results': results})

@app.route('/', methods=['GET'])
def home():
    return 'Excel File Reader API is up!'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
