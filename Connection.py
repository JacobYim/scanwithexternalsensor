from xmlrpc.client import Boolean
from bleak import BleakClient
from queue import Queue
from datetime import datetime
import asyncio
import time

class Connection:

    client: BleakClient = None

    acc_gyro_mag_char = "00e00000-0001-11e1-ac36-0002a5d5c51b"
    quaternion_char   = "00000100-0001-11e1-ac36-0002a5d5c51b"

    def __init__(self,
                 loop: asyncio.AbstractEventLoop,
                 device_address: str = None,
                 device_name: str = None,
                 data_q: Queue =None,
                 run_data_logging: Boolean = False):

        self.loop             = loop
        self.connected_device = device_address
        #self.device_name     = device_name
        self.data_q           = data_q

        self.connected = False
        
        self.last_packet_time = datetime.now()
        self.rx_data          = []
        self.rx_timestamps    = []
        self.rx_delays        = []

        self.run_data_logging = run_data_logging

        #**jyc**# async def find_device(self):
        #**jyc**#     devices = await discover()
        #**jyc**#     print('the waiting names of this device',devices)
        #**jyc**#     for d in devices:
        #**jyc**#         if self.device_name == d.name:
        #**jyc**#             self.connected_device = d.address
        #**jyc**#             return 
        #**jyc**#     if not self.connected_device:
        #**jyc**#         #print("Device: {} not found.".format(self.device_name))
        #**jyc**#         raise Exception

    def on_disconnect(self):
        self.connected = False
        #print("Disconnected!" + str(self.connected))

    def notification_handler(self, sender: str, data: any):
        self.rx_data.append(int.from_bytes(data, byteorder="big"))

    async def manager(self):
        print("Starting connection manager.")
        while True:
            if self.client:
                await self.connect()
            else:
                self.client = BleakClient(self.connected_device, loop=self.loop)
                await asyncio.sleep(1.0, loop=self.loop)

    async def connect(self):
        if self.connected:
            return
        try:
            self.client.set_disconnected_callback(self.on_disconnect())
            await self.client.connect()
            self.connected = await self.client.is_connected()
            if self.connected:
                #print("{} connected!".format(self.device_name))
                await self.client.start_notify(self.acc_gyro_mag_char, self.data_callback)
                #await self.client.start_notify(self.quaternion_char, self.data_callback)

                while True:
                    if not self.connected:
                        break
                    await asyncio.sleep(5.0, loop=self.loop)

            else:
                print("Failed to connect.")

        except Exception as e:
            print(e)

    async def cleanup(self):
        if self.client:
            await self.client.stop_notify(self.acc_gyro_mag_char)
            #await self.client.stop_notify(self.quaternion_char)
            await self.client.disconnect()

    def data_callback(self, sender: int, data: bytearray, run_data_logging = False):
        if self.data_q:
            data = bytes(data).hex()
            if self.run_data_logging:
                self.data_q.put((sender, str(time.time()), data))

    # def update_run_data_logging_status(self) :
    #         self.run_data_logging = not self.run_data_logging
