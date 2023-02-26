from machine import Pin, Signal
import utime



class Probe():
    """
A Class that provides means for events observation on oscilloscope.
Usefull for debugging.
"""
    def __init__(self,probe_gpio):
        self.probe = Signal(probe_gpio,Pin.OUT, invert=False)
        
    def on(self):
        self.probe.on()
        
    def off(self):
        self.probe.off()

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

# wiring of Logic Analyzer
D0 = Probe(27)#blanc  ch1
D1 = Probe(16)#brun   ch2
D2 = Probe(17)#rouge  ch3
D3 = Probe(18)#orange ch4
D4 = Probe(19)#jaune  ch5
D5 = Probe(20)#vert   ch6
D6 = Probe(21)#bleu   ch7
D7 = Probe(26)#violet ch8



    

if __name__ == "__main__":
    def test():
        probe_gpio = 16 # a single  probe test 
        p = Probe(probe_gpio)
        
        while (True):

            for n in range (10):
                p.on()
                p.off()
                # time on -> off = 33 us
                utime.sleep_ms(1)

            utime.sleep(1)
            
            for n in range (10):
                p.pulses(n)
                # time n=1 on -> off = 7 us
                # time n=2 on -> off = 9 us
                # time n=10 on -> off = 8 us
            utime.sleep(1)

            for n in range (1,10):
                p.pulse_single(n)
                # time n=1 on -> off = 45 us
                # time n=2 on -> off = 37 us
                # time n=3 on -> off = 47 us
                # time n=4 on -> off = 56 us
                # time n=10 on -> off = 106 us
            utime.sleep(1)
            
            p.pulse_begin(3) # time on -> off = 3.02 ms 
            utime.sleep_us(500)
            p.pulse_end(3) # time on -> off = 3.12 ms
            utime.sleep(2)
        
    def test2(): # a test with multiple GPIO for logic analyser observation
        delay = const(100)
        probes = [D0, D1, D2, D3, D4, D5, D6, D7]
        while True:
            utime.sleep_ms(delay*len(probes))
            for p in probes:
                p.on()
                utime.sleep_ms(delay)
                p.off()
        
    test2()
