import json
import paho.mqtt.client as mqtt
import psycopg2

# ---------------- DATABASE ---------------- #

conn = psycopg2.connect(
    host="localhost",
    database="iot_db",
    user="postgres",
    password="1234",
    port="5432"
)

cursor = conn.cursor()

# ---------------- MQTT ---------------- #

def on_connect(client, userdata, flags, reason_code, properties=None):
    print("Connected to MQTT Broker!")
    client.subscribe("test/topic")
    print("Subscribed to test/topic")


def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())

    print("\n========== NEW SENSOR DATA ==========")
    print(data)

    cursor.execute("""
        INSERT INTO vibration_data
        (device_id, timestamp, vibration, temperature, rpm)
        VALUES (%s,%s,%s,%s,%s)
    """, (
        data["device_id"],
        data["timestamp"],
        data["vibration"],
        data["temperature"],
        data["rpm"]
    ))

    conn.commit()

    print("✅ Stored in PostgreSQL")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

client.on_connect = on_connect
client.on_message = on_message

client.connect("127.0.0.1",1883)

client.loop_forever()