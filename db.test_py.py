import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        database="iot_db",
        user="postgres",
        password="1234",   # Try 1234 first
        port="5432"
    )

    print("✅ Database Connected Successfully!")

    conn.close()

except Exception as e:
    print("❌ Connection Failed")
    print(e)