# Inside app.py

from flask import Flask, request, render_template, jsonify
import pandas as pd
from forecast_logic import run_forecast

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/forecast', methods=['POST'])
def forecast():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty file name'}), 400

    try:
        # Get parameters from the form
        date_col = request.form.get('date_col')
        value_col = request.form.get('value_col')
        frequency = request.form.get('frequency')  # Weekly, Monthly, etc.
        method = request.form.get('method')
        period = int(request.form.get('period'))

        # Read CSV file
        df = pd.read_csv(file)

        # Rename the selected columns
        df = df[[date_col, value_col]]
        df.columns = ['Date', 'Value']

        # Generate the forecast
        result = run_forecast(df, method=method, period=period, frequency=frequency)
        return jsonify({'forecast': result})

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
