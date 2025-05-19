import RPi.GPIO as GPIO
import time
from email_alert import send_email
from datetime import datetime

# GPIO pin where fusible wire circuit is connected
FIRE_PIN = 17  # BCM pin 17 (physical pin 11)

GPIO.setmode(GPIO.BCM)
GPIO.setup(FIRE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

sensor_id = "hardware_fire_sensor"
temp = hum = co2 = -1  # placeholder, since these are unknown from GPIO

print("🔥 Fire detector activated. Monitoring fusible wire...")

try:
    while True:
        if GPIO.input(FIRE_PIN) == GPIO.HIGH:
            timestamp = datetime.utcnow().isoformat()
            print("🔥🔥 FUSIBLE WIRE MELTED! FIRE DETECTED!")
            send_email("fire", sensor_id, timestamp, temp, hum, co2, extra="Fusible wire open circuit")
            # Wait to prevent multiple repeated alerts
            time.sleep(60)
        else:
            print("✅ Fusible wire intact.")
        time.sleep(5)

except KeyboardInterrupt:
    print("\n🛑 Fire monitoring stopped.")
finally:
    GPIO.cleanup()
