import sys
import types

# 1. Force inject a mock pyaes module into memory to completely bypass the Windows path bug
if "pyaes" not in sys.modules:
    mock_pyaes = types.ModuleType("pyaes")
    sys.modules["pyaes"] = mock_pyaes

# 2. Now import your packages safely
import os
import json
import logging
from datetime import datetime
import asyncio
from telethon import TelegramClient
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()
API_ID = os.getenv("TG_API_ID")
API_HASH = os.getenv("TG_API_HASH")

if not API_ID or not API_HASH:
    raise ValueError("TG_API_ID or TG_API_HASH missing from .env file!")

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/scraping.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Target Channels (Updated with correct @CheMed123 handle)
CHANNELS = ["@CheMed123", "@lobelia4cosmetics", "@TikvahPharma"]

async def scrape_channel(client, channel_name):
    logging.info(f"Starting to scrape channel: {channel_name}")
    print(f"\n--- Scraping {channel_name} ---")
    
    try:
        count = 0
        async for message in client.iter_messages(channel_name, limit=50):
            msg_date = message.date.strftime("%Y-%m-%d")
            msg_id = message.id
            clean_channel = channel_name.strip("@")
            
            # Setup Partitioned Directory
            lake_dir = f"data/raw/telegram_messages/{msg_date}"
            os.makedirs(lake_dir, exist_ok=True)
            
            # Handle Image Downloads
            image_path = None
            if message.photo:
                img_dir = f"data/raw/images/{clean_channel}"
                os.makedirs(img_dir, exist_ok=True)
                image_path = f"{img_dir}/{msg_id}.jpg"
                await message.download_media(file=image_path)
            
            # Build clean JSON payload
            payload = {
                "message_id": msg_id,
                "channel_name": channel_name,
                "message_date": message.date.isoformat(),
                "message_text": message.text or "",
                "has_media": True if message.photo else False,
                "image_path": image_path,
                "views": message.views or 0,
                "forwards": message.forwards or 0
            }
            
            # Save raw data
            file_path = f"{lake_dir}/{clean_channel}_{msg_id}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=4)
            
            count += 1
            if count % 10 == 0:
                print(f"Downloaded {count} messages from {channel_name}...")
                
        logging.info(f"Successfully scraped channel: {channel_name}")
        print(f"Finished {channel_name}! Saved {count} items.")
    except Exception as e:
        logging.error(f"Error scraping {channel_name}: {str(e)}")
        print(f"Error scraping {channel_name}: {e}")

async def main():
    async with TelegramClient("scraper_session", int(API_ID), API_HASH) as client:
        for channel in CHANNELS:
            await scrape_channel(client, channel)

if __name__ == "__main__":
    asyncio.run(main())