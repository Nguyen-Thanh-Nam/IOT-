from flask import Flask, render_template, jsonify, request
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
import os
import threading
import time
import requests

app = Flask(__name__)

MODEL_DIR = os.path.join(os.path.dirname(__file__), '../ai_model')


BLYNK_TOKEN = "-JtyN9CYCudclKkkfClXNl-i3hQNEGpA"
BLYNK_URL = f"https://blynk.cloud/external/api/getAll?token={BLYNK_TOKEN}"
FETCH_INTERVAL = 1


latest_data_store = {
    'display_text': 'Đang chờ dữ liệu...',
    'color': '#95a5a6',
    'icon': 'spinner',
    'confidence': 0,
    'raw_sensors': {'mq135': 0, 'mq7': 0, 'pm25': 0, 'sound': 0},
    'alert_level': 0
}

model = None
le = None
features_list = None

try:
    print(f"Loading AI from: {MODEL_DIR}...")
    model = joblib.load(os.path.join(MODEL_DIR, 'scenario_model.pkl'))
    le = joblib.load(os.path.join(MODEL_DIR, 'label_encoder.pkl'))
    features_list = joblib.load(os.path.join(MODEL_DIR, 'model_features.pkl'))
    print("AI Model loaded successfully!")
except Exception as e:
    print(f"Load model failed: {e}")

# ==================== HÀM XỬ LÝ AI (Dùng chung) ====================
def process_ai_prediction(mq135, mq7, pm25, sound):
    global latest_data_store
    
    if model is None: return None

    try:
        # 1. Feature Engineering (Xử lý thời gian)
        now = datetime.now()
        input_data = {
            'MQ135_AirQuality': mq135,
            'MQ7_CO_ppm': mq7,
            'PM25_ugm3': pm25,
            'Sound_dB': sound,
            'hour_sin': np.sin(2 * np.pi * now.hour / 24),
            'hour_cos': np.cos(2 * np.pi * now.hour / 24),
            'day_sin': np.sin(2 * np.pi * now.weekday() / 7),
            'day_cos': np.cos(2 * np.pi * now.weekday() / 7)
        }
        
        X_new = pd.DataFrame([input_data])[features_list]
        pred_index = model.predict(X_new)[0]
        if isinstance(pred_index, (list, np.ndarray)):
            pred_index = pred_index.flatten()[0]
        
        scenario_name = le.inverse_transform([int(pred_index)])[0]
        probs = model.predict_proba(X_new)[0]
        confidence = round(max(probs) * 100, 1)

        alert_level = 0
        
        if scenario_name == 'BOTH_POLLUTED': 
            alert_level = 3
            
        elif scenario_name == 'NOISE_POLLUTED': 
            alert_level = 2
            
        elif scenario_name == 'AIR_POLLUTED': 
            alert_level = 1 
        else: 
            alert_level = 0  

        scenario_info = {
            'VERY_CLEAN':     {'text': 'RẤT TRONG LÀNH', 'color': '#2ecc71', 'icon': 'leaf'},
            'SAFE':           {'text': 'AN TOÀN',        'color': '#27ae60', 'icon': 'check-circle'},
            'AIR_POLLUTED':   {'text': 'Ô NHIỄM KHÍ',    'color': '#e67e22', 'icon': 'smog'},
            'NOISE_POLLUTED': {'text': 'Ô NHIỄM ỒN',     'color': '#d35400', 'icon': 'volume-up'},
            'BOTH_POLLUTED':  {'text': 'Ô NHIỄM NẶNG',  'color': '#c0392b', 'icon': 'exclamation-triangle'}
        }
        display = scenario_info.get(scenario_name, {'text': scenario_name, 'color': '#95a5a6', 'icon': 'info'})


        result = {
            'alert_level': alert_level,
            'scenario_code': scenario_name,
            'display_text': display['text'],
            'color': display['color'],
            'icon': display['icon'],
            'confidence': confidence,
            'raw_sensors': {'mq135': mq135, 'mq7': mq7, 'pm25': pm25, 'sound': sound}
        }
        latest_data_store = result
        return result

    except Exception as e:
        print(f"[AI ERROR] {e}")
        return None

def run_blynk_pipeline():
    """Luồng này chạy song song để hút dữ liệu từ Blynk"""
    print("[PIPELINE] Started background thread for Blynk...")
    while True:
        try:
            response = requests.get(BLYNK_URL, timeout=2)
            if response.status_code == 200:
                data = response.json()
                print(f"data:{data}")
                mq135 = float(data.get('v0', 0))
                mq7 = float(data.get('v1', 0))
                pm25 = float(data.get('v2', 0))
                sound = float(data.get('v3', 0))
                
                result = process_ai_prediction(mq135, mq7, pm25, sound)
                
                if result:
                    pass
            
        except Exception as e:
            print(f"[PIPELINE ERROR] {e}")
        
        time.sleep(FETCH_INTERVAL)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/latest', methods=['GET'])
def get_latest():
    return jsonify(latest_data_store)

@app.route('/api/predict', methods=['POST'])
def predict_endpoint():
    try:
        data = request.json
        mq135 = float(data.get('mq135', 0))
        mq7 = float(data.get('mq7', 0))
        pm25 = float(data.get('pm25', 0))
        sound = float(data.get('sound', 0))

        result = process_ai_prediction(mq135, mq7, pm25, sound)
        if result:
            return jsonify(result)
        else:
            return jsonify({'error': 'AI Error'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    pipeline_thread = threading.Thread(target=run_blynk_pipeline)
    pipeline_thread.daemon = True # Tự tắt khi chương trình chính tắt
    pipeline_thread.start()

    print(">>> Access Dashboard at: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False) 