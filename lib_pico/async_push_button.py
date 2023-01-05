from machine import Pin, Signal
import utime
import uasyncio



class Button():   
    def __init__(self, name,
                 gpio,
                 pull=-1,
                 interrupt_service_routine=None,
                 debounce_delay=100,
                 active_HI=True,
                 both_edge=False,
                 repeat=False,
                 repeat_delay=500):
        """
"""
        self.name = name
        self.interrupt_service_routine = interrupt_service_routine
        self.debounce_delay = debounce_delay
        self.active_HI = active_HI        
        self.both_edge = both_edge
        self.repeat = repeat
        self.repeat_delay = repeat_delay
        
        self.pin = Pin(gpio, Pin.IN, pull)
        self.signal = Signal(self.pin, invert=not self.active_HI)
        self.is_pressed=False        
        self.last_change_time = 0
        self.last_event_duration =0
        
        self.handler=None
        self.trigger = None
        
        self.handler = self.irq_handler
        
        if self.both_edge ==True:
            self.trigger = self.pin.IRQ_RISING | self.pin.IRQ_FALLING
        else:
            if self.active_HI == True:
                self.trigger = self.pin.IRQ_RISING
            else:
                self.trigger = self.pin.IRQ_FALLING
        
        self.pin.irq(handler=self.handler, trigger=self.trigger)
         
    def set_irq_routine(self, routine):
        self.interrupt_service_routine = routine
       
    async def irq_repeat_handler(self, pin):
        status = self.is_pressed
        while status == bool(self.signal.value()):
            self.interrupt_service_routine(self)
            await uasyncio.sleep_ms(int(self.repeat_delay))        
        
    def irq_handler(self, pin):
        self.pin.irq(handler=None)    
        self.current_change_time = utime.ticks_ms()
        self.is_pressed = bool(self.signal.value())
        #print(self.is_pressed)
        last_event_delay = self.current_change_time - self.last_change_time
        # print(f"@{utime.ticks_ms()} Button/irq_handler/last_event_delay={last_event_delay}")
        self.last_change_time = self.current_change_time
        if last_event_delay >= self.debounce_delay:
            self.last_event_duration = last_event_delay
            if self.repeat == True:
                uasyncio.run(self.irq_repeat_handler(pin))
            else:
                self.interrupt_service_routine(self)
        self.pin.irq(handler=self.irq_handler)        

def test():
    print("start test: 'push_button'\
                        \n press any button")
     
    def button_handler(button):
        if button.is_pressed == True:
            print(f"button name: {button.name} pressed")
        else:
            print(f"button name: {button.name} released")
    
    K1_gpio = 2
    K1 = Button("K1", K1_gpio,
                interrupt_service_routine=button_handler,
                active_HI= False, repeat=True)
    
    K2_gpio = 3
    K2 = Button("K2", K2_gpio,
                interrupt_service_routine=button_handler,
                active_HI= False, repeat=True)
    
    K3_gpio = 22
    K3 = Button("K3", K3_gpio,
                interrupt_service_routine=button_handler,
                active_HI= False, both_edge=True, repeat=False)
    
    K4_gpio = 12
    K4 = Button("K4", K4_gpio, pull=Pin.PULL_DOWN,
                interrupt_service_routine=button_handler,
                active_HI= True, both_edge=True, repeat=False)
    
    K5_gpio = 13
    K5 = Button("K5", K5_gpio, pull=Pin.PULL_UP,
                interrupt_service_routine=button_handler,
                active_HI= False, repeat=False)
    

if __name__ == "__main__":
    test()
    

