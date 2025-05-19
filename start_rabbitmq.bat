@echo off
echo 🚀 Starting RabbitMQ container...
docker start rabbitmq-container

timeout /t 2 > nul
echo ✅ RabbitMQ started!
start http://localhost:15672
