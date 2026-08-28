import asyncio
from dotenv import load_dotenv
load_dotenv()

from notifications import notify

async def main():
    await notify("This is a test notification from your Python script")

asyncio.run(main())