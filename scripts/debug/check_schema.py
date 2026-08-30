import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()
from db import get_connection

conn = get_connection()
schema = conn.execute("SELECT sql FROM sqlite_master WHERE name='saved_locations'").fetchone()
print(schema["sql"])