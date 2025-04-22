from flask import Flask, request, render_template, jsonify
from forecast_logic import run_forecast
import pandas as pd

app = Flask(__name__)

# Aggregation function for weekly/monthly/quarterly/yearly
def aggregate_data(df, period):
    if period == 'weekly':
        df['Date'] = pd.to_datetime(df['Date']).dt.to_period('W').dt.start_time
    elif period == 'monthly':
        df['Date'] = pd.to_datetime(df['Date']).dt.to_period('M').dt.start_time
    elif period == 'quarterly':
        df['Date'] = pd.to_datetime(df['Date']).dt.to_period('Q').dt.start_time
    elif period == 'yearly':
        df['Date'] = pd.to_datetime(df['Date']).dt.to_period('Y').dt.start_time
    else:
        raise ValueError("Unsupported period")

    # Aggregating data at the selected period level
    df = df.groupby('Date')['Value'].sum().reset_index()
    return df

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
        period = request.form.get('period')  # 'weekly', 'monthly', etc.
        forecast_period = int(request.form.get('forecast_period'))  # Forecast range, e.g., 8 weeks

        # Read CSV file
        df = pd.read_csv(file)

        # Rename the selected columns
        df = df[[date_col, value_col]]
        df.columns = ['Date', 'Value']

        # Aggregate data based on selected period (weekly, monthly, etc.)
        df = aggregate_data(df, period)

        # Run the forecast on the aggregated data
        result = run_forecast(df, method=method, period=forecast_period)

        return jsonify({'forecast': result})

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
