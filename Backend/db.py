import mysql.connector

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="vehicle_rental"
    )

    if conn.is_connected():
        print("Connected to MySQL Successfully!")

except Exception as e:
    print("Error:", e)
