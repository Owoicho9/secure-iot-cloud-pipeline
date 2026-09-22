# Secure IoT-to-Cloud Sensor Network

A simulated IoT pipeline demonstrating secure device-to-cloud data flow: 
sensor nodes publish over MQTT, data is authenticated and encrypted in transit, 
and (eventually) stored and visualized via a cloud-deployed backend.


## Roadmap

- Week 1: Basic MQTT pub/sub with simulated nodes
- Week 2: TLS/mTLS security, per-device authentication, threat model
- Week 3: Cloud deployment, InfluxDB + Grafana dashboard
- Week 4: Documentation, demo video, final polish

## Status: Week 1 complete — basic MQTT pub/sub pipeline
## Architecture (Week 1)

3 simulated sensor nodes → Mosquitto MQTT broker → subscriber (logs to console)

- `sensor_node.py` — publishes simulated temperature readings (`sensors/node-01/temperature`)
- `sensor_node_2.py` — publishes simulated humidity readings (`sensors/node-02/humidity`)
- `sensor_node_3.py` — publishes simulated motion readings (`sensors/node-03/motion`)
- `subscriber.py` — subscribes to `sensors/#` (all nodes) and logs incoming data

## Why MQTT
MQTT uses a publish/subscribe model: publishers and subscribers never talk directly, 
only through the broker. This decouples devices from consumers — new sensor nodes 
can be added without changing subscriber code, and vice versa.

## Setup

1. Install Mosquitto
2. `python -m venv venv`
3. `venv\Scripts\activate` (Windows)
4. `pip install -r requirements.txt`

## Running it

Open separate terminals for each (activate venv in each Python one):
mosquitto -v
python subscriber.py
python sensor_node.py
python sensor_node_2.py
python sensor_node_3.py

