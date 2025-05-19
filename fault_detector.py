import pika
import json
from datetime import datetime, timedelta
from email_alert import send_email
import csv
import os

# Log file setup
log_filename = "iaq_log.csv"

# Create CSV file with headers if it doesn't exist yet
if not os.path.exists(log_filename):
    with open(log_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "sensor_id", "temperature", "humidity", "co2", "fault_detected"])

def log_to_csv(timestamp, sensor_id, temp, hum, co2, fault_msg=""):
    with open(log_filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, sensor_id, temp, hum, co2, fault_msg])


# Track state for each sensor
sensor_data_log = {}

# Fault thresholds
MAX_CO2 = 1000
CO2_TIME_LIMIT = timedelta(minutes=20)
DISCONNECT_TIME_LIMIT = timedelta(minutes=10)

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='iaq_data')

print("🕵️ Listening for sensor data...")

def callback(ch, method, properties, body):
    fault_msg = ""
    data = json.loads(body)
    sensor_id = data['sensor_id']
    timestamp = datetime.fromisoformat(data['timestamp'])
    temp = data['temperature']
    hum = data['humidity']
    co2 = data['co2']

    now = datetime.utcnow()

    if sensor_id not in sensor_data_log:
        sensor_data_log[sensor_id] = {
            'last_values': [],
            'last_time': timestamp,
            'co2_high_since': None
        }

    log = sensor_data_log[sensor_id]

    # Check for same values (disconnection simulation)
    log['last_values'].append((temp, hum, co2))
    if len(log['last_values']) > 40:  # keep data for 10+ minutes (~15s each) (60/15 * 10)
        log['last_values'].pop(0)

    if all(val == log['last_values'][0] for val in log['last_values']):
        if now - log['last_time'] > DISCONNECT_TIME_LIMIT:
            fault_msg += " Disconnected or stuck; "
            send_email("disconnected", sensor_id, now, temp, hum, co2, extra=log['last_time'])
            print(f"❌ {sensor_id} might be disconnected or stuck (no change > 10 mins)")
    else:
        log['last_time'] = now  # reset disconnect timer if values changed

    # Check for physically impossible values
    if temp > 100 or temp < -50 or hum < 0 or hum > 100 or co2 < 0 or co2 > 10000:
        fault_msg += "🚨 Invalid data; "
        print(f"🚨 {sensor_id} sent invalid data! Temp: {temp}, Hum: {hum}, CO₂: {co2}")
        send_email("invalid_data", sensor_id, timestamp, temp, hum, co2)

    # Check for long-term high CO₂
    if co2 > MAX_CO2:
        if log['co2_high_since'] is None:
            log['co2_high_since'] = now
        elif now - log['co2_high_since'] > CO2_TIME_LIMIT:
            fault_msg += "☠️ CO₂ > 1000ppm too long; "
            print(f"☠️ {sensor_id} CO₂ has been dangerously high for over 20 minutes!")
            send_email("high_co2", sensor_id, now, temp, hum, co2, extra=log['co2_high_since'])

    else:
        log['co2_high_since'] = None
    log_to_csv(timestamp, sensor_id, temp, hum, co2, fault_msg.strip())


channel.basic_consume(queue='iaq_data', on_message_callback=callback, auto_ack=True)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("\n🛑 Stopped fault detection.")
finally:
    connection.close()
