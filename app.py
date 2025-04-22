from flask import Flask, request, render_template, jsonify
from forecast_logic import forecast_from_uploaded_file  # assuming this function exists

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

    result = forecast_from_uploaded_file(file)  # your logic function
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
