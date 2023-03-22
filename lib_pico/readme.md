# DHT11

## DHT11_v2.py
This is a pure async driver for DHT11 temperature and humidity sensor

# ST7735.py and sysfont.py
These are derived from the original drivers copied from [Pico Primer kit](https://github.com/Makerfabs/Pico_Primer_Kit/tree/main/example/lib).

ST7735.py has been changed to fix a bug when the font size is > 1, and background capability has also been added

# async_push_button.py and push_button.py
These are two versions of a general purpose push button driver. 
They provide debounce feature, IRQ handler, choice of trigger (falling edge, rising edge, both edges), and "repeat" capability.
- push_button.py is a synchronous version. It is no longer maintained or used, because it blocks te execution of the processor.
- async_push_button.py is a more efficient asynchronous version, relying on "asyncio" library.

# ST7735_TextUIv2.py 
This is a wrapper for the original ST7735.py driver. 
It provides for writing text methods in dedicated frames on the ST7735 LCD display. 
However, It is limited to text only, graphic capabilities could probably be performed in dedicated area with the original driver.

# Filter

## filter.py
This is a general purpose Filter base class implementing the generic formula : y0 = a0.x0 + a1.x1 + a2.x2 + ..... b1.y1 + b2.y2 + ....

Then inherited classes are provided to implement PID, FileredPID, Means.



