import os
import pandas as pd
from tqdm import tqdm
import xmltodict

# construct new folder 'img'
new_folder = "img"

if os.path.exists(new_folder):
    pass
else:
    os.makedirs(new_folder)

# construct new folder 'log'
new_folder = "log"
if os.path.exists(new_folder):
    pass
else:
    os.makedirs(new_folder)

# construct new folder for each location
locations_path = "Traffic_Camera_Locations_En.xml"
locations = pd.read_xml(locations_path)
# with open(locations_path, 'rb') as f:
#     locations = xmltodict.parse(f)
# locations = pd.DataFrame(locations['image-list']['image'])

os.chdir("img")
for key in tqdm(locations['key'].values, desc="Construct folders: "):
    
    if os.path.exists(key):
        pass
    else:
        os.makedirs(key)
