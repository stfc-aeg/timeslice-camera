import importlib
import threading
import time

class LedDriver(object):
    
    GreenLed = 19
    RedLed   = 26
    
    OFF    = 0
    RED    = 1
    GREEN  = 2
    YELLOW = 3
    
    
    def __init__(self, simulate=False):
        
        if not simulate:
            
            self.gpio = importlib.import_module('RPi.GPIO')
            self.gpio.setwarnings(False)
            self.gpio.setmode(self.gpio.BCM)
            self.gpio.setup(LedDriver.GreenLed, self.gpio.OUT)
            self.gpio.setup(LedDriver.RedLed, self.gpio.OUT)
            
        else:
            self.gpio = None
            
        self.colour = LedDriver.OFF
        self.blink_event = threading.Event()
        self.blink_thread = None
            
    def set_colour(self, colour=None):
        
        self.blink_event.set()
        self._set_colour(colour)
        
    def _set_colour(self, colour):
 
        self.colour = colour
        
        if self.gpio == None:
            print "LED colour is now {}".format(colour)
            return
 
        red = self.gpio.LOW
        green = self.gpio.LOW
         
        if colour == LedDriver.RED:
            red = self.gpio.HIGH
        elif colour == LedDriver.GREEN:
            green = self.gpio.HIGH
        elif colour == LedDriver.YELLOW:
            red = self.gpio.HIGH
            green = self.gpio.HIGH
             
        self.gpio.output(LedDriver.RedLed, red)
        self.gpio.output(LedDriver.GreenLed, green)
            
    
    def blink(self, colour1=0, colour2=1, period=1.0, repeat=0):
        
        self.blink_event.clear()
        self.blink_thread = threading.Thread(target = self._blink_loop, args=(colour1, colour2, period, repeat))
        self.blink_thread.start()
        
    def _blink_loop(self, colour1, colour2, period, repeat):
        
        current_colour = colour1
        
        while not self.blink_event.is_set():
            self._set_colour(current_colour)
            time.sleep(period)
            current_colour = colour2 if current_colour == colour1 else colour1
            if repeat > 0:
                repeat = repeat - 1
                if repeat == 0:
                    break
            
if __name__ == '__main__':
    
    led = LedDriver(True)
    
    led.set_colour(0)
    led.set_colour(1)
    led.set_colour(2)
    led.set_colour(3)
    
    led.blink(0, 1, 0.1, 10)
    time.sleep(2)
    
    led.blink(2,3, 0.1, 0)
    time.sleep(2)
    led.set_colour(1)    