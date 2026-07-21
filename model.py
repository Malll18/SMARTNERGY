import pandas as pd
import numpy as np
import time
import joblib
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, HistGradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

print("🚀 Start Model Training...")

# Load cleaned data
data = pd.read_csv("data/cleaned_data.csv")
print("✅ Data loaded!")

X = data[['hour', 'day', 'month', 'weekday', 'tou']]
y = data['Global_active_power']

# Temporal split (no shuffling — this is time-series data)
split_idx = int(len(data) * 0.8)
X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
print("✅ Data split!")

# ==============================
# MODELS TO COMPARE
# ==============================
models = {
    "Linear Regression": LinearRegression(),
    "Ridge Regression": Ridge(alpha=1.0),
    "Decision Tree": DecisionTreeRegressor(max_depth=12, random_state=42),
    "Random Forest": RandomForestRegressor(
        n_estimators=100, max_depth=15, n_jobs=-1, random_state=42
    ),
    "Extra Trees": ExtraTreesRegressor(
        n_estimators=100, max_depth=15, n_jobs=-1, random_state=42
    ),
    "Hist Gradient Boosting": HistGradientBoostingRegressor(
        max_iter=200, random_state=42
    ),
    "Neural Network (MLP)": make_pipeline(
        StandardScaler(),
        MLPRegressor(hidden_layer_sizes=(64, 32), max_iter=50,
                     early_stopping=True, random_state=42)
    ),
}

# ==============================
# TRAIN & EVALUATE
# ==============================
results = []
best_model, best_mae, best_name = None, float("inf"), None

for name, model in models.items():
    start = time.time()
    model.fit(X_train, y_train)
    pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, pred)
    rmse = np.sqrt(mean_squared_error(y_test, pred))
    r2 = r2_score(y_test, pred)
    elapsed = time.time() - start

    results.append([name, mae, rmse, r2, elapsed])
    print(f"✅ {name}: MAE={mae:.4f} | RMSE={rmse:.4f} | R²={r2:.4f} | {elapsed:.1f}s")

    if mae < best_mae:
        best_mae, best_model, best_name = mae, model, name

# ==============================
# RESULTS TABLE
# ==============================
results_df = pd.DataFrame(results, columns=["Model", "MAE", "RMSE", "R²", "Train time (s)"])
results_df = results_df.sort_values("MAE").reset_index(drop=True)
print("\n📊 MODEL COMPARISON")
print(results_df.to_string(index=False))
results_df.to_csv("data/model_comparison.csv", index=False)

# ==============================
# SAVE BEST MODEL
# ==============================
joblib.dump(best_model, "model.pkl")
print(f"\n🏆 Best model: {best_name} (MAE={best_mae:.4f}) — saved as model.pkl")
