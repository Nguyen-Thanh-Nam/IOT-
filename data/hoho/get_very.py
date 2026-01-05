import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- CẤU HÌNH ---
NUM_SAMPLES = 4000  # Số lượng dòng dữ liệu
FILENAME = '../dataset_VERY_CLEAN.csv' # Lưu vào thư mục data

print(f"Dang tao {NUM_SAMPLES} dong du lieu VERY CLEAN...")

# 1. TẠO THỜI GIAN
start_time = datetime.now()
time_list = [start_time + timedelta(seconds=i) for i in range(NUM_SAMPLES)]
time_str_list = [t.strftime('%Y-%m-%d %H:%M:%S') for t in time_list]

# 2. TẠO DỮ LIỆU CẢM BIẾN (Mức cực thấp)

# -- MQ135: Siêu sạch --
# Trong ảnh của bạn là 0.04 cố định. Ở đây mình random nhẹ quanh đó để AI học tốt hơn.
mq135_data = np.random.uniform(0.01, 0.09, NUM_SAMPLES)
mq135_data = np.round(mq135_data, 2)

# -- MQ7 (CO): Thấp --
# Trong ảnh dao động từ 3.3 đến 3.8
mq7_data = np.random.uniform(2.0, 4.0, NUM_SAMPLES)
mq7_data = np.round(mq7_data, 2)

# -- PM2.5: Không có bụi --
# Trong ảnh là 0.0. Mình cho random từ 0 đến 2.0 (vẫn là rất sạch)
pm25_data = np.random.uniform(0.0, 2.0, NUM_SAMPLES)
pm25_data = np.round(pm25_data, 1)

# -- Sound: Yên tĩnh (Thư viện/Phòng ngủ) --
# Trong ảnh là 38.0.
sound_data = np.random.uniform(30.0, 40.0, NUM_SAMPLES)
sound_data = np.round(sound_data, 1)

# 3. TẠO DATAFRAME
df = pd.DataFrame({
    'MQ135_AirQuality': mq135_data,
    'MQ7_CO_ppm': mq7_data,
    'PM25_ugm3': pm25_data,
    'Sound_dB': sound_data,
    'Scenario': 'VERY_CLEAN', # Nhãn kịch bản
    'Alert_Level': 0,         # Mức 0 (An toàn tuyệt đối)
    'DateTime': time_str_list
})

# 4. LƯU RA FILE
# Kiểm tra thư mục data có chưa
import os
if not os.path.exists('data'):
    os.makedirs('data')

df.to_csv(FILENAME, index=False)

print(f"----> Da tao xong file: {FILENAME}")
print("5 dong dau tien:")
print(df.head())