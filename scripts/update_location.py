from dotenv import load_dotenv
load_dotenv()
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db import get_connection

conn = get_connection()
conn.execute(
    "UPDATE saved_locations SET latitude = ?, longitude = ?, radius_m = ? WHERE id = 1",
    (37.369169, -122.079839, 50)  # 2500 Grant Rd 
)
conn.commit()
conn.close()
print("Location updated")