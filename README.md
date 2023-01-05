# RP2-micropython
## My Raspberry Pi Pico projects

This is the place where one can find my coding and DIY projects.
All the material here is developped on MakerFab Pico development board.
The associated resources can be found at https://github.com/Makerfabs/Pico_Primer_Kit.git

## Debug_utility folder
This is a general purpose modules that I've used in my projects

## lib_pico folder
General purpose modules developped for use in my projects

### ST7735.py and sysfont.py
These are the original unchanged drivers copied from https://github.com/Makerfabs/Pico_Primer_Kit/tree/main/example/lib.

### async_push_button.py and push_button.py
These are two versions of a general purpose push button driver. 
They provide debounce feature, IRQ handler, choice of trigger (falling edge, rising edge, both edges), and "repeat" capability.
- push_button.py is a synchronous version. It is no longer maintained or used, because it blocks te execution of the processor.
- async_push_button.py is a more efficient asynchronous version, relying on "asyncio" library.

### ST7735_GUI.py 
This is a wrapper for the original ST7735.py driver. 
It provides for writing text methods in dedicated frames on the ST7735 LCD display. 
However, It is limited to text only, graphic capabilities can be performed in dedicated area with the original driver.
