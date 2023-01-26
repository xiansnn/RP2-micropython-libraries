from lib_pico.ST7735 import TFT
from lib_pico.sysfont import sysfont
from machine import SPI, Pin
import utime

BLANK = chr(218)
display_first_px = 1
display_first_py = 1


class TFT_display():
    '''
The physical hardware display ST7735, based on ST735.py library and TFT class
'''
    def __init__(self,
                 SCK_PIN=10, MOSI_PIN=11, MISO_PIN=12, #SPI interface
                 DataCommand_PIN=14, Reset_PIN=15, ChipSelect_PIN = 13 #TFT screen interface
                 ): 
        #setup SPI
        self.spi = SPI(1, baudrate=20000000, polarity=0, phase=0, sck=Pin(SCK_PIN),
                  mosi=Pin(MOSI_PIN), miso=Pin(MISO_PIN))
        #init display
        self.tft = TFT(self.spi, DataCommand_PIN, Reset_PIN, ChipSelect_PIN)
        self.tft.initg()
        self.tft.rgb(True)
        self.tft.fill(TFT.BLACK)
        self.frames = {}
        
    def add_frame(self, name, aStart, aEnd,
                  background_color=TFT.BLACK, font=sysfont, font_size_factor=(1,1),
                  left_border=0, top_border=0 ):
        f=Frame(self, name, aStart, aEnd,
                background_color=background_color, font_size_factor=font_size_factor,
                top_border=top_border, left_border=left_border )
        self.frames[f.name] = f
        return f

class Frame():
    '''
Frame is an area of the display where we can write text. Characters are based on <sysfont.py> font.
Frame dimension is based on a grid. The grid dimension is computed with respect to the dimension of the font Width and Height. 
name : the name of the frame in the TFT_display dictionary
first_grid_line : 
first_grid_column : 
last_grid_line : 
last_grid_column : 
background_color=TFT.BLACK : only background_color is an attribute of a frame. foreground_color is an attibute of the characters
font=sysfont : 
font_size_factor=(1,1) : 
horiz_border=0 : the number of pixel space on left and right side of the frame
vert_border=0 : the number of pixel space on top and bottom side of the frame
'''
    def __init__(self,screen, name, start_pixel, end_pixel,
                background_color=TFT.BLACK, font=sysfont , font_size_factor=(1,1),
                top_border=0, left_border=0 ):
        self.tft = screen.tft
        self.name = name        
        self.background_color = background_color
        self.font = font        
        self.left_border = left_border
        self.top_border = top_border

        self.start_pixel = start_pixel
        self.end_pixel = end_pixel
        self.first_px, self.first_py = self.start_pixel
        self.last_px, self.last_py = self.end_pixel
        self.px_frame_size = self.last_px - self.first_px +1
        self.py_frame_size = self.last_py - self.first_py +1
        self.px_char_start = self.first_px + self.left_border
        self.py_char_start = self.first_py + self.top_border
        
        self.first_grid_line = 0
        self.first_grid_column = 0        
        self.current_char_line = self.first_grid_line
        self.current_char_column = self.first_grid_column
        self.set_background_color(background_color)
        self.set_font_size_factor(font_size_factor)

    def set_background_color(self, color):
        self.background_color = color
        self.erase_frame()

    def erase_frame(self):
        aSize = (self.px_frame_size   ,  self.py_frame_size)
        self.tft.fillrect(self.start_pixel, aSize, self.background_color )

    def _erase_char_line(self):
        aStart = (self.first_px       ,  self.first_py + self.current_char_line*self.grid_size[1]  )
        aSize  = (self.px_frame_size  ,  self.grid_size[1]      )
        self.tft.fillrect( aStart, aSize, self.background_color)


    def set_font_size_factor(self, font_size_factor):
        ''' this method can be used when the font size of a frame is changed after __init__'''
        self.font_size_factor = font_size_factor
        self.grid_size = ((self.font["Width"]  +1)*self.font_size_factor[0] ,
                          (self.font["Height"] +1)*self.font_size_factor[1] ) # ST7735.py places a 1-pixel space between each character
        self.last_grid_line = int((self.py_frame_size - self.top_border)/self.grid_size[1]) - 1
        self.last_grid_column = int((self.px_frame_size - self.left_border)/self.grid_size[0]) - 1  
        if __name__ == "__main__":
            print(f"frame:{self.name}")
            print(f"\tfirst_px:{self.first_px}\tlast_px:{self.last_px}\tpx_frame_size:{self.px_frame_size}\tleft_border:{self.left_border}")
            print(f"\tfirst_py:{self.first_py}\tlast_py:{self.last_py}\tpy_frame_size:{self.py_frame_size}\ttop_border:{self.top_border}")
            print(f"\tfont_size_factor:{self.font_size_factor}\tgrid_size:{self.grid_size}")
            print(f"\tfirst_grid_line:{self.first_grid_line}\tlast_grid_line:{self.last_grid_line}")
            print(f"\tfirst_grid_column:{self.first_grid_column}\tlast_grid_column:{self.last_grid_column}")
       
        
      
    def _reset_char_position(self):
        self.current_char_column=self.first_grid_column
        self.current_char_line=self.first_grid_line
    
        
    def write_text(self, txt, foreground_color, append=True, reset_position=True):
        if reset_position:
            self._reset_char_position()
        for char in txt:
            self.write_char(char, foreground_color, append=append)
            
    def write_char(self, char, foreground_color, append=True):
        if self.current_char_column > self.last_grid_column: # check if there is enough room to write the char on this line
            self._next_char_column()
        px = self.px_char_start + self.current_char_column*self.grid_size[0]
        py = self.py_char_start + self.current_char_line*self.grid_size[1]
        self.tft.char((px,py), char, foreground_color, self.font, self.font_size_factor, bgColor=self.background_color )
        if append:
            self._next_char_column()

    def _next_char_column(self, step=1):
        if self.current_char_column > self.last_grid_column: # check if there is enough room to write the char on this line
            self.current_char_column = self.first_grid_column
            self._next_char_line() 
        else:
            self.current_char_column += step
        
    def _next_char_line(self):
        if self.current_char_line >= self.last_grid_line: 
            self.current_char_line = self.first_grid_line
            self.erase_frame()
        else:
            self.current_char_line += 1
        self._erase_char_line()

    
        
           
           
           

def test_all():
    """
"""
    print("start test: several frames, size, wrap-around, etc")
    ui=TFT_display()
    AA = ui.add_frame("AA",(0,0),(66,11),left_border=0, top_border=1, background_color=TFT.YELLOW )
    AB = ui.add_frame("AB",(67,0),(96,9),left_border=0, top_border=1, background_color=TFT.YELLOW)
    AC = ui.add_frame("AC",(97,0),(126,9),left_border=0, top_border=1, background_color=TFT.YELLOW)
    
    BA = ui.add_frame("BA",(0,10),(66,18))    
    BB = ui.add_frame("BB",(67,10),(114,18))
    BC = ui.add_frame("BC",(115,10),(126,18))
    
    CA = ui.add_frame("CA",(0,19),(24,27))
    CB = ui.add_frame("CB",(25,19),(30,27), background_color=TFT.GRAY)
    CC = ui.add_frame("CC",(31,19),(66,27))
    CD = ui.add_frame("CD",(67,19),(90,27),background_color=TFT.GOLD)
    CE = ui.add_frame("CE",(91,19),(126,27),background_color=TFT.YELLOW)    
    
    DA = ui.add_frame("DA",(0,28),(24,36),background_color=TFT.BLACK)
    DB = ui.add_frame("DB",(25,28),(54,36),background_color=TFT.BLACK)
    DC = ui.add_frame("DC",(55,28),(90,36),background_color=TFT.GOLD)
    DD = ui.add_frame("DD",(91,28),(126,36),background_color=TFT.BLACK)
    
    EA = ui.add_frame("EA",(0,37),(24,45), background_color=TFT.BLACK)
    EB = ui.add_frame("EB",(25,37),(60,45), background_color=TFT.BLACK)
    EC = ui.add_frame("EC",(61,37),(90,45), background_color=TFT.BLACK)
    ED = ui.add_frame("ED",(91,37),(126,45),background_color=TFT.BLACK)
    
    FA = ui.add_frame("FA",(0,46),(126,117),background_color=TFT.GRAY, left_border=0, top_border=2 )
    
    GA = ui.add_frame("GA",(0,118),(126,126),background_color=TFT.BLACK, left_border=0, top_border=1 )
    

    AA.write_text("frame1....>", TFT.RED)
    AC.write_text("units", TFT.LIME)
    BA.write_text("frame2....>", TFT.ORANGE)
    BC.write_text("ms", TFT.GOLD)
    CC.write_text("YELLOW", TFT.YELLOW)
    CD.write_text("NAVY", TFT.NAVY)
    CE.write_text("_BLUE_", TFT.BLUE)
    
    DA.write_text("GRAY", TFT.GRAY)
    DB.write_text("GREEN", TFT.GREEN)
    DC.write_text("MAROON", TFT.MAROON)
    DD.write_text("ORANGE", TFT.ORANGE)
    EA.write_text("GOLD", TFT.GOLD)
    EB.write_text("FOREST", TFT.FOREST)
    EC.write_text("WHITE", TFT.WHITE)
    ED.write_text("PURPLE", TFT.PURPLE)
    
    
    GA.write_text("this is the last line", TFT.GRAY)

    
    for step in range(10):
        wpm=6 + step
        dot=800/wpm  
        AB.write_text(f"{wpm:0>5d}", TFT.GREEN)
        BB.write_text(f"{dot:0>8.2f}", TFT.FOREST)
        utime.sleep_ms(200)
#     
    #search 1st char
    CA.write_char("A", TFT.RED, append=False)
    utime.sleep_ms(200)
    CA.write_char("B", TFT.RED, append=False)
    utime.sleep_ms(200)
    CA.write_char("C", TFT.RED, append=False)
    CA._next_char_column() # char found C
    utime.sleep_ms(200)
    #search 2nd char
    CA.write_char("D", TFT.RED, append=False)
    utime.sleep_ms(200)
    CA.write_char("E", TFT.RED, append=False)
    utime.sleep_ms(200)
    CA.write_char("Q", TFT.RED, append=False)
    CA._next_char_column() # char found F
    utime.sleep_ms(200)
    #search 3rd char
    CA.write_char("G", TFT.RED, append=False)
    utime.sleep_ms(200)
    CA.write_char("F", TFT.RED, append=False)
    CA._next_char_column() #char found F
    utime.sleep_ms(200)
    #search 4th char
    CA.write_char("I", TFT.RED, append=False)
    utime.sleep_ms(200)
    CA.write_char("J", TFT.RED, append=False)
    utime.sleep_ms(200)
    CA.write_char("D", TFT.RED, append=False)
    utime.sleep_ms(200)
    CA._next_char_column(3) #char found D
#
    msg = ("123456789012345678901 "*13)
    FA.write_text(msg, TFT.BLUE)
#    
    utime.sleep_ms(1000)
    msg = ("1234567890")
    CB.write_text(msg, TFT.BLACK)
#    
    utime.sleep_ms(1000)
    FA.erase_frame()
    FA.write_text("CYAN", TFT.CYAN)
#    
    utime.sleep_ms(1000)
    CA.erase_frame()
    CA.write_text("RED",TFT.RED, reset_position= True)
#
    utime.sleep_ms(1000)
    ui.frames["FA"].erase_frame()
    ui.frames["FA"].set_font_size_factor((4,3))
    ui.frames["FA"].set_background_color(TFT.BLUE)
    msg = ("ABCDEFGHI")
    FA.write_text(msg,TFT.WHITE)

    print("end test")


def test_font():
    print("start test3: test font")
    #init display
    screen = TFT_display()
    frame = screen.add_frame("show_font", (0,0), (127,127),
                  background_color=TFT.BLACK, font=sysfont, font_size_factor=(1,1),
                  top_border=1, left_border=1 )
    
    for page in range(7):
        for n in range(42):
            char_num = n + page*42
            if char_num >= 254 : break
            char_tab = f"{char_num:>3d}  {chr(char_num):1s} "
            frame.write_text(char_tab, TFT.WHITE, append=True, reset_position=False)
        utime.sleep(4)
   
def test_color():
    from lib_pico.ST7735 import TFTColor
    print("Start test color")
    color_dict = {
      "BLACK"  : 0,
      "WHITE"  : TFTColor(0xFF, 0xFF, 0xFF),
      "RED"    : TFTColor(0xFF, 0x00, 0x00),
      "LIME"   : TFTColor(0x00, 0xFF, 0x00),
      "BLUE"   : TFTColor(0x00, 0x00, 0xFF),
      "YELLOW" : TFTColor(0xFF, 0xFF, 0x00),
      "CYAN"   : TFTColor(0x00, 0xFF, 0xFF),
      "MAGENTA": TFTColor(0xFF, 0x00, 0xFF),

      "SILVER" : TFTColor(0xC0, 0xC0, 0xC0),
      "GRAY"   : TFTColor(0x80, 0x80, 0x80),
      "MAROON" : TFTColor(0x80, 0x00, 0x00),
      "OLIVE"  : TFTColor(0x80, 0x80, 0x00),
      "GREEN"  : TFTColor(0x00, 0x80, 0x00),
      "PURPLE" : TFTColor(0x80, 0x00, 0x80),
      "TEAL"   : TFTColor(0x00, 0x80, 0x80),
      "NAVY"   : TFTColor(0x00, 0x00, 0x80),

      "ORANGE" : TFTColor(0xFF, 0xA5, 0x00),
      "GOLD"   : TFTColor(0xFF, 0xD7, 0x00),
      "FOREST" : TFTColor(0x22, 0x8B, 0x22)
      }
    
    ui=TFT_display()
    n=0
    for c in color_dict:
        start_x = n%2 * 64
        end_x   = n%2 * 63 + 63
        start_y = int(n/2) * 10
        end_y = int(n/2) * 10 +9
        start = (start_x,start_y)
        end = (end_x, end_y)
        f = ui.add_frame(str(n),start,end, top_border=2, background_color=color_dict[c])
        f.write_text(f"{c}",color_dict["BLACK"])
        n+=1
        
    
if __name__ == "__main__":
    test_all()
    utime.sleep(2)
    test_font()
    utime.sleep(2)
    test_color()
      
    

