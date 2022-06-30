from threading import Thread
from datetime import datetime
import os
import time

def byte_swap(h):
    if type(h) == str:
        h = int(h,16)
    return ((h<<8) | (h>>8)) & 0xFFFF


def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val

class DataToFile:

    column_names = ["ts_receiver", "ts_sensor", "acc_x", "acc_y", "acc_z", "gyr_x", "gyr_y", "gyr_z", "mag_x", "mag_y", "mag_z"]

    def __init__(self, data_q, _sbj, sensor_label, package_directory):
        self.q = data_q
        self.sbj = _sbj
        self.label = sensor_label
        self.data_file = None
        self.data_file_name = ''
        self.data_file_path = package_directory
        self.column_names = self.column_names
        # self.path = write_path
        self.data_thread_stop = 0
        self.start_time = ''

        self.data_thread = Thread(target=self.data_getter)
        # self.start_data_thread()

    def start_data_thread(self):
        self.data_thread_stop = 0
        self.data_file_path = os.path.join(self.data_file_path, "IMU_data")
        if not os.path.isdir(self.data_file_path):
            os.mkdir(self.data_file_path)

        tmp = datetime.now()
        self.start_time = tmp.strftime("%Y%m%d_%H%M%S")
        self.data_file_name = self.sbj + '_' + self.start_time + '_' + self.label + '.csv'
        self.data_file_path = os.path.join(self.data_file_path, self.data_file_name)

        self.data_file = open(self.data_file_path, "w+")
        self.data_file.write(",".join(self.column_names))
        self.data_file.write("\n")

        self.data_thread.start()

    def stop_data_thread(self):
        self.data_thread_stop = 1
        time.sleep(0.2)

        if self.data_file:
            self.data_file.close()

    def data_getter(self):

        while True:
            stream, timestamp, data = self.q.get()

            if stream == 'exit':
                break

            if int(stream) == 16:

                data_list = []

                data_list.append(str(byte_swap(data[0:4])))

                for i in range(4, len(data), 4):
                    data_list.append(str(twos_comp(byte_swap(data[i:i+4]), 16)))


            data_str = [timestamp] + data_list
            data_str = ",".join(data_str)

            self.data_file.write(data_str)
            self.data_file.write("\n")

            time.sleep(0.001)


