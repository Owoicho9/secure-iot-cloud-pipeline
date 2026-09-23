import paho.mqtt.client as mqtt
import time
import random
import json

BROKER = "localhost"
PORT = 8883
NODE_ID = "node-01"
TOPIC = f"sensors/{NODE_ID}/temperature"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

client.tls_set(
    ca_certs="certs/ca.crt",
    certfile="certs/node-01.crt",
    keyfile="certs/node-01.key"
)

client.connect(BROKER, PORT, 60)

print(f"{NODE_ID} publishing to {TOPIC} — Ctrl+C to stop")

try:
    while True:
        reading = {
            "node_id": NODE_ID,
            "temperature": round(random.uniform(18.0, 30.0), 2),
            "timestamp": time.time()
        }
        client.publish(TOPIC, json.dumps(reading))
        print(f"Published: {reading}")
        time.sleep(3)
except KeyboardInterrupt:
    print("Stopped.")