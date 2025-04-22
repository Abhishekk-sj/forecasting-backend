import pandas as pd
from flask import Flask, request, render_template, jsonify
from forecast_logic import run_forecast

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    try:
        df = pd.read_csv(file)
        columns = df.columns.tolist()
        # Save to global storage for later use (or session)
        df.to_csv('temp_uploaded.csv', index=False)
        return jsonify({'columns': columns})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/forecast', methods=['POST'])
def forecast():
    try:
        data = request.get_json()
        date_col = data['date_column']
        value_col = data['value_column']
        method = data.get('method', 'sma')
        period = int(data.get('period', 3))

        df = pd.read_csv('temp_uploaded.csv')
        df = df[[date_col, value_col]]
        df.columns = ['Date', 'Value']

        result = run_forecast(df, method, period)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
