import pandas as pd

print("🚀 Starting preprocessing...")

# ==============================
# 1. LOAD DATA
# ==============================
data = pd.read_csv("data/household_power_consumption.txt", sep=';')

print("✅ Data loaded")

# ==============================
# 2. CLEAN DATA
# ==============================
# Replace missing values
data = data.replace('?', None)

# Drop missing rows
data = data.dropna()

print("✅ Missing values removed")

# Convert to numeric
data['Global_active_power'] = data['Global_active_power'].astype(float)

# ==============================
# 3. CREATE DATETIME
# ==============================
data['datetime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'])

# Extract features
data['hour'] = data['datetime'].dt.hour
data['day'] = data['datetime'].dt.day
data['month'] = data['datetime'].dt.month
data['weekday'] = data['datetime'].dt.weekday

print("✅ Time features created")

# ==============================
# 4. ADD ADVANCED FEATURES
# ==============================

# Weekend indicator
data['is_weekend'] = data['weekday'].apply(lambda x: 1 if x >= 5 else 0)

# TOU (Time of Use)
def tou(hour):
    if hour >= 22 or hour < 6:
        return 0  # Off-peak
    elif 6 <= hour < 14:
        return 1  # Mid
    else:
        return 2  # Peak

data['tou'] = data['hour'].apply(tou)

# Rolling mean (important for ML performance)
data['rolling_mean'] = data['Global_active_power'].rolling(window=3).mean()

# Drop rows with NaN after rolling
data = data.dropna()

print("✅ Advanced features added")

# ==============================
# 5. REMOVE OUTLIERS (IMPORTANT)
# ==============================
# Remove extreme values (top 1%)
threshold = data['Global_active_power'].quantile(0.99)
data = data[data['Global_active_power'] < threshold]

print("✅ Outliers removed")

# ==============================
# 6. FINAL FEATURES
# ==============================
data = data[
    [
        'hour',
        'day',
        'month',
        'weekday',
        'is_weekend',
        'tou',
        'rolling_mean',
        'Global_active_power'
    ]
]

print(data.head())

# ==============================
# 7. SAVE CLEAN DATA
# ==============================
data.to_csv("data/cleaned_data.csv", index=False)

print("🎉 Preprocessing DONE! File saved as cleaned_data.csv")