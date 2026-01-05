import pandas as pd
import numpy as np
from datetime import datetime, timedelta

NUM_SAMPLES = 2000  # Tạo nhiều hơn chút để đủ các trường hợp
FILENAME = '../dataset_BOTH_POLLUTED.csv'

print(f"Dang tao {NUM_SAMPLES} dong du lieu BOTH POLLUTED (Mix 1 trong 3)...")


start_time = datetime.now()
time_list = [start_time + timedelta(seconds=i) for i in range(NUM_SAMPLES)]
time_str_list = [t.strftime('%Y-%m-%d %H:%M:%S') for t in time_list]

mq135_data = np.random.uniform(0.01, 0.5, NUM_SAMPLES)

mq7_data = np.random.uniform(0.5, 5.0, NUM_SAMPLES)

pm25_data = np.random.uniform(0.0, 30.0, NUM_SAMPLES)

sound_data = np.random.uniform(75.0, 95.0, NUM_SAMPLES)

spike_choice = np.random.randint(0, 3, NUM_SAMPLES)


mq135_data[spike_choice == 0] = np.random.uniform(2.0, 5.0, np.sum(spike_choice == 0))

mq7_data[spike_choice == 1] = np.random.uniform(15.0, 60.0, np.sum(spike_choice == 1))

pm25_data[spike_choice == 2] = np.random.uniform(150.0, 900.0, np.sum(spike_choice == 2))

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
print(df.sample(10)) 