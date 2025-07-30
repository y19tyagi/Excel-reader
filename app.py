from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

EXCEL_FILES = [
    "b7ee_Prijslijst delta light.xlsx",
    "CLEANED Flos Outdoor Pricelist Netherland 2025.xlsx",
    "CLEANED iGUZZINI _2025.xlsb"
]

# Load all Excel files, normalize SKU column for searching
excel_data = []
for filename in EXCEL_FILES:
    df = pd.read_excel(filename)
    df['SKU_NORM'] = df['SKU'].astype(str).str.replace(r'\s+', '', regex=True).str.upper()
    excel_data.append({"filename": filename, "df": df})

@app.route('/lookup', methods=['POST'])
def lookup():
    items = request.json.get('items', [])
    results = []
    for item in items:
        input_sku = str(item.get('SKU', '')).replace(' ', '').upper()
        found = False
        for excel in excel_data:
            match = excel["df"][excel["df"]['SKU_NORM'] == input_sku]
            if not match.empty:
                excel_row = match.iloc[0].to_dict()
                excel_row.pop('SKU_NORM', None)
                merged = {**item, **excel_row}
                merged["source_file"] = excel["filename"]
                results.append(merged)
                found = True
                break
        if not found:
            not_found_info = item.copy()
            not_found_info['not_found'] = True
            results.append(not_found_info)
    return jsonify({'results': results})

@app.route('/', methods=['GET'])
def home():
    return 'Excel Multi-File Reader API is up!'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
