# =============================================================================
#  IoT SCADA Telemetry Server
#  Copyright (c) 2026 Saksham (github.com/nanusaksham6). All rights reserved.
#
#  Original author : Saksham
#  Institution     : Thapar Institute of Engineering and Technology
#  Repository      : https://github.com/nanusaksham6/iot-server
#  First published : 9 September 2026
#
#  Licensed under the terms in LICENSE. Unauthorised copying, redistribution,
#  or academic submission of this file by any other individual is prohibited.
# =========================================================================









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

