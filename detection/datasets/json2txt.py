import os
import json
import shutil
from tqdm import tqdm

def convert_labelme_to_yolo(json_folder, img_folder, output_base_folder, subfolder_name):
    # Create output subfolders
    output_txt_folder = os.path.join(output_base_folder, 'labels', subfolder_name)
    output_img_folder = os.path.join(output_base_folder, 'images', subfolder_name)
    os.makedirs(output_txt_folder, exist_ok=True)
    os.makedirs(output_img_folder, exist_ok=True)

    labels = ["PC", "HGV", "HDB", "TX", "FBDD", "LGV", "LDB", "MC"]
    label_dict={
        k: v for v, k in enumerate(labels)
    }

    # Iterate over all JSON files in the input folder
    for json_file in tqdm(os.listdir(json_folder)):
        if json_file.endswith('.json'):
            json_path = os.path.join(json_folder, json_file)
            
            # Read JSON file
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if there are any objects in the image
            if 'shapes' not in data or len(data['shapes']) == 0:
                continue
            
            # Get image dimensions
            img_height = data['imageHeight']
            img_width = data['imageWidth']
            
            # Prepare YOLO format annotations
            yolo_annotations = []
            for shape in data['shapes']:
                label = shape['label']
                points = shape['points']
                x_min = min(points[0][0], points[1][0])
                x_max = max(points[0][0], points[1][0])
                y_min = min(points[0][1], points[1][1])
                y_max = max(points[0][1], points[1][1])
                
                # Calculate YOLO format values
                x_center = (x_min + x_max) / 2 / img_width
                y_center = (y_min + y_max) / 2 / img_height
                width = (x_max - x_min) / img_width
                height = (y_max - y_min) / img_height
                
                # Append annotation to the list
                yolo_annotations.append(f"{label_dict[label]} {x_center} {y_center} {width} {height}")
            
            # Write YOLO annotations to a txt file
            txt_file_name = os.path.splitext(json_file)[0] + '.txt'
            txt_file_path = os.path.join(output_txt_folder, txt_file_name)
            with open(txt_file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(yolo_annotations))
            
            # Copy corresponding image file to the output image folder
            img_file_name = os.path.splitext(json_file)[0] + '.jpg'
            img_src_path = os.path.join(img_folder, img_file_name)
            img_dst_path = os.path.join(output_img_folder, img_file_name)
            shutil.copyfile(img_src_path, img_dst_path)

if __name__ == '__main__':
    json_folder = input("Enter the path to the JSON folder (e.g., './raw/train/labels'): ")
    img_folder = input("Enter the path to the image folder (e.g., './raw/train/images'): ")
    output_base_folder = input("Enter the path to the base output folder (e.g., './data): ")
    subfolder_name = input("Enter the name of the subfolder ('train', 'val', or 'test'): ")
    convert_labelme_to_yolo(json_folder, img_folder, output_base_folder, subfolder_name)
