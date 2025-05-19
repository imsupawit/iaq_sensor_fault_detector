import pandas as pd
from datetime import datetime

# Load the full log
df = pd.read_csv("iaq_log.csv")

# Convert timestamp column to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Keep only today's data (or customize the date range)
today = datetime.utcnow().date()
df_today = df[df['timestamp'].dt.date == today]

if df_today.empty:
    print("📭 No data for today.")
    exit()

# Count total readings and valid fault types only
def is_faulty(msg):
    if not isinstance(msg, str):
        return False
    msg = msg.lower()
    return "invalid" in msg or "disconnected" in msg or "stuck" in msg

grouped = df_today.groupby('sensor_id').agg(
    total_readings=('timestamp', 'count'),
    fault_count=('fault_detected', lambda x: sum(is_faulty(val) for val in x))
)

grouped['fault_percent'] = (grouped['fault_count'] / grouped['total_readings']) * 100
grouped['date'] = today

# Save or append to health log
health_log_path = "sensor_health_log.csv"
try:
    existing = pd.read_csv(health_log_path)
    updated = pd.concat([existing, grouped.reset_index()], ignore_index=True)
except FileNotFoundError:
    updated = grouped.reset_index()

updated.to_csv(health_log_path, index=False)
print(f"✅ Sensor health stats saved for {today}")

