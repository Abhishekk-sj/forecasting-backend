from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
from forecast_logic import run_forecast  # Your custom forecasting logic

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return 'Flask Forecasting API is running!'

@app.route('/forecast', methods=['POST'])
def forecast():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    method = request.form.get('method', 'sma')
    period = int(request.form.get('period', 3))

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        df = pd.read_excel(file_path)
        result = run_forecast(df, method, period)

        os.remove(file_path)

        return jsonify({'forecast': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)