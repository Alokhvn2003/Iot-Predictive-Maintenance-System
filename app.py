from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd

app = Flask(__name__)

# Load the pre-trained Isolation Forest Model
model = joblib.load("isolation_forest_model.pkl")

# Global variable to store latest reading for dashboard
latest_data = {"vibration": 0, "frequency": 0, "temperature": 0, "ai": "Waiting"}

@app.route('/')
def dashboard():
    return render_template('index.html', data=latest_data)

@app.route('/data', methods=['POST'])
def receive_data():
    global latest_data
    content = request.json
    
    # Prepare features for Isolation Forest
    features = pd.DataFrame([[content['vibration'], content['frequency'], content['temperature']]], 
                            columns=['vibration', 'frequency', 'temperature'])
    
    # Predict: 1 = Normal, -1 = Anomaly
    prediction = model.predict(features)
    status = "ANOMALY" if prediction[0] == -1 else "NORMAL"
    
    latest_data = content
    latest_data['ai'] = status
    
    return jsonify({"ai": status})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
