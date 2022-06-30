import asyncio
from threading import Thread
import time
from bleak import discover

def check_key(_dict, key):
    if key in _dict.keys():
        return _dict[key]
    else:
        return False

class BLEScanner:
    def __init__(self):
        self.ble_devices = {}
        self.run = True
        self.ready = False
        self.loop = asyncio.get_event_loop()
        self.ble_scanner_t = Thread(target=self.ble_scanner)
        self.ble_scanner_t.start()
        while not self.ready:
            time.sleep(0.1)
    async def find_device(self):
        devices = await discover()
        #print('the devices are ', devices)
        for d in devices:
            # print('the device id', d)
            if not check_key(self.ble_devices, d.name):
                self.ble_devices[d.name] = d.address
                #print("New BLE device found: " + str(d.name))

    def ble_scanner(self):
        while self.run:
            self.loop.run_until_complete(self.find_device())
            self.ready = True
            time.sleep(0.1)

    def close(self):
        self.run = False
        time.sleep(1)

    def get_address(self, device_name):
        #print('device_name',device_name)
        return check_key(self.ble_devices, device_name)
