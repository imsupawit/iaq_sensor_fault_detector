import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import joblib

# Load the health log
df = pd.read_csv("sensor_health_log_for_train.csv")

# Ensure correct types
df['date'] = pd.to_datetime(df['date'])
df['day_index'] = df['date'].rank(method='dense').astype(int)  # use rank as a simple time index

# Group by sensor
models = {}
predictions = {}

for sensor_id in df['sensor_id'].unique():
    sensor_data = df[df['sensor_id'] == sensor_id].sort_values('day_index')
    
    if len(sensor_data) < 3:
        print(f"📭 Not enough data for {sensor_id}, skipping.")
        continue

    X = sensor_data[['day_index']]
    y = sensor_data['fault_percent']

    # Try both and choose one you like
    #model = RandomForestRegressor(n_estimators=100, random_state=42)
    model = LinearRegression()

    model.fit(X, y)
    next_day = [[X['day_index'].max() + 1]]
    predicted = model.predict(next_day)[0]

    models[sensor_id] = model
    predictions[sensor_id] = predicted

# Save models and predictions
joblib.dump(models, 'sensor_health_models.joblib')

print("\n🔮 Predicted Fault % for Tomorrow:")
for sensor_id, pred in predictions.items():
    print(f"  {sensor_id}: {pred:.2f}%")
    if pred > 10:
        print(f"  ⚠️  Consider replacing {sensor_id} soon!")
