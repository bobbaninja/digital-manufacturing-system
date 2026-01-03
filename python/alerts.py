import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect("../sql/manufacturing.db")
df = pd.read_sql("SELECT * FROM validated_data", conn)
conn.close()

# Check for alerts
threshold = 3
alerts = df[df["consecutive_failures"] > threshold]

if not alerts.empty:
    print("ALERT: Serial numbers with consecutive failures > 3:")
    for _, row in alerts.iterrows():
        print(f"Serial: {row['serial_number']}, Failures: {row['consecutive_failures']}")
else:
    print("No alerts.")