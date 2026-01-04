import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from catboost import CatBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import joblib
import os

# giao dien bieu do
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Tao thu muc
charts_dir = 'charts_scenario'
if not os.path.exists(charts_dir):
    os.makedirs(charts_dir)
    print(f"Tao thu muc: {charts_dir}")

print("=" * 70)
print("TRAINING AI")
print("=" * 70)

# load dataset 
print("\nload data")
data_path = 'datasets/dataset_combined_all.csv'

if os.path.exists(data_path):
    df = pd.read_csv(data_path)
    print(f"Loaded dataset: {len(df)} samples")
else:
    print(f"fail load dataset")
    exit()

# check Scenario 
if 'Scenario' not in df.columns:
    print("Dataset missing 'Scenario' column!")
    exit()

print(f"Scenarios found: {df['Scenario'].unique()}")

# 3. FEATURE ENGINEERING (Xử lý dữ liệu)
print("\n[2] Creating Features...")

# chuyen doi thoi gian
df['DateTime'] = pd.to_datetime(df['DateTime'])
df['Hour'] = df['DateTime'].dt.hour
df['DayOfWeek'] = df['DateTime'].dt.dayofweek

# Cyclical encoding (Biến đổi giờ giấc thành vòng tròn để AI hiểu 23h gần 0h)
df['hour_sin'] = np.sin(2 * np.pi * df['Hour'] / 24)
df['hour_cos'] = np.cos(2 * np.pi * df['Hour'] / 24)
df['day_sin'] = np.sin(2 * np.pi * df['DayOfWeek'] / 7)
df['day_cos'] = np.cos(2 * np.pi * df['DayOfWeek'] / 7)

# bo cac dong loi
df = df.dropna().reset_index(drop=True)

TARGET = 'Scenario' 

FEATURES = [
    'MQ135_AirQuality', 'MQ7_CO_ppm', 'PM25_ugm3', 'Sound_dB', 
    'hour_sin', 'hour_cos', 'day_sin', 'day_cos'               
]

X = df[FEATURES]
y_text = df[TARGET] # Dữ liệu nhãn đang là dạng chữ (SAFE, AIR_POLLUTED...)

# Mã hóa nhãn (Chuyển chữ thành số để AI học)
le = LabelEncoder()
y = le.fit_transform(y_text)
class_names = list(le.classes_) # Lưu lại danh sách tên thật để dùng sau này

print(f"\nSetup Training:")
print(f"Target: {TARGET}")
print(f"Input Features ({len(FEATURES)}): {FEATURES}")
print(f"Classes mapping: {dict(enumerate(class_names))}")

# 5. CHIA DỮ LIỆU (Train/Test)
print("\n[4] Splitting Data...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"Training Set: {len(X_train)} samples")
print(f"Test Set:     {len(X_test)} samples")

# 6. TRAIN MODEL (Dùng CatBoost)
print("\n[5] Training Model (CatBoost)...")
model = CatBoostClassifier(
    iterations=500,         # so luong cay quyet dinh
    learning_rate=0.05,     # toc do hoc
    depth=6,                # do sau cay quyet dinh
    random_seed=42,
    verbose=100,            # in thong tin sau moi 100 vong
    loss_function='MultiClass',
    allow_writing_files=False
)

model.fit(
    X_train, y_train,
    eval_set=(X_test, y_test),
    early_stopping_rounds=50 # dung dung som neu khong cai thien
)

# 7. ĐÁNH GIÁ MODEL
print("\n[6] Evaluating Model...")
y_pred = model.predict(X_test)
if y_pred.ndim > 1: y_pred = y_pred.flatten()

# Tính độ chính xác
accuracy = accuracy_score(y_test, y_pred)
print(f"\n    >>> ACCURACY: {accuracy*100:.2f}% <<<")

print("\n    Detailed Report:")
print(classification_report(y_test, y_pred, target_names=class_names))

# 8. VẼ BIỂU ĐỒ (VISUALIZATION)
print(f"\n[7] Generating Charts into '{charts_dir}'...")

# Chart 1: Confusion Matrix (Ma trận nhầm lẫn)
plt.figure(figsize=(10, 8))
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=class_names, yticklabels=class_names)
plt.title('Confusion Matrix (Scenario Prediction)', fontsize=14, fontweight='bold')
plt.ylabel('Thực tế (True)', fontsize=12)
plt.xlabel('Dự đoán (Predicted)', fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f'{charts_dir}/1_confusion_matrix.png', dpi=300)
plt.close()

# Chart 2: Feature Importance (Cái gì quan trọng nhất?)
plt.figure(figsize=(10, 6))
importance = model.get_feature_importance()
indices = np.argsort(importance)[::-1] # Sắp xếp giảm dần
plt.barh(range(len(indices)), importance[indices], color='steelblue')
plt.yticks(range(len(indices)), [FEATURES[i] for i in indices])
plt.gca().invert_yaxis() # Đảo ngược trục Y để cái quan trọng nhất lên đầu
plt.title('Yếu tố ảnh hưởng đến kết quả dự đoán', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{charts_dir}/2_feature_importance.png', dpi=300)
plt.close()

# Chart 3: Dự đoán đúng sai theo từng lớp
plt.figure(figsize=(12, 6))
# Tính tỷ lệ đúng cho từng class
accuracies = cm.diagonal() / cm.sum(axis=1)
colors = ['green' if x > 0.9 else 'orange' if x > 0.7 else 'red' for x in accuracies]
bars = plt.bar(class_names, accuracies, color=colors)
plt.title('Độ chính xác theo từng loại ô nhiễm', fontsize=14, fontweight='bold')
plt.ylabel('Tỷ lệ chính xác (0-1)')
plt.ylim(0, 1.1)
for bar, acc in zip(bars, accuracies):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, 
             f'{acc*100:.1f}%', ha='center', va='bottom', fontweight='bold')
plt.tight_layout()
plt.savefig(f'{charts_dir}/3_accuracy_per_class.png', dpi=300)
plt.close()

# 9. LƯU MODEL
print("\n[8] Saving System Files...")

# Lưu bộ não AI
joblib.dump(model, 'scenario_model.pkl')
print("    [SAVED] scenario_model.pkl")

# Lưu từ điển dịch mã (CỰC KỲ QUAN TRỌNG)
joblib.dump(le, 'label_encoder.pkl')
print("    [SAVED] label_encoder.pkl")

# Lưu danh sách features
joblib.dump(FEATURES, 'model_features.pkl')
print("    [SAVED] model_features.pkl")

print("\n" + "="*70)
print("TRAINING COMPLETE! READY FOR DEPLOYMENT.")
print("="*70)