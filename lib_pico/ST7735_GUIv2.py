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
        #GRID is used to position frames on a grid that fits with the sysfont size (1,1) 
        self.GRID_LINE_NB =int(self.tft.size()[0]/( sysfont["Width"]+1))
        self.GRID_COLUMN_NB = int(self.tft.size()[1]/( sysfont["Height"]+1))
        self.frames = {}
        
    def add_frame(self, name, first_line, first_column, last_line, last_column,
                  foreground_color, background_color=TFT.BLACK, font=sysfont, font_size_factor=(1,1) ):
        f=Frame(self, name, first_line, first_column, last_line, last_column,
                foreground_color, background_color=TFT.BLACK , font_size_factor=font_size_factor )
        self.frames[f.name] = f
        return f

class Frame():
    '''
'''
    def __init__(self,screen, name, first_grid_line, first_grid_column, last_grid_line, last_grid_column,
                 foreground_color, font=sysfont , background_color=TFT.BLACK , font_size_factor=(1,1) ):
        self.tft = screen.tft
        self.name = name

        self.foreground_color = foreground_color
        self.background_color = background_color

        self.font = font
        
        # this is the position of the frame expressed in size(1,1)font unit
        self.first_grid_line = first_grid_line
        self.first_grid_column = first_grid_column
        self.last_grid_line = last_grid_line
        self.last_grid_column = last_grid_column
        self.grid_size = ((self.font["Width"]+1) , (self.font["Height"]+1) )
        
        # this is the position of the frame expressed in pixels coordinates
        self.first_px = display_first_px + self.first_grid_column*self.grid_size[0]
        self.first_py = display_first_py + self.first_grid_line*self.grid_size[1]
        self.last_px = (self.last_grid_column+1)*self.grid_size[0]
        self.last_py = (self.last_grid_line+1)*self.grid_size[1]
        self.px_frame_size = self.last_px - self.first_px +1
        self.py_frame_size = self.last_py - self.first_py +1
        
        self.set_font_size_factor(font_size_factor)

    def set_foreground_color(self, color):
        self.foreground_color = color
        
    def set_font_size_factor(self, font_size_factor):
        ''' this method can be used when the font size of a frame is changed after __init__'''
        # this is used to position the char in coordinates expressed in unit of this frame font size and all dependent variables
        self.font_size_factor = font_size_factor # this the font size within this frame
        self.char_size = (self.grid_size[0]*self.font_size_factor[0] , self.grid_size[1]*self.font_size_factor[1] )        
        self.first_char_column = 0 #char coordinates are expressed wrt frame origin
        self.first_char_line = 0
        self.last_char_column =  int(self.px_frame_size/self.char_size[0]) - 1
        self.last_char_line = int(self.py_frame_size/self.char_size[1]) - 1
        
        self.current_char_line = self.first_char_line
        self.current_char_column = self.first_char_column
        
#         print (f"name:{self.name}, char_w:{self.char_size[0]}, char_h:{self.char_size[1]}") 
#         print(f"\tfirst_char_line:{self.first_char_line}\tfirst_char_column:{self.first_char_column}")
#         print(f"\tlast_char_line:{self.last_char_line}\t last_char_column:{self.last_char_column}")
#         print(f"\tfirst_px:{self.first_px}\tlast_px:{self.last_px}\tpx_size:{self.px_frame_size}")
#         print(f"\tfirst_py:{self.first_py}\tlast_py:{self.last_py}\tpy_size:{self.py_frame_size}")
        
    def reset_char_position(self):
        self.current_char_column=self.first_char_column
        self.current_char_line=self.first_char_line
    
        
    def write_text(self, txt, append=True, reset_position=True):
        if reset_position:
            self.reset_char_position()
        for char in txt:
            self.write_char(char, append=append)
            
    def write_char(self, char, append=True):
        if self.current_char_column > self.last_char_column: # check if there is enough room to write the char on this line
            self.next_char_column()
        px = self.first_px + self.current_char_column*self.char_size[0]
        py = self.first_py + self.current_char_line*self.char_size[1]
        self.tft.char((px,py), char, self.foreground_color, self.font, self.font_size_factor )
        if append:
            self.next_char_column()

    def next_char_column(self, step=1):
        if self.current_char_column > self.last_char_column: # check if there is enough room to write the char on this line
            self.current_char_column = self.first_char_column
            self.next_char_line() 
        else:
            self.current_char_column += step
        
    def next_char_line(self):
        if self.current_char_line >= self.last_char_line: 
            self.current_char_line = self.first_char_line
            self.erase_frame()
        else:
            self.current_char_line += 1
        self.erase_char_line()

    def erase_char_line(self):
        py= self.first_py + self.current_char_line*self.char_size[1]
        for i in range(self.last_char_column + 1):
            px = self.first_px + i *self.char_size[0]
            self.tft.char((px,py), BLANK, self.background_color, self.font, self.font_size_factor )
    
    def erase_frame(self):
        self.current_char_line = self.first_char_line
        for i in range(self.last_char_line +1):
            self.erase_char_line()
            self.current_char_line += 1
        self.reset_char_position()
        
           
           
           
def test():
    """
"""
    print("start test: 'ST7735_GUIv2'\n")
    ui=TFT_display()
    AA = ui.add_frame("AA",0,0,0,10,TFT.RED)
    AB = ui.add_frame("AB",0,11,0,15,TFT.GREEN)
    AC = ui.add_frame("AC",0,16,0,20,TFT.MAROON)
    BA = ui.add_frame("BA",1,0,1,10,TFT.ORANGE)    
    BB = ui.add_frame("BB",1,11,1,18,TFT.FOREST)
    BC = ui.add_frame("BC",1,19,1,20,TFT.GOLD)
    CA = ui.add_frame("CA",2,0,2,3,TFT.RED)
    CB = ui.add_frame("CB",2,4,2,4,TFT.GREEN)
    CC = ui.add_frame("CC",2,5,2,10,TFT.YELLOW)
    CD = ui.add_frame("CD",2,11,2,14,TFT.NAVY)
    CE = ui.add_frame("CE",2,15,2,20,TFT.BLUE)    
    FA = ui.add_frame("FA",5,0,12,20,TFT.CYAN)
    NA = ui.add_frame("NA",13,0,13,20,TFT.GRAY)
    
    DA = ui.add_frame("DA",3,0,3,3,TFT.GRAY)
    DB = ui.add_frame("DB",3,4,3,8,TFT.GREEN)
    DC = ui.add_frame("DC",3,9,3,14,TFT.MAROON)
    DD = ui.add_frame("DD",3,15,3,20,TFT.ORANGE)
    EA = ui.add_frame("EA",4,0,4,3,TFT.GOLD)
    EB = ui.add_frame("EB",4,4,4,9,TFT.FOREST)
    EC = ui.add_frame("EC",4,10,4,14,TFT.WHITE)
    ED = ui.add_frame("ED",4,15,4,20,TFT.PURPLE)

    AA.write_text("frame1....>")
    AC.write_text("units")
    BA.write_text("frame2....>")
    BC.write_text("ms")
    CC.write_text("YELLOW")
    CD.write_text("NAVY")
    CE.write_text("_BLUE_")
    
    DA.write_text("GRAY")
    DB.write_text("GREEN")
    DC.write_text("MAROON")
    DD.write_text("ORANGE")
    EA.write_text("GOLD")
    EB.write_text("FOREST")
    EC.write_text("WHITE")
    ED.write_text("PURPLE")
    
    
    NA.write_text("this is the last line")

    
    for step in range(10):
        wpm=6 + step
        dot=800/wpm  
        AB.write_text(f"{wpm:0>5d}")
        BB.write_text(f"{dot:0>8.2f}")
        utime.sleep_ms(200)
#     
    #search 1st char
    CA.write_char("A",append=False)
    utime.sleep_ms(200)
    CA.write_char("B",append=False)
    utime.sleep_ms(200)
    CA.write_char("C",append=False)
    CA.next_char_column() # char found C
    utime.sleep_ms(200)
    #search 2nd char
    CA.write_char("D",append=False)
    utime.sleep_ms(200)
    CA.write_char("E",append=False)
    utime.sleep_ms(200)
    CA.write_char("Q",append=False)
    CA.next_char_column() # char found F
    utime.sleep_ms(200)
    #search 3rd char
    CA.write_char("G",append=False)
    utime.sleep_ms(200)
    CA.write_char("F",append=False)
    CA.next_char_column() #char found F
    utime.sleep_ms(200)
    #search 4th char
    CA.write_char("I",append=False)
    utime.sleep_ms(200)
    CA.write_char("J",append=False)
    utime.sleep_ms(200)
    CA.write_char("D",append=False)
    utime.sleep_ms(200)
    CA.next_char_column(3) #char found D
#
    msg = ("123456789012345678901 "*13)
    FA.write_text(msg)
#    
    utime.sleep_ms(1000)
    msg = ("1234567890")
    CB.write_text(msg)
#    
    utime.sleep_ms(1000)
    FA.erase_frame()
    FA.write_text("CYAN")
#    
    utime.sleep_ms(1000)
    CA.erase_frame()
    CA.write_text("RED", reset_position= True)
#
    utime.sleep_ms(1000)
    ui.frames["FA"].erase_frame()
    ui.frames["FA"].set_font_size_factor((4,3))
    ui.frames["FA"].set_foreground_color(TFT.WHITE)
    msg = ("ABCDEFGH")
    FA.write_text(msg)

    print("\nend test")

def test2():
    print("start test2\n")
    
    ui=TFT_display()
    ZZ = ui.add_frame("ZZ",12,0,13,20,TFT.GRAY)
    ZZ.write_text("this is the very  last line ")
    
    ZA = ui.add_frame("ZA",0,0,0,10,TFT.YELLOW)
    ZB = ui.add_frame("ZB",2,0,3,20,TFT.WHITE, font_size_factor=(2,2)  )
    ZC = ui.add_frame("ZC",4,0,6,20,TFT.GREEN, font_size_factor=(3,3)  )
    ZD = ui.add_frame("ZD",7,0,11,20,TFT.PURPLE, font_size_factor=(4,4)  )
    for step in range(20): 
        ZA.write_text(f"{step:0>3d}")
        ZB.write_text(f"{step:0>3d}")
        ZC.write_text(f"{step:0>3d}")
        ZD.write_text(f"{step:0>3d}")        
        utime.sleep_ms(500)


    print("\nend test")

if __name__ == "__main__":
#     test()
#     utime.sleep(1)
    test2()
