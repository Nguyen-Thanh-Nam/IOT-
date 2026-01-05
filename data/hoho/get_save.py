import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# --- CẤU HÌNH ---
NUM_SAMPLES = 3000  # Số lượng dòng
FILENAME = '../dataset_SAFE.csv'

print(f"Dang tao {NUM_SAMPLES} dong du lieu SAFE (Binh thuong)...")

# 1. TẠO THỜI GIAN
start_time = datetime.now()
time_list = [start_time + timedelta(seconds=i) for i in range(NUM_SAMPLES)]
time_str_list = [t.strftime('%Y-%m-%d %H:%M:%S') for t in time_list]

# 2. TẠO DỮ LIỆU CẢM BIẾN (Mức trung bình - An toàn)

# -- MQ135: Bình thường --
# Very Clean là ~0.04. Safe cho dao động từ 0.1 đến 0.5
mq135_data = np.random.uniform(0.1, 0.5, NUM_SAMPLES)
mq135_data = np.round(mq135_data, 2)

# -- MQ7 (CO): Bình thường --
# Very Clean là < 4. Safe cho từ 4.0 đến 9.0 (Dưới 10 là an toàn)
mq7_data = np.random.uniform(4.0, 9.0, NUM_SAMPLES)
mq7_data = np.round(mq7_data, 2)

# -- PM2.5: Bụi nhẹ --
# Very Clean ~0. Safe cho từ 10 đến 35 (Mức cho phép của WHO)
pm25_data = np.random.uniform(10.0, 35.0, NUM_SAMPLES)
pm25_data = np.round(pm25_data, 1)

# -- Sound: Tiếng ồn sinh hoạt --
# Safe là từ 45dB (nói chuyện) đến sát 68dB (tiếng xe cộ xa).
# Lưu ý: Phải giữ dưới 70dB để không bị nhầm là ỒN.
sound_data = np.random.uniform(45.0, 68.0, NUM_SAMPLES)
sound_data = np.round(sound_data, 1)

# 3. TẠO DATAFRAME
df = pd.DataFrame({
    'MQ135_AirQuality': mq135_data,
    'MQ7_CO_ppm': mq7_data,
    'PM25_ugm3': pm25_data,
    'Sound_dB': sound_data,
    'Scenario': 'SAFE',       # Nhãn kịch bản
    'Alert_Level': 0,         # Mức 0 (Vẫn an toàn)
    'DateTime': time_str_list
})

# 4. LƯU RA FILE
if not os.path.exists('data'):
    os.makedirs('data')

df.to_csv(FILENAME, index=False)

print(f"----> Da tao xong file: {FILENAME}")
print("5 dong dau tien:")
print(df.head())