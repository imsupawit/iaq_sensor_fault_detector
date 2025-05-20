# iaq_sensor_fault_detector
This repository contains a complete IoT system for monitoring indoor air quality (IAQ) using sensor data, detecting faults, and predicting future sensor failures with machine learning.

# Project Goals
Monitor IAQ in real-time
Detect and categorize sensor faults
Log historical sensor data
Predict future fault rates using AI
Send automated email alerts to users

# System Components

# Real-Time Simulation
sensor_publisher.py – Simulates 15 IAQ sensors and publishes their data to RabbitMQ every 15 seconds. Includes:
Normal sensors 1-5
Disconnected (stuck) sensors6-8
Sensors sending invalid data 9-11
CO₂ danger sensors 12-15

# Fault Detection
fault_detector.py – Subscribes to the RabbitMQ queue iaq_data, detects:
Disconnected sensors (no change for 10 minutes)
Physically impossible values
High CO₂ levels (> 1000 ppm for 20 minutes

Logs each reading and fault to iaq_log.csv
Optionally sends alerts using send_email()

# Email Notification
email_alert.py – Sends alert emails for each fault type:
Invalid data 🚨
Disconnection ❌
High CO₂ ☠️

# Hardware Extension
fire_detector.py – Monitors a GPIO pin for fire detection via fusible wire (for Raspberry Pi). Sends an alert on open circuit.

# AI-Powered Fault Forecasting

# Daily Stats
daily_fault_tracker.py – Analyzes iaq_log.csv daily, summarizes sensor faults, and logs to sensor_health_log.csv

# AI Forecast
train_fault_forecast_model.py – Trains a per-sensor LinearRegression model to forecast fault percent for the next day
Flags any predicted fault > 10% with a replacement warning

# How to Run the System

Requirements:
Python 3.11+
Docker (for RabbitMQ)

Quick Start:
Run RabbitMQ server:

docker run -d --restart unless-stopped \
  --hostname rabbitmq-test \
  --name rabbitmq-container \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management

OR double-click start_rabbitmq.bat

Run the publisher:
py sensor_publisher.py

Run the fault detector:
py fault_detector.py

(Daily) Run health tracker:
py daily_fault_tracker.py

Run the AI predictor:
py train_fault_forecast_model.py

# Files

sensor_publisher.py – Data generator 

fault_detector.py – Fault detection + logging

email_alert.py – Notification handler

fire_detector.py – Hardware trigger alert

iaq_log.csv – Daily logs

sensor_health_log.csv – Daily fault summaries

train_fault_forecast_model.py – AI model trainer

sensor_health_models.joblib – Saved ML models

start_rabbitmq.bat – One-click RabbitMQ starter


# Discussions : 
 Sub-Problem 1 – IAQ Sensor Study & Recommendation
 | Sensor     | Temp Range (°C) | CO₂   | Humidity  | Accuracy                            | Interface | Python Support  | Power Use | Price    | Notes                                        |
| ----------- | --------------- | ---   | --------  | ----------------------------------- | --------- | --------------  | --------- | ------   | -------------------------------------------- |
| **SCD40**   | –10 to 60       | ✅   | ✅        | ±0.5 °C, ±4% RH, ±(50 ppm + 5%) CO₂ | I²C       | ✅ Official lib | Low       | 1,872.50 บ.| Compact, 3-in-1 sensor, indoor IAQ optimized |
| **DS18B20** | –55 to 125      | ❌   | ❌        | ±0.5 °C                             | 1-Wire    | ✅ Very common  | Ultra-low | 85บ.      | Great range, but temp-only                   |
| **BME280**  | –40 to 85       | ❌   | ✅        | ±1 °C, ±3% RH                       | I²C / SPI | ✅ Adafruit lib | Low       | 100บ.   | High-quality for temp/hum/pressure             |
| **DHT22**   | –40 to 80       | ❌   | ✅        | ±0.5 °C, ±2–5% RH                   | Digital   | ✅ Adafruit lib | Low       | 260บ.      | Very cheap, but slow and less accurate      |
| **MH-Z19B** | 0 to 50         | ✅   | ❌        | ±(50 ppm + 5%) CO₂                  | UART      | ✅ with serial  | Moderate  | 950บ.    | Reliable CO₂, no temp/hum                     |
| **BME680**  | –40 to 85       | ❌   | ✅        | ±1 °C, ±3% RH                       | I²C / SPI | ✅              | Low–mod.  | 270 บ. | IAQ index estimate (not true CO₂)               |
| **PASCO2V15AUMA1**  |         | CO₂ only  |        | ±50 ppm ±5%, 0–32,000 ppm          | I²C/UART  | ✅ Official GitHub |Low     | 703.61  บ.         

The first candidate was the SCD40, a popular all-in-one IAQ sensor that measures:
CO₂ (up to ~5000 ppm)
Temperature (–10 to 60 °C)
Humidity (0–100% RH)
It’s I²C-based, accurate, and well-supported in Python. However, we discovered that its price is higher than combining two individual sensors.

This PAS CO₂ + BME280 combo provides:
Higher CO₂ detection range than SCD40
Modular design: easier to maintain or upgrade
Full Python compatibility with official support
https://github.com/Infineon/arduino-pas-co2-sensor

https://github.com/pimoroni/bme280-python
Lower total cost than SCD40
Option to position temp and CO₂ sensors separately for better readings

Go-Beyond Feature
Since CO₂ sensors are not designed to survive fire, we added a fusible wire connected to a GPIO pin. If extreme heat occurs, the wire melts, breaks the circuit, and triggers an email alert — making the system fire-aware in hardware.

# Alert Notification Design
I chose email as the user alert channel because:
It’s easy to implement and test
It works even when the user isn’t watching a dashboard

# AI Prediction Module
I trained a per-sensor Linear Regression model to forecast tomorrow’s fault percentage. This helps:
Proactively replace degrading sensors
Reduce long-term maintenance cost
Move toward predictive maintenance in IoT systems
A sensor is flagged if predicted fault % > 10%.
