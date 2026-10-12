import os
import json
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

load_dotenv()  # reads the .env file in the current folder

BROKER = "localhost"
PORT = 8883
TOPIC = "sensors/#"

INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = os.environ["INFLUXDB_TOKEN"]
INFLUX_ORG = os.environ["INFLUXDB_ORG"]
INFLUX_BUCKET = os.environ["INFLUXDB_BUCKET"]

influx = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = influx.write_api(write_options=SYNCHRONOUS)

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Connected to broker (rc={rc})")
    client.subscribe(TOPIC)
    print(f"Subscribed to {TOPIC}")

def on_message(client, userdata, msg):
    print(f"[{msg.topic}] {msg.payload.decode()}")
    try:
        data = json.loads(msg.payload.decode())
        _, node_id, sensor_type = msg.topic.split("/")
        point = (
            Point("sensor_reading")
            .tag("node_id", node_id)
            .field(sensor_type, float(data[sensor_type]))
            .time(int(data["timestamp"] * 1e9), WritePrecision.NS)
        )
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
    except Exception as e:
        print(f"Failed to write to InfluxDB: {e}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

client.tls_set(
    ca_certs="certs/ca.crt",
    certfile="certs/subscriber.crt",
    keyfile="certs/subscriber.key"
)

client.connect(BROKER, PORT, 60)
client.loop_forever()