from dotenv import load_dotenv
load_dotenv()
from db import get_or_create_default_user, get_saved_locations

user_id = get_or_create_default_user()
print(get_saved_locations(user_id))