# Only For Pico W
from wifi_data import SSID, PASSWORD # place a wifi-data.py file in pico root directory with the right SSID and PASSWORD
import time, network
 
 
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

def wifi_connect():
    wlan.disconnect()
    wlan.connect(SSID, PASSWORD)
    # Wait for connect or fail
    max_wait = 60
    while max_wait > 0:
#         print (wlan.isconnected())
#         print (wlan.status())
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print(f"[{max_wait:02d}]waiting for connection...")
        time.sleep(1)

    # Handle connection error
    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('connected')
        status = wlan.ifconfig()
        print( f"my_ip =  {status[0]}" )
    return wlan.isconnected()

if __name__ == "__main__":
    wifi_connect()

