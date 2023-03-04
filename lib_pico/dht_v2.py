import array
import micropython
import utime
from machine import Pin
import machine
from micropython import const
import uasyncio as asyncio

# DEBUG logic analyser probe definitions
from debug_utility.pulses import *
from DCF77.decoder_uGUIv1 import * #required to determine status of the clock
  
HIGH_LEVEL_DURATION = const(50)
# data sheet :
# HIGH_LEVEL_DURATION set to 50us, gives the middle value between "0" and "1"
## 26us...28us us = "0"  equals HIGH_LEVEL_DURATION*(1-50%) 
## 70 us          = "1"  equals HIGH_LEVEL_DURATION*(1+50%)  
EXPECTED_PULSES = const(42)
# data sheet : 1 start-bit + 40 bit-pulses + 1 stop-bit
 
class DHT11device:
    def __init__(self, gpio_device_interface, period, clock=None):
        pin = Pin(gpio_device_interface, Pin.OPEN_DRAIN, Pin.PULL_UP, value=1)
        self._pin = pin
        self._clock = clock
        self._hour = 0
        self._minute = 0
        self._temperature = -1.0 # not yet measured
        self._humidity = -1.0 # no yet measured
        self.measure_period = period # expressed in seconds
    
    def get_humidity(self):
        return self._humidity
 
    def get_temperature(self):
        return self._temperature
 
    async def async_measure(self):
        while True:
            
            self._send_init_signal()
            pulses = self._capture_pulses()
            buffer = self._convert_pulses_to_buffer(pulses)
            if self._is_checksum_correct(buffer):
                self._humidity = buffer[0] + buffer[1] / 10
                self._temperature = buffer[2] + buffer[3] / 10
            if self._clock is not None :
                t = self._clock.get_local_time()
                if t[8]: # if time is valid
                    self._hour = t[3]
                    self._minute = t[4]
                    print(f"{self._temperature:3.1f}°C\t{self._humidity:3.1f}%\t {self._hour:02d}:{self._minute:02d}")
            if __name__ == "__main__" : print(f"{self._temperature:3.1f}°C\t{self._humidity:3.1f}%")
            await asyncio.sleep(self.measure_period)
            
    def _send_init_signal(self):
        self._pin.init(Pin.OPEN_DRAIN, Pin.PULL_UP, value=0)
        utime.sleep_ms(20) # data sheet : assert shared wire to low at least 18ms
        self._pin.init(Pin.OPEN_DRAIN, Pin.PULL_UP, value=1) # release the shared wire

    @micropython.native
    def _capture_pulses(self):
        HIGH_LEVEL = const(1)
        TIME_OUT = const(100) # in us
        
        idx = 0
        pulses = bytearray(EXPECTED_PULSES)
        result = 0
        while result >= 0: # result is negative when time_pulse_us times out (here 100
            result = machine.time_pulse_us(self._pin, HIGH_LEVEL, TIME_OUT)
            pulses[idx] = result
            idx += 1
        return pulses
        
    @micropython.native
    def _convert_pulses_to_buffer(self, pulses):
        """Convert a list of 40 pulses into a 5 byte buffer
        The resulting 5 bytes in the buffer will be:
            0: Integral relative humidity data
            1: Decimal relative humidity data
            2: Integral temperature data
            3: Decimal temperature data
            4: Checksum
        """      
        # Convert the 40 pulses to 40 bits
        binary = 0
        for idx in range(1, len(pulses)-1): # excluding start and stop bits pulses
            binary = binary << 1 | int(pulses[idx] > HIGH_LEVEL_DURATION)
        # Split into 5 bytes
        buffer = array.array("B") # 'B' means unsigned char (i.e 8 bit word)
        for shift in range(4, -1, -1): # shift takes values  4, 3, 2, 1, 0
            buffer.append((binary >> (shift * 8)) & 0xFF)        
        return buffer
 
    def _is_checksum_correct(self, buffer):
        # Calculate checksum
        checksum = 0
        for buf in buffer[0:4]:
            checksum += buf
        if checksum & 0xFF != buffer[4]:
            print("frame / chksum error")
            return False
        else: return True
        
###############################################################################        
if __name__ == '__main__':
    print("test async DHT11")
    DHT_PIN_IN = const(9)
    PERIOD = const(1) # in seconds
    sensor = DHT11device(DHT_PIN_IN, PERIOD)

    scheduler = asyncio.get_event_loop()
    asyncio.create_task(sensor.async_measure())        
    scheduler.run_forever()
        
