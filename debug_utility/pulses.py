from machine import Pin, Signal
import utime


class Probe():
    """
A Class that provides means for events observation on oscilloscope.
Usefull for debugging.
"""
    def __init__(self,probe_gpio):
        self.probe = Signal(probe_gpio,Pin.OUT, invert=False)

    def pulses(self, n):
        for i in range (n):        
            self.probe.on()
            self.probe.off()

    def pulse_single(self,n=1, width_us=10):        
        self.probe.on()
        utime.sleep_us(n*width_us)
        self.probe.off()
    
    def pulse_begin(self, id):
        self.probe.on()
        utime.sleep_ms(id)
        self.probe.off()
        
    def pulse_end(self, id):
        for i in range(id):
            self.probe.on()
            utime.sleep_us(500)
            self.probe.off()
            utime.sleep_us(500)





def test():
    probe_gpio = 16
    p = Probe(probe_gpio)
    
    while (True):

        for n in range (10):
            p.pulses(n)

        utime.sleep(1)

        for n in range (1,10):
            p.pulse_single(n)

        utime.sleep(1)
        
        p.pulse_begin(3)
        utime.sleep_us(500)
        p.pulse_end(3)

        utime.sleep(2)

         
      
      



    



if __name__ == "__main__":
    test()
