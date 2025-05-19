import pika
import json
import random
import time
from datetime import datetime

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='iaq_data')

# Sensor roles
normal_sensors = [f"sensor_{i:02}" for i in range(1, 6)]
stuck_sensors = [f"sensor_{i:02}" for i in range(6, 9)]
invalid_sensors = [f"sensor_{i:02}" for i in range(9, 12)]
co2_danger_sensors = [f"sensor_{i:02}" for i in range(12, 16)]

# Keep values for stuck sensors
stuck_values = {
    sensor_id: {
        "temperature": round(random.uniform(22.0, 25.0), 2),
        "humidity": round(random.uniform(40.0, 50.0), 2),
        "co2": random.randint(450, 600)
    }
    for sensor_id in stuck_sensors
}

print("📡 Sending MIXED sensor data every 15 seconds... Press Ctrl+C to stop.\n")

try:
    while True:
        all_sensors = normal_sensors + stuck_sensors + invalid_sensors + co2_danger_sensors
        for sensor_id in all_sensors:
            timestamp = datetime.utcnow().isoformat()

            if sensor_id in normal_sensors:
                temp = round(random.uniform(22.0, 28.0), 2)
                hum = round(random.uniform(40.0, 60.0), 2)
                co2 = random.randint(450, 800)

            elif sensor_id in stuck_sensors:
                # Reuse fixed value every time
                val = stuck_values[sensor_id]
                temp = val["temperature"]
                hum = val["humidity"]
                co2 = val["co2"]

            elif sensor_id in invalid_sensors:
                temp = random.choice([999, -999, 1234])     # impossible temps
                hum = random.choice([-10, 150])             # impossible humidity
                co2 = random.choice([-500, 20000])          # impossible CO₂

            elif sensor_id in co2_danger_sensors:
                temp = round(random.uniform(22.0, 25.0), 2)
                hum = round(random.uniform(45.0, 55.0), 2)
                co2 = random.randint(1100, 1400)            # persistently high CO₂

            data = {
                "sensor_id": sensor_id,
                "timestamp": timestamp,
                "temperature": temp,
                "humidity": hum,
                "co2": co2
            }

            channel.basic_publish(
                exchange='',
                routing_key='iaq_data',
                body=json.dumps(data)
            )

            print(f"✅ Sent from {sensor_id}: {data}")

        time.sleep(5)

except KeyboardInterrupt:
    print("\n🛑 Stopped by user.")
finally:
    connection.close()
