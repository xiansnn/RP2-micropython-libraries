# Only For Pico W
from wifi_data import SSID, PASSWORD # place a wifi-data.py file in pico root directory with the right SSID and PASSWORD
import time, network, uasyncio

#------------------------------------------------------------------------------
# DEBUG logic analyser probe definitions
from debug_utility.pulses import *
# D0 = Probe(27) # wifi_connect 
# D1 = Probe(16) # wifi_connect>loop 
# D2 = Probe(17) # 
# D3 = Probe(18) # 
# D4 = Probe(19) # 
# D5 = Probe(20) # async_wifi_connect
# D6 = Probe(21) # async get_connection_status
# D7 = Probe(26) # 

 
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

def wifi_connect():
    D0.on()
    wlan.disconnect()
    wlan.connect(SSID, PASSWORD)
    # Wait for connect or fail
    max_wait = 10
    while max_wait > 0:
        D1.on()
        if wlan.status() < 0 or wlan.status() >= 3:
            D1.off()
            break
        max_wait -= 1
        print(f"[{max_wait:02d}]waiting for connection...")
        D1.off()
        time.sleep(1)

    # Handle connection error
    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('connected')
        wlan_config = wlan.ifconfig()
        print( f"my_ip =  {wlan_config[0]}" )
    D0.off()
    return wlan.isconnected()


async def get_connection_status():
    D6.on()
    status = wlan.status()
    D6.off()    
    await uasyncio.sleep(1)
    return status

def explain_wlan_status(status):
    if status == network.STAT_GOT_IP:
        result = (f"STAT_GOT_IP")
    elif status == network.STAT_CONNECTING:
        result = (f"STAT_CONNECTING")
    elif status == network.STAT_IDLE:
        result = (f"STAT_IDLE")
    elif status == network.STAT_CONNECT_FAIL:
        result = (f"STAT_CONNECT_FAIL")
    elif status == network.STAT_NO_AP_FOUND:
        result = (f"STAT_NO_AP_FOUND")
    elif status == network.STAT_WRONG_PASSWORD:
        result = (f"STAT_WRONG_PASSWORD")
    if __name__ == "__main__" : print(f"explanation: {result}")
    return result
    
def async_wifi_connect():
    D5.on()
    wlan.disconnect()
    wlan.connect(SSID, PASSWORD)
    if __name__ == "__main__":
        for n in range(10):
            status = uasyncio.run(get_connection_status())
            explain_wlan_status(status)
            if status ==network.STAT_GOT_IP:
                break
    D5.off()
    return wlan.isconnected()


if __name__ == "__main__":

    s = async_wifi_connect()
#     s = wifi_connect()
    print(f"wifi connected: {s}")
    
    

