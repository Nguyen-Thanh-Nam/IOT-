import pandas as pd
import numpy as np
import random
import os

# --- CẤU HÌNH ---
SAMPLES_PER_SCENARIO = 5000
NOISE_LEVEL = 0.1  # 10% dữ liệu sẽ bị làm nhiễu/sai lệch

if not os.path.exists('datasets'):
    os.makedirs('datasets')

def generate_random_data():
    all_data = []
    
    # Hàm tạo nhiễu nhẹ cho cảm biến (mô phỏng sai số thiết bị)
    def jitter(val, strength=2.0):
        return max(0, val + random.gauss(0, strength))

    print("Generating Dataset with NOISE/OVERLAP...")

    # ==========================================
    # 1. TRƯỜNG HỢP: RẤT SẠCH (VERY_CLEAN)
    # ==========================================
    for _ in range(SAMPLES_PER_SCENARIO):
        # Đôi khi sạch nhưng cảm biến bụi lại nhảy lung tung một chút
        all_data.append({
            'MQ135_AirQuality': jitter(random.uniform(5, 30)),   # Cho phépm chớm lên 30
            'MQ7_CO_ppm':       jitter(random.uniform(0.1, 4.0)), 
            'PM25_ugm3':        jitter(random.uniform(0, 25)),    
            'Sound_dB':         jitter(random.uniform(30, 50)),   # Đôi khi ồn nhẹ
            'Scenario':         'VERY_CLEAN',
            'Alert_Level':      0
        })

    # ==========================================
    # 2. TRƯỜNG HỢP: AN TOÀN (SAFE)
    # ==========================================
    # Logic cũ: Bụi < 50, Ồn < 60
    # Logic mới: Cho phép Bụi lên tới 55-58 (Sát ngưỡng 60), Ồn lên tới 68 (Sát ngưỡng 70)
    for _ in range(SAMPLES_PER_SCENARIO):
        is_anomaly = random.random() < NOISE_LEVEL # 10% là dữ liệu nhiễu
        
        if is_anomaly:
            # Dữ liệu "lừa": Ồn vọt lên 75 nhưng vẫn coi là SAFE (ví dụ tiếng còi xe thoáng qua)
            sound = random.uniform(65, 78) 
            pm25 = random.uniform(40, 65) # Bụi mấp mé ngưỡng ô nhiễm
        else:
            sound = random.uniform(45, 68) # Sát nút ngưỡng NOISE (70)
            pm25 = random.uniform(20, 55)  # Sát nút ngưỡng DUST (60)

        all_data.append({
            'MQ135_AirQuality': jitter(random.uniform(25, 55)), 
            'MQ7_CO_ppm':       jitter(random.uniform(3.0, 9.0)), # Sát ngưỡng 10
            'PM25_ugm3':        jitter(pm25),
            'Sound_dB':         jitter(sound),
            'Scenario':         'SAFE',
            'Alert_Level':      0
        })


    for _ in range(SAMPLES_PER_SCENARIO):
        # Tạo vùng giao thoa: Âm thanh có thể lên tới 72 (lấn sang vùng Noise Pollution)
        sound = random.uniform(40, 72) 
        
        pollution_type = random.choice(['DUST', 'CO', 'GAS', 'ALL'])
        
        # Mặc định giá trị thấp (nhưng cho phép mấp mé ngưỡng cao)
        pm25 = random.uniform(20, 55)
        co = random.uniform(2, 9)
        gas = random.uniform(20, 55)

        if pollution_type == 'DUST':
            pm25 = random.uniform(55, 300) # 55 là chưa tới 60, nhưng vẫn gán nhãn ô nhiễm (AI phải học khó hơn)
        elif pollution_type == 'CO':
            co = random.uniform(9.0, 30)   # 9.0 chưa tới 10
        elif pollution_type == 'GAS':
            gas = random.uniform(55, 200)  # 55 chưa tới 60
        else:
            pm25 = random.uniform(60, 300)
            co = random.uniform(10, 30)
            gas = random.uniform(60, 200)

        all_data.append({
            'MQ135_AirQuality': jitter(gas),
            'MQ7_CO_ppm':       jitter(co),
            'PM25_ugm3':        jitter(pm25),
            'Sound_dB':         jitter(sound),
            'Scenario':         'AIR_POLLUTED',
            'Alert_Level':      1
        })


    for _ in range(SAMPLES_PER_SCENARIO):
        sound = random.uniform(68, 110)
        

        all_data.append({
            'MQ135_AirQuality': jitter(random.uniform(20, 58)), # Gần 60
            'MQ7_CO_ppm':       jitter(random.uniform(2.0, 9.5)), # Gần 10
            'PM25_ugm3':        jitter(random.uniform(10, 58)),   # Gần 60
            'Sound_dB':         jitter(sound),
            'Scenario':         'NOISE_POLLUTED',
            'Alert_Level':      2
        })

    # ==========================================
    # 5. TRƯỜNG HỢP: Ô NHIỄM KÉP (BOTH_POLLUTED)
    # ==========================================
    for _ in range(SAMPLES_PER_SCENARIO):
        sound = random.uniform(70, 120) # Rõ ràng là ồn

        # Random chọn xem khí nào cao
        pollution_type = random.choice(['DUST', 'CO', 'GAS', 'ALL'])
        
        pm25 = random.uniform(30, 55)
        co = random.uniform(3, 9)
        gas = random.uniform(30, 55)

        if pollution_type == 'DUST':
            pm25 = random.uniform(60, 500)
        elif pollution_type == 'CO':
            co = random.uniform(10, 50)
        elif pollution_type == 'GAS':
            gas = random.uniform(60, 400)
        else: # ALL
            pm25 = random.uniform(60, 500)
            co = random.uniform(10, 50)
            gas = random.uniform(60, 400)

        # Thỉnh thoảng tạo dữ liệu khó hiểu: Vừa ồn, vừa bụi, nhưng CO lại cực thấp
        if random.random() < 0.1:
            co = 0.1 

        all_data.append({
            'MQ135_AirQuality': jitter(gas),
            'MQ7_CO_ppm':       jitter(co),
            'PM25_ugm3':        jitter(pm25),
            'Sound_dB':         jitter(sound),
            'Scenario':         'BOTH_POLLUTED',
            'Alert_Level':      3
        })

    # Tạo DataFrame
    df = pd.DataFrame(all_data)
    
    # Tạo thời gian giả lập
    start_date = pd.to_datetime('2025-11-01')
    df['DateTime'] = [start_date + pd.Timedelta(minutes=i*5) for i in range(len(df))]
    
    # Trộn ngẫu nhiên
    df = df.sample(frac=1).reset_index(drop=True)

    # Lưu file
    file_path = 'datasets/dataset_combined_all.csv'
    df.to_csv(file_path, index=False)
    print(f"\n[SUCCESS] Đã tạo dataset 'KHÓ' tại: {file_path}")
    print(f"Tổng số mẫu: {len(df)}")

if __name__ == "__main__":
    generate_random_data()