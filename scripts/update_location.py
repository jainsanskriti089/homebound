from dotenv import load_dotenv
load_dotenv()
from db import get_connection

conn = get_connection()
conn.execute(
    "UPDATE saved_locations SET latitude = ?, longitude = ?, radius_m = ? WHERE id = 1",
    (37.368431, -122.079506, 50)  # 2500 Grant Rd 
)
conn.commit()
conn.close()
print("Location updated")