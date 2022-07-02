import csv
import os
import argparse

CURRENT_DIR = os.getcwd()

if __name__ == "__main__" :

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--android', default="jjj_1656618176645_yes.csv", help='log filename form andriod')
    parser.add_argument('--sensor', default="s01_20220630_154018_dd.csv", help='log filename form sensor')
    parser.add_argument('--interval', default=0.5, help='log filename form interval cutting the signals')
    args = parser.parse_args()

    ANDRIOD_TYPING_FILE = args.android
    SENSOR_DATA_FILE = args.sensor
    TIME_INTERVAL = args.interval

    with open(ANDRIOD_TYPING_FILE, "r") as f :
        android_data = f.readlines()
        android_data = list(map(lambda row : row.replace('\n', '').replace("{", ",").replace("}", ",").replace("=", ",").split(','), android_data))
        android_data = list(map(lambda row : [float(row[0])/1000, row[1], row[6]], android_data))

    with open(SENSOR_DATA_FILE, "r") as f :
        sensor_data = f.readlines()
        sensor_data = sensor_data[1:]
        sensor_data = list(map(lambda row : row.replace('\n', '').split(','), sensor_data))

    if not os.path.exists('data') :
        os.makedirs('data')

    for row in android_data :
        time, usr, key = row
        if not os.path.exists('data/{}/{}'.format(key, usr)) :
            os.makedirs('data/{}/{}'.format(key, usr))
        data = list(filter(lambda x: float(time-TIME_INTERVAL) < float(x[0]) < float(time+TIME_INTERVAL), sensor_data))
        print(data)    
        with open("data/{}/{}/{}_{}_{}.csv".format(key, usr, usr, key, time), "w+") as f :
            writer=csv.writer(f)
            writer.writerows(data)
