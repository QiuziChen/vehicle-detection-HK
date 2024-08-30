import os
import pandas as pd
import numpy as np
from tqdm import tqdm
from datetime import datetime, timedelta

import torch
import cv2
from ultralytics import YOLO

def check_same_image(image1, image2):
    try:
        difference = cv2.subtract(image1, image2)
        same = not np.any(difference)
        return same
    except:
        return False

def generate_date_range(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    date_list = []
    current_date = start
    while current_date <= end:
        date_list.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    return date_list

def process_images(model_path, input_folder, output_folder, target_date):
    
    # Load model
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = YOLO(model_path)

    # Define vehicle classes
    vehicle_classes = ["PC", "HGV", "HDB", "TX", "FBDD", "LGV", "LDB", "MC"]
    vehicle_dict = {
        k: v for k, v in enumerate(vehicle_classes)
    }

    # Initialize DataFrame
    df = pd.DataFrame(columns=['camera_id', 'timestamp'] + vehicle_classes)

    # Iterate through each camera folder
    with open('fail cam.txt', 'r') as file:
        invalid_folders = file.read().splitlines()

    for camera_id in tqdm([folder for folder in os.listdir(input_folder) if folder not in invalid_folders]):
        camera_folder = os.path.join(input_folder, camera_id)
        if os.path.isdir(camera_folder):
            # Get all image files
            images = [img for img in os.listdir(camera_folder) if img.endswith('.jpg')]
            # Filter images by target date
            images = [img for img in images if target_date in img]
            images_paths = [os.path.join(camera_folder, image) for image in images]

            # Get timestamps
            timestamps_strs = [image.split('_')[1].split('.')[0] for image in images]
            timestamps = [datetime.strptime(timestamp_str, '%Y-%m-%d-%H-%M-%S') for timestamp_str in timestamps_strs]

            # Perform detection directly on the image file path
            image_last = None
            invalid_image = cv2.imread('invalid_image.jpg')

            for timestamp, images_path in zip(timestamps, images_paths):
                try:
                    # Check if valid image
                    image_now = cv2.imread(images_path)
                    if not check_same_image(image_last, image_now) and not check_same_image(invalid_image, image_now):
                        # Predict
                        results = model.predict(images_path, device=device)
                        # Count the number of each vehicle type
                        r = results[0]
                        vehicle_count = {cls: 0 for cls in vehicle_classes}
                        objs = [vehicle_dict[int(t.item())] for t in r.boxes.cls]
                        for obj in objs:
                            vehicle_count[obj] += 1
                        # Add to df
                        df.loc[df.shape[0]] = [camera_id, timestamp] + list(vehicle_count.values())
                    # Update last image
                    image_last = image_now
                except:
                    pass

    # Define the output CSV file path
    os.makedirs(output_folder, exist_ok=True)
    output_csv = os.path.join(output_folder, f'detect_results_{target_date}.csv')
    # Output to CSV file
    df.to_csv(output_csv, index=False)

if __name__ == "__main__":
    model_path = input("Please enter the path to your model (e.g. best.pt): ")
    input_folder = input("Please enter the path to the image folder (e.g. ../../snapshot HK/img): ")
    output_folder = "./results"
    start_date = input("Please enter the start date (format: YYYY-mm-dd): ")
    end_date = input("Please enter the end date (format: YYYY-mm-dd): ")

    target_dates = generate_date_range(start_date, end_date)
    for target_date in target_dates: 
        print("Start extract data on %s." % target_date)
        process_images(model_path, input_folder, output_folder, target_date)
