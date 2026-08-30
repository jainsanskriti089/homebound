from dotenv import load_dotenv
load_dotenv()
from db import get_connection

conn = get_connection()
conn.execute(
    "UPDATE saved_locations SET expected_leave_start = ?, expected_leave_end = ? WHERE id = 1",
    ("01:00", "02:00")
)
conn.commit()
conn.close()
print("Window set to the past")