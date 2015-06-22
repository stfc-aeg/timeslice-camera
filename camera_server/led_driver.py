import importlib

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
            
    def set_colour(self, colour=None):
 
        self.colour = colour
        
        if self.gpio == None:
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
            
        