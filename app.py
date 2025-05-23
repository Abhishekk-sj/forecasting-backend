from flask import Flask, request, render_template, jsonify
from forecast_logic import run_forecast
import pandas as pd

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
        # Get parameters from the frontend
        date_col = request.form.get('date_col')
        value_col = request.form.get('value_col')
        method = request.form.get('method')
        period = int(request.form.get('period'))

        # Load and prepare the dataframe
        df = pd.read_csv(file)

        if date_col not in df.columns or value_col not in df.columns:
            return jsonify({'error': 'Selected columns not found in the uploaded file'}), 400

        df = df[[date_col, value_col]]
        df.columns = ['Date', 'Value']

        # Run forecasting logic
        result = run_forecast(df, method=method, period=period)
        return jsonify({'forecast': result})

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
