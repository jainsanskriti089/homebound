from dotenv import load_dotenv
load_dotenv()
from db import get_connection
conn = get_connection()
conn.execute("DELETE FROM location_readings")
conn.execute("DELETE FROM geofence_events")
conn.commit()
conn.close()
print("Cleared test history")