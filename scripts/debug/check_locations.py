import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()
from db import get_or_create_default_user, get_saved_locations

user_id = get_or_create_default_user()
print(get_saved_locations(user_id))