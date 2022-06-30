#--------------------------------------REVISIONS---------------------------------------
# Date        Name        Ver#    Description
#--------------------------------------------------------------------------------------
#**************************************************************************************

# Find STEVAL-BCN002V1

from BLEScanner import BLEScanner
from DataToFile import DataToFile
from Connection import Connection
import asyncio
from aioconsole import ainput
from queue import Queue
import time
import os

package_directory = os.path.dirname(os.path.abspath(__file__))

async def user_console_manager(connection_list: list):
    print(connection_list)

    while not (connection_list.client and connection_list.connected):
        print('conn client and list',connection_list.client, connection_list.connected)
        await asyncio.sleep(0.1, loop=loop)

    await asyncio.sleep(0.1, loop=loop)

    print("Supporting commands:")
    print("\t1 (Start logging)\n\t0 (Stop logging)")

    while True:
        command = await ainput("New Command: ")
        command = int(command)
        global run_data_logging

        if command == 1:
            connection_list.run_data_logging = True 
            data_to_file_dd = DataToFile(dq_dd, sbj, 'dd', package_directory=package_directory) #dd connection
            data_to_file_dd.start_data_thread() #dd connection

        elif command == 0:
            connection_list.run_data_logging = False
            dq_dd.put(('exit', '', ''))
            data_to_file_dd.stop_data_thread()

        await asyncio.sleep(0.5, loop=loop)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    d_name = "BCN-002"
    n_name = "SMTRN-N"

    ble = BLEScanner()

    timeout = 10
    while not ble.get_address(d_name):#or not ble.get_address(n_name):
        time.sleep(0.1)
        timeout = timeout - 0.1
        if timeout < 0:
            exit(0)

    ble.close()
    address_list = ['A510B90B-13F9-97E3-DAB8-288B132022D2']
    dd_address = address_list[0]
    print('the address of dd_device',dd_address)

    dq_dd = Queue() #dd third connection
    sbj = 's01'

    print('step1 TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT the connection finished')
    connection_dd = Connection(loop, device_address=dd_address, data_q=dq_dd) #dd connection

    try:
        asyncio.ensure_future(connection_dd.manager())
        print('step4 TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT   the connection finished')
        asyncio.ensure_future(user_console_manager( connection_dd ))
        print('step5 *****************************************   the connection finished')
        loop.run_forever()

    except KeyboardInterrupt:
        print()
        print("User stopped program.")

    finally:
        print("Disconnecting...")
        loop.run_until_complete(connection_dd.cleanup())
