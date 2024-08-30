import os
import requests
import xmltodict
import pandas as pd
import time
from tqdm import tqdm


def time_str(fmt="%Y-%m-%d %H:%M:%S"):
    """
    Generate string of the current time stamp.
    """
    return time.strftime(fmt, time.localtime())

# data to dict
def get_dict(url):
    res = requests.get(url)
    data = xmltodict.parse(res.content)
    return data

# dict to dataframe
def get_df(data):
    """
    Transform xml dict to dataframe
    """
    df_dict = {
        'period_from': [],
        'period_to': [],
        'detector_id': [],
        'valid': [],
        'direction': [],
        'MOTOR CYCLE': [],
        'PRIVATE CAR': [],
        'TAXI': [],
        'PRIVATE LIGHT BUS': [],
        'PUBLIC LIGHT BUS': [],
        'LIGHT GOODS VEHICLE': [],
        'MEDIUM/HEAVY GOODS VEHICLE': [],
        'NON-FRANCHISED BUS': [],
        'FRANCHAISED BUS (S.D.)': [],
        'FRANCHIASED BUS (D.D.)': [],
        'COMMERCIAL VEHICLE': [],
    }
    # date
    date  =data['traffic_volume_list']['date']
    # iter periods
    periods = data['traffic_volume_list']['periods']['period']
    for period in tqdm(periods):
        t_from = period['period_from']
        t_to = period['period_to']

        # iter detectors
        detectors = period['detectors']['detector']
        for detector in detectors:
            df_dict['period_from'].append(t_from)
            df_dict['period_to'].append(t_to)
            df_dict['detector_id'].append(detector['detector_id'])
            df_dict['valid'].append(detector['valid'])
            try:
                df_dict['direction'].append(detector['direction'])
            except:
                df_dict['direction'].append('')
                
            # iter vehicle classes
            vehicles = detector['vehicle_class']['class']
            for veh in vehicles:
                df_dict[veh['class_name']].append(veh['proportion'])

    return pd.DataFrame(df_dict), date

# match detector info
def match_info(df, info):
    """
    Match location information to each detector.
    """
    return df.set_index('detector_id').join(info[['Device_ID', 'District', 'Road_EN', 'Latitude', 'Longitude', 'Direction', 'Rotation']].set_index('Device_ID')).reset_index()


# ========== main ==========


url = 'https://resource.data.one.gov.hk/td/traffic-detectors/volByVClass-all.xml'
info = pd.read_csv('traffic_prop_vehicle_class_info.csv')
save_path = './prop'

# extract
while True:

    exe_time = time_str()
    print("==========================")
    print("Execution [%s]" % exe_time)

    try:
        # load data
        data = get_dict(url)
        df, date = get_df(data)
        df = match_info(df, info)
        df.to_csv(os.path.join(save_path, "prop_%s.csv" % date))
        print("Save successfully!")
    except:
        print("Something went wrong...")
    # sleep
    time.sleep(24*3600)  # daily