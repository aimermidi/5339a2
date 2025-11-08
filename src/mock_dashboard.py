import os
import json
import time
import folium
import threading
import paho.mqtt.client as mqtt
import streamlit as st
from streamlit_folium import st_folium

# ---------- MQTT CONFIG ----------
BROKER = "test.mosquitto.org"
TOPIC = "comp5339/electricity/mock"

# ---------- FILE PATH ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "../data/samples/mock_cache.json")
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

# ---------- GLOBAL CACHE ----------
latest_data = {}

# ---------- MQTT CALLBACK ----------
def on_message(client, userdata, msg):
    global latest_data
    try:
        data = json.loads(msg.payload.decode())
        latest_data[data["facility"]] = data

        # 写入缓存文件并强制刷新到磁盘
        with open(DATA_FILE, "w") as f:
            json.dump(latest_data, f)
            f.flush()
            os.fsync(f.fileno())

        print("📩 Received:", data)
        print("💾 Writing to:", DATA_FILE)
    except Exception as e:
        print("⚠️ Error parsing message:", e)


def mqtt_listener():
    """后台监听线程"""
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(BROKER, 1883, 60)
    client.subscribe(TOPIC)
    client.loop_forever()


# ---------- 启动监听线程 ----------
threading.Thread(target=mqtt_listener, daemon=True).start()

# ---------- Streamlit 页面 ----------
st.set_page_config(page_title="COMP5339 Electricity Dashboard", layout="wide")
st.title("⚡ Mock Electricity Data Dashboard")

placeholder = st.empty()

while True:
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except Exception:
        data = {}

    if not data:
        st.warning("⚠️ No data received yet. Please ensure mock_publisher.py is running.")
        time.sleep(2)
        continue
    else:
        st.success(f"✅ Received {len(data)} facilities.")
        st.write(f"**Last Updated:** {time.strftime('%H:%M:%S')}")

    # ---------- 创建地图 ----------
    m = folium.Map(location=[-33.5, 151.0], zoom_start=5)
    for d in data.values():
        popup = (
            f"<b>{d['facility']}</b><br>"
            f"Power: {d['power_MW']} MW<br>"
            f"CO₂: {d['co2_tonnes']} tonnes<br>"
            f"Time: {d['timestamp']}"
        )
        folium.Marker(
            location=[d["lat"], d["lon"]],
            popup=popup,
            icon=folium.Icon(color="green", icon="bolt"),
        ).add_to(m)

    # ---------- 更新地图 ----------
    with placeholder:
        st_folium(m, width=700, height=500, key=f"map_{int(time.time())}")

    time.sleep(2)
