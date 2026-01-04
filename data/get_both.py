import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- CẤU HÌNH ---
NUM_SAMPLES = 3000  # Tạo nhiều hơn chút để đủ các trường hợp
FILENAME = 'dataset_BOTH_POLLUTED_mixed.csv'

print(f"Dang tao {NUM_SAMPLES} dong du lieu BOTH POLLUTED (Mix 1 trong 3)...")

# 1. TẠO THỜI GIAN
start_time = datetime.now()
time_list = [start_time + timedelta(seconds=i) for i in range(NUM_SAMPLES)]
time_str_list = [t.strftime('%Y-%m-%d %H:%M:%S') for t in time_list]

# 2. KHỞI TẠO NỀN TẢNG (Mặc định là SẠCH trước)
# MQ135 Sạch (0.01 - 0.5)
mq135_data = np.random.uniform(0.01, 0.5, NUM_SAMPLES)
# MQ7 Sạch (0.5 - 5.0)
mq7_data = np.random.uniform(0.5, 5.0, NUM_SAMPLES)
# PM2.5 Sạch (0 - 30)
pm25_data = np.random.uniform(0.0, 30.0, NUM_SAMPLES)

# 3. TẠO DỮ LIỆU TIẾNG ỒN (LUÔN LUÔN CAO)
# Vì đây là BOTH_POLLUTED nên bắt buộc phải Ồn (> 75dB)
sound_data = np.random.uniform(75.0, 95.0, NUM_SAMPLES)

# 4. XỬ LÝ LOGIC "1 TRONG 3 KHÍ CAO"
# Tạo một mảng ngẫu nhiên từ 0 đến 2 để quyết định chỉ số nào sẽ bị "Spike" (tăng vọt)
# 0: MQ135 cao
# 1: MQ7 cao
# 2: PM2.5 cao
spike_choice = np.random.randint(0, 3, NUM_SAMPLES)

# -- TRƯỜNG HỢP 0: MQ135 CAO (Khói/Gas) --
# Gán lại giá trị cao cho những dòng có spike_choice = 0
mq135_data[spike_choice == 0] = np.random.uniform(2.0, 5.0, np.sum(spike_choice == 0))

# -- TRƯỜNG HỢP 1: MQ7 CAO (CO) --
# Gán lại giá trị cao cho những dòng có spike_choice = 1
mq7_data[spike_choice == 1] = np.random.uniform(15.0, 60.0, np.sum(spike_choice == 1))

# -- TRƯỜNG HỢP 2: PM2.5 CAO (Bụi mịn) --
# Gán lại giá trị cao cho những dòng có spike_choice = 2
pm25_data[spike_choice == 2] = np.random.uniform(150.0, 900.0, np.sum(spike_choice == 2))

# Làm tròn số liệu cho đẹp
mq135_data = np.round(mq135_data, 2)
mq7_data = np.round(mq7_data, 2)
pm25_data = np.round(pm25_data, 1)
sound_data = np.round(sound_data, 1)

# 5. TẠO DATAFRAME
df = pd.DataFrame({
    'MQ135_AirQuality': mq135_data,
    'MQ7_CO_ppm': mq7_data,
    'PM25_ugm3': pm25_data,
    'Sound_dB': sound_data,
    'Scenario': 'BOTH_POLLUTED',
    'Alert_Level': 3,  # Mức 3: Nguy hiểm
    'DateTime': time_str_list
})

# 6. LƯU RA FILE
df.to_csv(FILENAME, index=False)

print(f"----> Da tao xong file: {FILENAME}")
print("Du lieu mau (Random 10 dong):")
print(df.sample(10)) # In ngẫu nhiên 10 dòng để bạn kiểm tra