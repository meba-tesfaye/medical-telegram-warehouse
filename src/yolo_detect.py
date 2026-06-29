import os
import csv
import logging
from functools import partial
import torch

# Force all downstream torch.load calls to run with weights_only=False
torch.load = partial(torch.load, weights_only=False)

from ultralytics import YOLO

# Setup Logging Configs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def determine_image_category(detected_labels):
    """
    Categorizes the image based on specific YOLO pre-trained COCO object overlaps:
    - promotional: Contains a person AND a product container (bottle/cup/vase/etc)
    - product_display: Contains product containers (bottle, etc), no person
    - lifestyle: Contains a person, no product containers
    - other: Neither detected
    """
    has_person = 'person' in detected_labels
    has_product_container = any(item in detected_labels for item in ['bottle', 'cup', 'bowl', 'box', 'vase', 'refrigerator'])

    if has_person and has_product_container:
        return 'promotional'
    elif has_product_container and not has_person:
        return 'product_display'
    elif has_person and not has_product_container:
        return 'lifestyle'
    else:
        return 'other'

def run_object_detection_pipeline(image_root_dir, output_csv_path):
    logging.info("Initializing YOLOv8 Nano model weights...")
    model = YOLO('yolov8n.pt')
    
    detection_records = []
    valid_extensions = ('.jpg', '.jpeg', '.png')
    
    logging.info(f"Scanning target directory structure: {image_root_dir}")
    
    # Walk through the nested data/raw/images/{channel_name}/ directories
    for root, _, files in os.walk(image_root_dir):
        for file in files:
            if file.lower().endswith(valid_extensions):
                image_path = os.path.join(root, file)
                
                # Structure: data/raw/images/{channel_name}/{message_id}.jpg
                path_parts = os.path.normpath(image_path).split(os.sep)
                channel_name = path_parts[-2] if len(path_parts) >= 2 else "unknown_channel"
                
                message_id_str = os.path.splitext(file)[0]
                try:
                    message_id = int(message_id_str)
                except ValueError:
                    logging.warning(f"Non-numeric filename encountered: {file}. Defaulting identifier map to 0.")
                    message_id = 0

                try:
                    results = model(image_path, verbose=False, conf=0.25)
                    
                    detected_labels = []
                    confidence_scores = []
                    
                    for r in results:
                        for box in r.boxes:
                            cls_id = int(box.cls[0])
                            label = model.names[cls_id]
                            conf = float(box.conf[0])
                            
                            detected_labels.append(label)
                            confidence_scores.append(round(conf, 4))
                    
                    image_category = determine_image_category(detected_labels)
                    labels_str = ",".join(detected_labels) if detected_labels else "none"
                    avg_conf = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

                    detection_records.append({
                        'message_id': message_id,
                        'channel_name': channel_name,
                        'image_path': image_path,
                        'detected_objects': labels_str,
                        'confidence_score': round(avg_conf, 4),
                        'image_category': image_category
                    })
                    logging.info(f"Processed image: {file} | Category: {image_category} | Objects: {labels_str}")
                    
                except Exception as inference_error:
                    logging.error(f"Failed to infer object telemetry matrices on {file}: {inference_error}")
                    continue

    # Save tracking records to output matrix
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    
    csv_headers = ['message_id', 'channel_name', 'image_path', 'detected_objects', 'confidence_score', 'image_category']
    with open(output_csv_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=csv_headers)
        writer.writeheader()
        writer.writerows(detection_records)
        
    logging.info(f"YOLO Processing Pipeline execution complete. Analytical CSV logs exported to: {output_csv_path}")

if __name__ == "__main__":
    IMAGE_INPUT_DIRECTORY = "data/raw/images"
    OUTPUT_LOGS_CSV = "data/cleaned/image_detections.csv"
    
    run_object_detection_pipeline(IMAGE_INPUT_DIRECTORY, OUTPUT_LOGS_CSV)