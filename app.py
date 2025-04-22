from flask import Flask, request, render_template, jsonify
import pandas as pd
from forecast_logic import run_forecast  # this matches your function

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/forecast', methods=['POST'])
def forecast():
    if 'file' not in request.files:
        return "No file uploaded", 400
    
    file = request.files['file']
    
    if file.filename == '':
        return "Empty file name", 400

    try:
        df = pd.read_csv(file)

        # You might want to get method and period from form data or set defaults
        method = request.form.get('method', 'sma')  # default to sma
        period = int(request.form.get('period', 3))  # default to 3

        result = run_forecast(df, method, period)
        return jsonify(result)

    except Exception as e:
        return f"An error occurred: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
