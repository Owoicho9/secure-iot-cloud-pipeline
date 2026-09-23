import paho.mqtt.client as mqtt
import time
import random
import json

BROKER = "localhost"
PORT = 8883
NODE_ID = "node-02"
TOPIC = f"sensors/{NODE_ID}/humidity"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

client.tls_set(
    ca_certs="certs/ca.crt",
    certfile="certs/node-02.crt",
    keyfile="certs/node-02.key"
)

client.connect(BROKER, PORT, 60)

print(f"{NODE_ID} publishing to {TOPIC} — Ctrl+C to stop")

try:
    while True:
        reading = {
            "node_id": NODE_ID,
            "humidity": round(random.uniform(30.0, 90.0), 2),
            "timestamp": time.time()
        }
        client.publish(TOPIC, json.dumps(reading))
        print(f"Published: {reading}")
        time.sleep(3)
except KeyboardInterrupt:
    print("Stopped.")