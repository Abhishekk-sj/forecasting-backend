from flask import Flask, request, render_template, jsonify
import pandas as pd
import numpy as np
from datetime import timedelta

app = Flask(__name__)

def run_forecast(df, method, period):
    if df.empty or df.shape[1] < 2:
        raise ValueError("Data must have at least two columns")

    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')

    if method == 'sma':
        df['Forecast'] = df['Value'].rolling(window=period).mean()
    elif method == 'wma':
        weights = range(1, period + 1)
        df['Forecast'] = df['Value'].rolling(window=period).apply(
            lambda x: sum(w * val for w, val in zip(weights, x)) / sum(weights),
            raw=True
        )
    else:
        raise ValueError("Unsupported method")

    df = df.dropna()
    forecast_list = df[['Date', 'Forecast']].tail(10).to_dict(orient='records')
    return forecast_list

def aggregate_data(df, frequency):
    if frequency == 'W':
        df['Date'] = df['Date'].dt.to_period('W').dt.start_time
    elif frequency == 'M':
        df['Date'] = df['Date'].dt.to_period('M').dt.start_time
    elif frequency == 'Q':
        df['Date'] = df['Date'].dt.to_period('Q').dt.start_time
    elif frequency == 'Y':
        df['Date'] = df['Date'].dt.to_period('Y').dt.start_time
    
    aggregated_df = df.groupby('Date').agg({'Value': 'sum'}).reset_index()
    return aggregated_df

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
        method = request.form.get('method')
        period = int(request.form.get('period'))
        frequency = request.form.get('frequency')

        # Read CSV file
        df = pd.read_csv(file)

        # Rename the selected columns
        df = df[[date_col, value_col]]
        df.columns = ['Date', 'Value']

        # Aggregate data by frequency (weekly, monthly, etc.)
        df = aggregate_data(df, frequency)

        # Run forecasting
        forecast_result = run_forecast(df, method=method, period=period)
        return jsonify({'forecast': forecast_result})

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
