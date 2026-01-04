import requests
import time
import csv
import os
from datetime import datetime

BLYNK_TOKEN = "-JtyN9CYCudclKkkfClXNl-i3hQNEGpA"
BLYNK_URL = f"https://blynk.cloud/external/api/getAll?token={BLYNK_TOKEN}"

FILE_NAME = "dataset_AIR_POLLUTED.csv" 

TARGET_LABEL = "AIR_POLLUTED"    
LEVEL = 0       


INTERVAL = 0.5

def fetch_and_save():

    file_exists = os.path.isfile(FILE_NAME)
    
    with open(FILE_NAME, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        if not file_exists:
            writer.writerow(['MQ135_AirQuality', 'MQ7_CO_ppm', 'PM25_ugm3', 'Sound_dB', 'Scenario', 'Alert_Level', 'DateTime'])
            print(f"--- Đã tạo file mới: {FILE_NAME} ---")
            print(f"--- Đang thu thập dữ liệu nhãn '{TARGET_LABEL}' ---")

        while True:
            try:
                response = requests.get(BLYNK_URL, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    mq135 = float(data.get('v0', 0))
                    mq7 = float(data.get('v1', 0))
                    pm25 = float(data.get('v2', 0))
                    sound = float(data.get('v3', 0))
                    
 
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    

                    writer.writerow([mq135, mq7, pm25, sound, TARGET_LABEL, LEVEL, now_str])
                    
                    print(f"[{now_str}] Đã lưu: Bụi={pm25} | Ồn={sound} -> Nhãn: {TARGET_LABEL}")
                    
                    f.flush() 
                else:
                    print(f"[LỖI SERVER] Code: {response.status_code}")

            except Exception as e:
                print(f"[LỖI KẾT NỐI] {e}")
            
            time.sleep(INTERVAL)

if __name__ == "__main__":
    fetch_and_save()