from lib_pico.ST7735 import TFT
from lib_pico.ST7735_TextUIv2 import TFT_display
# from lib_pico.sysfont import sysfont



class Scale():
    def __init__(self, frame, relative_Start, length, color):
        px, py = frame.start_pixel
        dx, dy = relative_Start
        self.frame = frame
        self.start = (px+dx,py+dy)
        self.length = length
        self.color = color
        self.draw_scale()

    def set_color(self, color):
        self.color = color
    def draw_scale(self):
        self.frame.tft.hline( self.start, self.length, self.color )
        v_len = -6
        bottom = self.start[0] + self.length    
        self.frame.tft.vline( self.start, v_len, self.color )
        self.frame.tft.vline( (bottom,self.start[1]), v_len, self.color )
   
    def set_value(self, value):
        if value>=59:
            color = self.frame.background_color
        else :
            color = self.color
        self.draw_scale()
        dl = int(self.length/60)
        for n in range(value+1):
            if n%10==0 : v_len = -6
            elif n%5==0 : v_len = -4
            else: v_len = -2
            bottom = self.start[0] + n*dl
            self.frame.tft.vline( (bottom,self.start[1]), v_len, color )


if __name__=="__main__":
    import time
    screen = TFT_display()
    frame = screen.add_frame("scale", (0,0), (127,10), background_color=TFT.BLACK)
    scale = Scale(frame, (4,8),120, TFT.YELLOW)
    for i in range(5):
        for n in range(61):
            time.sleep_ms(50)
            scale.set_value(n)
    
