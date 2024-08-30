import pandas as pd
import xmltodict
import requests
import time
from tqdm import tqdm
import logging


def time_str(fmt="%Y-%m-%d %H:%M:%S"):
    """
    Generate string of the current time stamp.
    """
    return time.strftime(fmt, time.localtime())


def load_save(url, key, save_path):
    """
    Load and save snapshot images.
    url: image url
    key: image id
    save_path: save dir path
    """
    # request
    load_time = time_str("%Y-%m-%d-%H-%M-%S")
    res = requests.get(url)

    # save
    save_name = save_path + key + "_" + load_time + ".jpg"
    with open(save_name, "wb") as f:
        f.write(res.content)


# ========== main ==========


# load locations info
locations_path = "Traffic_Camera_Locations_En.xml"
locations = pd.read_xml(locations_path)

# with open(locations_path, 'rb') as f:
#     locations = xmltodict.parse(f)
# locations = pd.DataFrame(locations['image-list']['image'])

keys = locations['key'].values
urls = locations['url'].values

# log
init_time = time_str("%Y-%m-%d")
log_filename = "./log/log_%s.txt" % init_time
DATE_FORMAT = "%Y/%m/%d %H:%M:%S"
logging.basicConfig(filename=log_filename, level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s", datefmt=DATE_FORMAT)

# frequency
freq = 100  # sec

# extract
while True:

    tic = time.time()

    exe_time = time_str()
    print("==========================")
    print("Execution [%s]" % exe_time)

    err_n = 0  # error num

    for key, url in tqdm(zip(keys, urls)):

        try:
            save_path = "./img/%s/" % key
            load_save(url, key, save_path)
        except:
            err_n += 1
            logging.error(key)
    
    print("Error num: %d" % err_n)

    toc = time.time()
    
    # sleep
    sleep_time = freq - (toc - tic)
    if sleep_time > 0:
        time.sleep(sleep_time)