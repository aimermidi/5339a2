import time
import json
import random
import paho.mqtt.client as mqtt

# ---------- MQTT CONFIG ----------
BROKER = "test.mosquitto.org"   # 公共测试服务器
TOPIC = "comp5339/electricity/mock"

# ---------- 模拟设施数据 ----------
FACILITIES = [
    {"name": "Bayswater", "lat": -32.3, "lon": 150.9, "state": "NSW"},
    {"name": "Eraring", "lat": -33.1, "lon": 151.5, "state": "NSW"},
    {"name": "Torrens Island", "lat": -34.8, "lon": 138.5, "state": "SA"},
]

# ---------- 启动客户端 ----------
client = mqtt.Client()
client.connect(BROKER, 1883, 60)

print(f"✅ Connected to broker: {BROKER}")
print(f"📡 Publishing to topic: {TOPIC}")

try:
    while True:
        facility = random.choice(FACILITIES)
        msg = {
            "facility": facility["name"],
            "state": facility["state"],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "power_MW": round(random.uniform(300, 2500), 1),
            "co2_tonnes": round(random.uniform(100, 800), 1),
            "lat": facility["lat"],
            "lon": facility["lon"]
        }
        client.publish(TOPIC, json.dumps(msg))
        print("Published:", msg)
        time.sleep(0.1)  # 模拟流式发布
except KeyboardInterrupt:
    print("\n🛑 Stopped publishing.")
    client.disconnect()
