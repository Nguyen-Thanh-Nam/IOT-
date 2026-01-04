"""
GENERATE DATASET CHUẨN THEO LOGIC MỚI:
1. AIR_POLLUTED:  (Bụi > 60 OR CO > 10 OR MQ135 > 60) AND (Sound < 65)
2. NOISE_POLLUTED: (Sound > 70) AND (Bụi < 50 AND CO < 8 AND MQ135 < 50)
3. BOTH_POLLUTED: (Sound > 70) AND (Bụi > 60 OR CO > 10 OR MQ135 > 60)
4. SAFE/CLEAN:    Tất cả đều thấp
"""

import pandas as pd
import numpy as np
import random
import os

# Cấu hình số lượng mẫu
SAMPLES_PER_SCENARIO = 5000

# Tạo thư mục datasets
if not os.path.exists('datasets'):
    os.makedirs('datasets')

def generate_random_data():
    all_data = []

    # ==========================================
    # 1. TRƯỜNG HỢP: RẤT SẠCH (VERY_CLEAN)
    # ==========================================
    print("Generating VERY_CLEAN...")
    for _ in range(SAMPLES_PER_SCENARIO):
        all_data.append({
            'MQ135_AirQuality': random.uniform(5, 25),    # Rất thấp
            'MQ7_CO_ppm':       random.uniform(0.1, 3.0), # Rất thấp
            'PM25_ugm3':        random.uniform(0, 20),    # Rất thấp
            'Sound_dB':         random.uniform(30, 45),   # Yên tĩnh
            'Scenario':         'VERY_CLEAN',
            'Alert_Level':      0
        })

    # ==========================================
    # 2. TRƯỜNG HỢP: AN TOÀN (SAFE)
    # ==========================================
    print("Generating SAFE...")
    for _ in range(SAMPLES_PER_SCENARIO):
        all_data.append({
            'MQ135_AirQuality': random.uniform(25, 50),   # Bình thường
            'MQ7_CO_ppm':       random.uniform(3.0, 8.0), # Bình thường
            'PM25_ugm3':        random.uniform(20, 50),   # Bình thường
            'Sound_dB':         random.uniform(45, 60),   # Hơi ồn nhẹ
            'Scenario':         'SAFE',
            'Alert_Level':      0
        })

    print("Generating AIR_POLLUTED...")
    for _ in range(SAMPLES_PER_SCENARIO):
        # Mặc định âm thanh AN TOÀN
        sound = random.uniform(35, 65)
        
        # Random chọn 1 trong 3 loại khí để làm nguyên nhân ô nhiễm
        pollution_type = random.choice(['DUST', 'CO', 'GAS', 'ALL'])
        
        if pollution_type == 'DUST':
            # Chỉ Bụi cao
            pm25 = random.uniform(65, 800) # Cho max lên 800 để AI học số lớn
            co = random.uniform(1, 8)
            gas = random.uniform(10, 50)
        elif pollution_type == 'CO':
            # Chỉ CO cao
            pm25 = random.uniform(10, 50)
            co = random.uniform(12, 50)
            gas = random.uniform(10, 50)
        elif pollution_type == 'GAS':
            # Chỉ MQ135 cao
            pm25 = random.uniform(10, 50)
            co = random.uniform(1, 8)
            gas = random.uniform(65, 500)
        else:
            # Cả 3 cùng cao
            pm25 = random.uniform(65, 800)
            co = random.uniform(12, 50)
            gas = random.uniform(65, 500)

        all_data.append({
            'MQ135_AirQuality': gas,
            'MQ7_CO_ppm':       co,
            'PM25_ugm3':        pm25,
            'Sound_dB':         sound,
            'Scenario':         'AIR_POLLUTED',
            'Alert_Level':      1
        })

    print("Generating NOISE_POLLUTED...")
    for _ in range(SAMPLES_PER_SCENARIO):
        all_data.append({
            'MQ135_AirQuality': random.uniform(10, 50),   
            'MQ7_CO_ppm':       random.uniform(0.5, 8.0), 
            'PM25_ugm3':        random.uniform(5, 50),    
            'Sound_dB':         random.uniform(75, 130),  
            'Scenario':         'NOISE_POLLUTED',
            'Alert_Level':      2
        })

    print("Generating BOTH_POLLUTED...")
    for _ in range(SAMPLES_PER_SCENARIO):
        # Chắc chắn âm thanh phải CAO
        sound = random.uniform(75, 120)

        # Random chọn xem khí nào cao (hoặc tất cả)
        pollution_type = random.choice(['DUST', 'CO', 'GAS', 'ALL'])
        
        if pollution_type == 'DUST':
            pm25 = random.uniform(65, 900)
            co = random.uniform(1, 8)
            gas = random.uniform(10, 50)
        elif pollution_type == 'CO':
            pm25 = random.uniform(10, 50)
            co = random.uniform(12, 100)
            gas = random.uniform(10, 50)
        elif pollution_type == 'GAS':
            pm25 = random.uniform(10, 50)
            co = random.uniform(1, 8)
            gas = random.uniform(65, 800)
        else:
            pm25 = random.uniform(65, 900)
            co = random.uniform(12, 100)
            gas = random.uniform(65, 800)

        all_data.append({
            'MQ135_AirQuality': gas,
            'MQ7_CO_ppm':       co,
            'PM25_ugm3':        pm25,
            'Sound_dB':         sound,
            'Scenario':         'BOTH_POLLUTED',
            'Alert_Level':      3
        })

    df = pd.DataFrame(all_data)
    
    start_date = pd.to_datetime('2024-01-01')
    df['DateTime'] = [start_date + pd.Timedelta(minutes=i*10) for i in range(len(df))]
    
    # Shuffle dữ liệu
    df = df.sample(frac=1).reset_index(drop=True)

    file_path = 'datasets/dataset_combined_all.csv'
    df.to_csv(file_path, index=False)
    print(f"\n[SUCCESS] Đã tạo dataset mới tại: {file_path}")
    print(f"Tổng số mẫu: {len(df)}")
    print("Phân bố dữ liệu:")
    print(df['Scenario'].value_counts())

if __name__ == "__main__":
    generate_random_data()