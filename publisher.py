import json
import random
import time
from datetime import datetime

import paho.mqtt.publish as publish

while True:
    data = {
        "device_id": "MOTOR_01",
        "timestamp": datetime.now().isoformat(),
        "vibration": round(random.uniform(2.0, 5.0), 2),
        "temperature": round(random.uniform(35, 50), 2),
        "rpm": random.randint(1400, 1500)
    }

    publish.single(
        topic="test/topic",
        payload=json.dumps(data),
        hostname="127.0.0.1"
    )

    print("Sent:", data)

    time.sleep(2)

