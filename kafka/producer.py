import time
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from itertools import cycle
import pandas as pd

#  CONFIG 
CSV_DIR = Path("measurements")
FAST_ROUND_ROBIN = True                     
REPLAY_INTERVAL_SECONDS = 0.4               

USE_KAFKA = True                           
KAFKA_BOOTSTRAP_SERVERS = "kafka:29092"      
KAFKA_TOPIC = "smart-home-measurements"

logging.basicConfig(level=logging.INFO, format='%(message)s')

# Kafka producer
producer = None
if USE_KAFKA:
    from kafka import KafkaProducer
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        acks='all',
        retries=5,
        linger_ms=5,
    )

def load_all_sensors():
    sensors = []
    for file in sorted(CSV_DIR.glob("*.csv")):
        location = file.stem.split("_", 1)[0]
        metric = file.stem.split("_", 1)[1] if "_" in file.stem else file.stem
        try:
            df = pd.read_csv(file, sep=r'\s+', header=None, names=["ts", "value"], engine='python')
            values = [float(x) for x in df["value"].dropna() if str(x).strip()]
            if values:
                sensors.append((location, metric, values))
                logging.info(f"Loaded {file.name:45} → {location:<12} | {metric:<30} | {len(values)} rows")
        except Exception as e:
            logging.error(f"Failed to load {file.name}: {e}")
    return sensors

# Load once at startup
all_sensors = load_all_sensors()
logging.info(f"\nLoaded {len(all_sensors)} sensors → {sum(len(v) for _, _, v in all_sensors)} total measurements\n")

def stream_forever():
    if FAST_ROUND_ROBIN:
        # One value from each sensor in turn 
        iterators = [cycle(values) for _, _, values in all_sensors]
        while True:
            for (location, metric, _), value_iter in zip(all_sensors, iterators):
                value = next(value_iter)
                payload = {
                    "time": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z", 
                    "location": location,
                    "metric": metric,
                    "value": round(value, 4)
                }

                msg = {
                    "schema": {
                        "type": "struct",
                        "fields": [
                            {"type": "string", "optional": False, "field": "time"},
                            {"type": "string", "optional": False, "field": "location"},
                            {"type": "string", "optional": False, "field": "metric"},
                            {"type": "double", "optional": False, "field": "value"}
                        ],
                        "optional": False,
                        "name": "smart_home_measurement"
                    },
                    "payload": payload
                }

                print(f"{payload['time']} | {location:<12} | {metric:<30} | {payload['value']:.4f}")

                if USE_KAFKA:
                    producer.send(KAFKA_TOPIC, value=msg)
                else:
                    print(f"{payload['time']} | {location:<12} | {metric:<30} | {payload['value']:.4f}")
    else:
        # Full historical replay
        cycle_nr = 1
        while True:
            logging.info(f"Starting full replay cycle #{cycle_nr}")
            for location, metric, values in all_sensors:
                for value in values:
                    msg = {
                        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
                        "location": location,
                        "metric": metric,
                        "value": round(value, 4)
                    }
                    if USE_KAFKA:
                        producer.send(KAFKA_TOPIC, value=msg)
                    else:
                        print(f"{msg['timestamp']} | {location:<12} | {metric:<30} | {msg['value']}")
                    time.sleep(0.15)
            cycle_nr += 1

if __name__ == "__main__":
    try:
        stream_forever()
    except KeyboardInterrupt:
        logging.info("\nProducer stopped by user (Ctrl+C)")
        if producer:
            producer.flush(10)
            producer.close()