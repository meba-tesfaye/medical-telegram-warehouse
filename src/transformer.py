import os
import json
import re
import pandas as pd

# Define Data Lake Paths
RAW_DIR = "data/raw/telegram_messages"
CLEANED_DIR = "data/cleaned"

def extract_price(text):
    """
    Regex helper to extract currency values (e.g., '450 ETB', '450 birr', 'Price: 450')
    """
    if not text:
        return None
    # Look for numbers followed or preceded by common Ethiopian currency terms
    match = re.search(r'(\d+)\s*(?:etb|birr|ብር)|(?:price|ዋጋ)\s*[:=-]?\s*(\d+)', text, re.IGNORECASE)
    if match:
        return int(match.group(1) or match.group(2))
    return None

def clean_text(text):
    """
    Removes messy excess whitespaces and system symbols from message text
    """
    if not text:
        return ""
    # Strip out newline clusters and replace with single space
    cleaned = re.sub(r'\s+', ' ', text)
    return cleaned.strip()

def transform_data():
    print("⚡ Starting Data Transformation Pipeline...")
    transformed_records = []

    # Check if raw data directory exists
    if not os.path.exists(RAW_DIR):
        print(f"❌ Error: Raw data directory {RAW_DIR} not found. Run the scraper first!")
        return

    # Loop through partitioned date folders in data/raw/telegram_messages/
    for date_folder in os.listdir(RAW_DIR):
        folder_path = os.path.join(RAW_DIR, date_folder)
        if not os.path.isdir(folder_path):
            continue
            
        # Process each JSON message inside the folder
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".json"):
                file_path = os.path.join(folder_path, file_name)
                
                with open(file_path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                
                # Transform & Normalize fields
                raw_text = raw_data.get("message_text", "")
                cleaned_msg = clean_text(raw_text)
                estimated_price = extract_price(raw_text)
                
                # Standardize timestamps down to standard date format
                iso_date = raw_data.get("message_date", "")
                formatted_date = iso_date.split("T")[0] if iso_date else date_folder
                
                record = {
                    "message_id": raw_data.get("message_id"),
                    "channel": raw_data.get("channel_name", "").strip("@"),
                    "date": formatted_date,
                    "cleaned_text": cleaned_msg,
                    "extracted_price_etb": estimated_price,
                    "has_media": raw_data.get("has_media", False),
                    "image_path": raw_data.get("image_path"),
                    "views": raw_data.get("views", 0),
                    "forwards": raw_data.get("forwards", 0)
                }
                transformed_records.append(record)

    # Convert normalized list to Pandas DataFrame
    if transformed_records:
        df = pd.DataFrame(transformed_records)
        
        # Create output directory
        os.makedirs(CLEANED_DIR, exist_ok=True)
        
        # Save clean warehouse table to CSV format
        output_csv = os.path.join(CLEANED_DIR, "cleaned_medical_data.csv")
        df.to_csv(output_csv, index=False, encoding="utf-8")
        
        print(f"✅ Success! Processed {len(df)} files.")
        print(f"💾 Clean structured warehouse file saved to: {output_csv}")
        print("\nPreview of transformed warehouse structure:")
        print(df[["channel", "date", "extracted_price_etb", "views"]].head())
    else:
        print("⚠ No records found to process.")

if __name__ == "__main__":
    transform_data()