# Only For Pico W
from wifi_data import SSID, PASSWORD # place a wifi-data.py file in pico root directory with the right SSID and PASSWORD
import time, network, uasyncio

#------------------------------------------------------------------------------
# DEBUG logic analyser probe definitions
from debug_utility.pulses import *
# D0 = Probe(27) # 
# D1 = Probe(16) # 
# D2 = Probe(17) # 
# D3 = Probe(18) # 
# D4 = Probe(19) # 
# D5 = Probe(20) # 
# D6 = Probe(21) # 
# D7 = Probe(26) # 

RETRY_GET_WLAN_CONNECT_STATUS = const(1) # in seconds
MAX_GET_STATUS_RETRY = const(10)

class WiFiDevice():
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.ifconfig = None
        self.status = network.STAT_IDLE

    def get_status(self):
        self.status = self.wlan.status()
        return self.status
    
    def set_status(self, status):
        self.status = status
    
    def get_ifconfig(self):
        self.ifconfig = self.wlan.ifconfig()
        return self.ifconfig
        
    def wifi_connect(self):
        self.wlan.disconnect()
        self.wlan.connect(SSID, PASSWORD)
        
    def explain_wlan_status(self, status):
        result = ""
        if status == network.STAT_GOT_IP:           # 3
            result = (f"STAT_GOT_IP") 
        elif status == network.STAT_CONNECTING:     # 1
            result = (f"STAT_CONNECTING")
        elif status == network.STAT_IDLE:           # 0
            result = (f"STAT_IDLE")
        elif status == network.STAT_CONNECT_FAIL:   #-1
            result = (f"STAT_CONNECT_FAIL")
        elif status == network.STAT_NO_AP_FOUND:    #-2
            result = (f"STAT_NO_AP_FOUND")
        elif status == network.STAT_WRONG_PASSWORD: #-3
            result = (f"STAT_WRONG_PASSWORD")
        return result

                
    def blocking_wait_connection(self):
        # Wait for connect or fail
        D2.on()
        max_wait = MAX_GET_STATUS_RETRY
        while max_wait > 0:
            D2.on()
            status = self.get_status()
            if status == network.STAT_GOT_IP :
                D2.off()
                return True
            elif status == network.STAT_CONNECTING:
                print(f"internal status[{status}] #[{max_wait:02d}]waiting for connection...")
                max_wait -= 1
                D2.off()
                time.sleep(RETRY_GET_WLAN_CONNECT_STATUS)
            else :
                print(f"internal status[{status}]")
                D2.off()
                return False
        self.status = network.STAT_CONNECT_FAIL
        D2.off()
        return False


    async def async_wait_connection(self):

        # Wait for connect or fail
        max_wait = MAX_GET_STATUS_RETRY
        while max_wait > 0:
            D2.on()
            status = self.get_status()
            if status == network.STAT_GOT_IP :
                D2.off()
                return True
            elif status == network.STAT_CONNECTING:
                print(f"status[{status}] #[{max_wait:02d}]waiting for connection...")
                max_wait -= 1
                D2.off()
                await uasyncio.sleep(RETRY_GET_WLAN_CONNECT_STATUS)
            else :
                D2.off()
                return False
        self.status = network.STAT_CONNECT_FAIL
        return False

    async def async_wait_status(self):
        # Wait for connect or fail)
        await uasyncio.sleep(RETRY_GET_WLAN_CONNECT_STATUS)
    

        

###############################################################################
if __name__ == "__main__":
    
    async def bgtask(qty, probe):
        """" this is a background task, just to show blocking and non-blocking wifi connection """
        for n in range(qty):
            probe.on()
            time.sleep_ms(50)
            probe.off()
            await uasyncio.sleep_ms(50)

    
    async def main_prog():
        #cleaning probes states
        D2.off()
        D3.off()
        D4.off()
        D5.off()
        
        D0.on()
        wifi_device = WiFiDevice()
        D0.off()

#-------------------        
        
        await uasyncio.sleep(1) # first pause to let tasks start executing
 
#-------------------        
        print("\tblocking connection")
        D1.on()
        wifi_device.wifi_connect()
        D1.off()
        
        D5.on()
        wifi_device.blocking_wait_connection()
        print(f"final sync wifi status: {wifi_device.explain_wlan_status(wifi_device.status)}\n")
        D5.off()
        
#-------------------        
        
        await uasyncio.sleep(3) # second pause to let tasks start executing

#-------------------        
        print("\t non blocking async connection with acces to wlan status")
        D1.on()
        wifi_device.wifi_connect()
        D1.off()
        
        D3.on()
        max_wait = MAX_GET_STATUS_RETRY
        while max_wait > 0:
            D2.on()
            status = wifi_device.get_status()
            if status == network.STAT_CONNECTING:
                print(f"exposed status[{status}] #[{max_wait:02d}]waiting for connection...")
                max_wait -= 1
                D2.off()
                await uasyncio.sleep(RETRY_GET_WLAN_CONNECT_STATUS)
            else:
                print(f"exposed status[{status}]")
                D2.off()
                break
            D2.off()
        if max_wait == 0:
            wifi_device.set_status(network.STAT_CONNECT_FAIL)
        print(f"final sync wifi status: {wifi_device.explain_wlan_status(wifi_device.status)}\n")
        D3.off()
#-------------------        
        D0.on()
        print("end")
        D0.off()

#-------------------        
        
    scheduler = uasyncio.get_event_loop()
    scheduler.create_task(main_prog())
    scheduler.create_task(bgtask(150,D6))
    scheduler.create_task(bgtask(50,D7))

    scheduler.run_forever()

        

    


