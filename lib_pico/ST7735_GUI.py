from lib_pico.ST7735 import TFT
from lib_pico.sysfont import sysfont
from machine import SPI, Pin
import utime

BLANK = chr(218)
px_origin = 1
py_origin = 1


class TFT_display():
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
        self.LINE_NB =int(self.tft.size()[0]/( sysfont["Width"]+1))
        self.COLUMN_NB = int(self.tft.size()[1]/( sysfont["Height"]+1))
        self.frames = {}
        
    def add_frame(self, name, first_line, first_column, last_line, last_column,
                  foreground_color, background_color=TFT.BLACK, font=sysfont):
        f=Frame(self, name, first_line, first_column, last_line, last_column,
                foreground_color, background_color=TFT.BLACK)
        self.frames[f.name] = f
        return f

class Frame():
    def __init__(self,screen, name, first_line, first_column, last_line, last_column,
                 foreground_color, background_color=TFT.BLACK, font=sysfont):
        self.tft = screen.tft
        self.font = font
        self.name = name
        self.first_line = first_line
        self.first_column = first_column
        self.last_line = last_line
        self.last_column = last_column
        self.line_size = self.last_column-self.first_column+1
        self.column_size = self.last_line-self.first_line+1
        self.foreground_color = foreground_color
        self.background_color = background_color
        self.current_line = self.first_line
        self.current_column = self.first_column

    def reset_char_position(self):
        self.current_column=self.first_column
        self.current_line=self.first_line
    
        
    def write_text(self, txt, append=True, reset_position=True):
            if reset_position:
                self.reset_char_position()
            for c in txt:
                self.write_char(c, append=append)
            
    def write_char(self, char, append=True):
        if self.current_column > self.last_column:
            self.next_column()
        px= px_origin + self.current_column*(self.font["Width"]+1)
        py= px_origin + self.current_line*(self.font["Height"]+1)
        self.tft.char((px,py), char, self.foreground_color, self.font, (1,1) )
        if append:
            self.next_column()

    def next_column(self, step=1):
            if self.current_column > self.last_column:
                self.current_column = self.first_column
                self.next_line()
            else:
                self.current_column +=step
        
    def next_line(self):
        if self.current_line == self.last_line:
            self.current_line = self.first_line
            self.erase_frame()
        else:
            self.current_line +=1
        self.erase_line()

    def erase_line(self):
        py= py_origin + self.current_line*(self.font["Height"]+1)
        current_x = self.first_column
        for i in range(self.line_size):
            px= px_origin + current_x*(self.font["Width"]+1)
            self.tft.char((px,py), BLANK, self.background_color, self.font, (1,1) )
            current_x += 1
    def erase_frame(self):
        self.current_column=self.first_column
        self.current_line = self.first_line
        for i in range(self.column_size):
            self.erase_line()
            self.current_line += 1
        self.reset_char_position()
        
           
#TODO   faire un test independant de morse_keying_manager      
def test():
    """
"""
    print("start test: 'ST7735_GUI'")
    ui=TFT_display()
    AA = ui.add_frame("AA",0,0,0,10,TFT.RED)
    AB = ui.add_frame("AB",0,11,0,15,TFT.GREEN)
    AC = ui.add_frame("AC",0,16,0,20,TFT.MAROON)
    BA = ui.add_frame("BA",1,0,1,10,TFT.ORANGE)    
    BB = ui.add_frame("BB",1,11,1,18,TFT.FOREST)
    BC = ui.add_frame("BC",1,19,1,20,TFT.GOLD)
    CA = ui.add_frame("CA",2,0,2,3,TFT.RED)
    CB = ui.add_frame("CB",2,4,2,4,TFT.BLUE)
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
    
    #search 1st char
    CA.write_char("A",append=False)
    utime.sleep_ms(200)
    CA.write_char("B",append=False)
    utime.sleep_ms(200)
    CA.write_char("C",append=False)
    CA.next_column() # char found C
    utime.sleep_ms(200)
    #search 2nd char
    CA.write_char("D",append=False)
    utime.sleep_ms(200)
    CA.write_char("E",append=False)
    utime.sleep_ms(200)
    CA.write_char("Q",append=False)
    CA.next_column() # char found F
    utime.sleep_ms(200)
    #search 3rd char
    CA.write_char("G",append=False)
    utime.sleep_ms(200)
    CA.write_char("F",append=False)
    CA.next_column() #char found F
    utime.sleep_ms(200)
    #search 4th char
    CA.write_char("I",append=False)
    utime.sleep_ms(200)
    CA.write_char("J",append=False)
    utime.sleep_ms(200)
    CA.write_char("D",append=False)
    utime.sleep_ms(200)
    CA.next_column(3) #char found D

    
    msg = ("123456789012345678901   "*15)
    FA.write_text(msg)
    msg = ("1234567890")
    CB.write_text(msg)#     utime.sleep_ms(6000)
    utime.sleep_ms(200)
    FA.erase_frame()
    FA.write_text("CYAN")
    utime.sleep_ms(200)
    CA.erase_frame()
    CA.write_text("RED", reset_position= True)
    print("end test")

if __name__ == "__main__":
    test()      
