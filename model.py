import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

print("🚀 Start Model Training...")

# Load cleaned data
data = pd.read_csv("data/cleaned_data.csv")

print("✅ Data loaded!")

# Features & target
X = data[['hour','day','month','weekday','tou']]
y = data['Global_active_power']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

print("✅ Data split!")

# Train model
model = RandomForestRegressor()
model.fit(X_train, y_train)

print("✅ Model trained!")

# Predict
pred = model.predict(X_test)

# Evaluate
mae = mean_absolute_error(y_test, pred)

print(f"📊 MAE: {mae}")

print("🎉 DONE!")