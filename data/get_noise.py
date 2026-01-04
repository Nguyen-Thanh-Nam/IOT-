import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- CẤU HÌNH ---
NUM_SAMPLES = 100  # Số lượng dòng muốn tạo
FILENAME = 'dataset_NOISE_POLLUTED.csv'

print(f"Dang tao {NUM_SAMPLES} dong du lieu NOISE POLLUTION...")

# 1. TẠO THỜI GIAN (DateTime) tăng dần theo từng giây
start_time = datetime.now()
time_list = [start_time + timedelta(seconds=i) for i in range(NUM_SAMPLES)]
time_str_list = [t.strftime('%Y-%m-%d %H:%M:%S') for t in time_list]

# 2. TẠO DỮ LIỆU CẢM BIẾN
# -- MQ135 (Không khí): Thấp (Sạch) --
# Trong ảnh của bạn là 0.04, ta random quanh số đó
mq135_data = np.random.uniform(0.02, 0.08, NUM_SAMPLES)
mq135_data = np.round(mq135_data, 2) 

# -- MQ7 (CO): Thấp (Sạch) --
# Trong ảnh của bạn là ~2.46, ta random quanh đó
mq7_data = np.random.uniform(2.0, 3.5, NUM_SAMPLES)
mq7_data = np.round(mq7_data, 2)

# -- PM2.5 (Bụi): Thấp (Sạch) --
# Trong ảnh Air Polluted là 767.0 (Cao).
# Nhưng đây là Noise Pollution nên bụi phải THẤP (ví dụ < 35)
pm25_data = np.random.uniform(5.0, 30.0, NUM_SAMPLES)
pm25_data = np.round(pm25_data, 1)

# -- Sound (Tiếng ồn): CAO (Ồn) --
# Trong ảnh là 38.0 (Yên tĩnh).
# Đây là Noise Pollution nên phải CAO (ví dụ > 75dB)
sound_data = np.random.uniform(75.0, 95.0, NUM_SAMPLES)
sound_data = np.round(sound_data, 1)

# 3. TẠO DATAFRAME
df = pd.DataFrame({
    'MQ135_AirQuality': mq135_data,
    'MQ7_CO_ppm': mq7_data,
    'PM25_ugm3': pm25_data,
    'Sound_dB': sound_data,
    'Scenario': 'NOISE_POLLUTED', # Nhãn kịch bản
    'Alert_Level': 2,             # Mức cảnh báo (2 = Ô nhiễm ồn)
    'DateTime': time_str_list
})

# 4. LƯU RA FILE CSV
df.to_csv(FILENAME, index=False)

print(f"----> Da tao xong file: {FILENAME}")
print("Du lieu mau:")
print(df.head())