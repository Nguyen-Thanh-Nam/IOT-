import pandas as pd
import os


folder_path = '' 


files_to_merge = [
    'dataset_AIR_POLLUTED.csv',
    'dataset_BOTH_POLLUTED.csv',
    'dataset_NOISE_POLLUTED.csv',
    'dataset_SAFE.csv',
    'dataset_VERY_CLEAN.csv'
]


output_filename = 'dataset_combined_all.csv'

# ---------------------------
print("="*50)
print("BAT DAU GOP DU LIEU")
print("="*50)

all_dataframes = []

for file_name in files_to_merge:
    full_path = os.path.join(folder_path, file_name)
    
    if os.path.exists(full_path):
        try:
            # Đọc file CSV
            df = pd.read_csv(full_path)
            print(f"OK --> Đã đọc: {file_name} ({len(df)} dòng)")
            all_dataframes.append(df)
        except Exception as e:
            print(f"ERR --> Lỗi khi đọc file {file_name}: {e}")
    else:
        print(f"MISSING --> Không tìm thấy file: {full_path}")


if len(all_dataframes) > 0:

    combined_df = pd.concat(all_dataframes, axis=0, ignore_index=True)
    
    combined_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)

    output_path = os.path.join(folder_path, output_filename)
    combined_df.to_csv(output_path, index=False)
    
    print("\n" + "="*50)
    print("GOP THANH CONG!")
    print(f"Tong so luong mau: {len(combined_df)}")
    print(f"File da luu tai: {output_path}")
    print("="*50)
    

    print("\n5 dong du lieu dau tien (Da duoc tron):")
    print(combined_df.head())

else:
    print("\nKHONG CO DU LIEU NAO DUOC GOP! KIEM TRA LAI THU MUC.")