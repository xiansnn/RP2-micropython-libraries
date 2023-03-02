import array
import micropython
import utime
from machine import Pin
from micropython import const
import uasyncio as asyncio

# DEBUG logic analyser probe definitions
from debug_utility.pulses import *
  
MAX_UNCHANGED = const(90) # the number of times the pin value hasn't changed, meaning : no more transitions
MIN_INTERVAL_US = const(200000)
HIGH_LEVEL = const(50)
# data sheet :
## 26us...28us us = "0"  then triggger is 50us*(1-50%) 
## 70 us = "1" then triggger is then triggger is 50us*(1+50%)  
EXPECTED_TRANSITIONS = const(84)
# data sheet : 1 start-bit pulse + 1 ACK + 40 bit-pulses + 1 stop-bit -> 84 transitions
 
class DHT11device:
    _temperature: float
    _humidity: float
 
    def __init__(self, gpio_device_interface, period):
#         pin = Pin(gpio_device_interface, Pin.OUT, Pin.PULL_UP, value=1)
        pin = Pin(gpio_device_interface, Pin.OPEN_DRAIN, Pin.PULL_UP, value=1)
        self._pin = pin
        self._last_measure = utime.ticks_us()
        self._temperature = -1 # not yet measured
        self._humidity = -1 # no yet measured
        self.measure_period = period # expressed in seconds
    
    def get_humidity(self):
        return self._humidity
 
    def get_temperature(self):
        return self._temperature
 
    def measure(self):
        current_ticks = utime.ticks_us()
        # check if measure period is large enough
        if utime.ticks_diff(current_ticks, self._last_measure) < MIN_INTERVAL_US \
                               and(self._temperature > -1 or self._humidity > -1):
            return
        self._send_init_signal()
        pulses = self._capture_pulses()
        buffer = self._convert_pulses_to_buffer(pulses)
        if self._is_checksum_correct(buffer): # if chksum OK then measures are updated
            self._humidity = buffer[0] + buffer[1] / 10
            self._temperature = buffer[2] + buffer[3] / 10
        self._last_measure = utime.ticks_us()
    
    async def async_measure(self):
        while True:
            self._send_init_signal()
            pulses = self._capture_pulses()
            if pulses is not None:
                buffer = self._convert_pulses_to_buffer(pulses)
                if self._is_checksum_correct(buffer):
                    self._humidity = buffer[0] + buffer[1] / 10
                    self._temperature = buffer[2] + buffer[3] / 10
            print(f"Temperature: {self._temperature:3.0f}°C\tHumidity:    {self._humidity:3.0f}%")
            await asyncio.sleep(self.measure_period)
            
    def _send_init_signal(self):
        self._pin.init(Pin.OPEN_DRAIN, Pin.PULL_UP, value=0)
        utime.sleep_ms(20) # data sheet : at least 18ms

    @micropython.native
    def _capture_pulses(self):
        pin = self._pin
        pin.init(Pin.OPEN_DRAIN, Pin.PULL_UP)
        val = 1
        idx = 0
        transitions = bytearray(EXPECTED_TRANSITIONS)
        unchanged = 0
        timestamp = utime.ticks_us()
 
        while unchanged < MAX_UNCHANGED:
            if val != pin.value():
                if idx >= EXPECTED_TRANSITIONS:
                    print(f"Got more than {EXPECTED_TRANSITIONS} pulses")
                    break
                now = utime.ticks_us()
                transitions[idx] = now - timestamp
                timestamp = now
                idx += 1
 
                val = 1 - val
                unchanged = 0
            else:
                unchanged += 1
        pin.init(Pin.OPEN_DRAIN, Pin.PULL_UP, value=1)
        if idx != EXPECTED_TRANSITIONS:
            print(f"Expected {EXPECTED_TRANSITIONS} but got {idx} pulses" )
            return None
        else:
            return transitions[4:]
 
    def _convert_pulses_to_buffer(self, pulses):
        """Convert a list of 80 pulses into a 5 byte buffer
        The resulting 5 bytes in the buffer will be:
            0: Integral relative humidity data
            1: Decimal relative humidity data
            2: Integral temperature data
            3: Decimal temperature data
            4: Checksum
        """
        # Convert the pulses to 40 bits
        binary = 0
        for idx in range(0, len(pulses), 2):
            binary = binary << 1 | int(pulses[idx] > HIGH_LEVEL)
 
        # Split into 5 bytes
        buffer = array.array("B")
        for shift in range(4, -1, -1):
            buffer.append(binary >> shift * 8 & 0xFF)
        return buffer
 
    def _is_checksum_correct(self, buffer):
        # Calculate checksum
        checksum = 0
        for buf in buffer[0:4]:
            checksum += buf
        if checksum & 0xFF != buffer[4]:
            print("chksum error")
            return False
        else: return True
        
###############################################################################        
if __name__ == '__main__':
    DHT_PIN_IN = const(9)
    PERIOD = const(1)
    sensor = DHT11device(DHT_PIN_IN, PERIOD)
    
    def test_sync(): 
        while True:
            sensor.measure()
            t  = sensor.get_temperature()
            h = sensor.get_humidity()
            print(f"Temperature: {t:3.0f}°C")
            print(f"Humidity:    {h:3.0f}%")
            utime.sleep(10)
    
    def test_async():
        print("test_async")
    #start coroutines
        scheduler = asyncio.get_event_loop()
        dht11 = asyncio.create_task(sensor.async_measure())        
        scheduler.run_forever()


        
    test_async()
#     test_sync()
        

        
