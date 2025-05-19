import smtplib
from email.mime.text import MIMEText

SENDER_EMAIL = "srinansupawit@gmail.com"
SENDER_PASSWORD = "mvtmmeebcadqnbls"  # ← no spaces, just straight 16 characters
RECEIVER_EMAIL = "6532176821@student.chula.ac.th"  # Or any email you want alerts sent to

def send_email(fault_type, sensor_id, timestamp, temp, hum, co2, extra=None):
    subject = ""
    body = ""

    if fault_type == "invalid_data":
        subject = f"🚨 Invalid Data from {sensor_id}"
        body = f"""Sensor {sensor_id} reported values outside physical limits:

Temperature: {temp} °C
Humidity: {hum} %
CO₂: {co2} ppm
Timestamp: {timestamp}
"""
    elif fault_type == "disconnected":
        subject = f"❌ {sensor_id} Disconnected or Stuck"
        body = f"""Sensor {sensor_id} has not changed readings for over 10 minutes.

Last recorded values:
Temperature: {temp} °C
Humidity: {hum} %
CO₂: {co2} ppm
Last update: {extra}
Now: {timestamp}
"""
    elif fault_type == "high_co2":
        subject = f"☠️ High CO₂ Alert: {sensor_id}"
        body = f"""Sensor {sensor_id} has reported high CO₂ levels for over 20 minutes.

Current CO₂: {co2} ppm
High since: {extra}
Now: {timestamp}
"""

    # Send the email
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)
        print(f"📧 Email sent for {fault_type} from {sensor_id}!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")