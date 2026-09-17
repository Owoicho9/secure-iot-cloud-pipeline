import paho.mqtt.client as mqtt
import time
import random
import json

BROKER = "localhost"
PORT = 1883
NODE_ID = "node-03"
TOPIC = f"sensors/{NODE_ID}/motion"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(BROKER, PORT, 60)

print(f"{NODE_ID} publishing to {TOPIC} — Ctrl+C to stop")

try:
    while True:
        reading = {
            "node_id": NODE_ID,
            "motion": random.choice([0, 1]),
            "timestamp": time.time()
        }
        client.publish(TOPIC, json.dumps(reading))
        print(f"Published: {reading}")
        time.sleep(3)
except KeyboardInterrupt:
    print("Stopped.")