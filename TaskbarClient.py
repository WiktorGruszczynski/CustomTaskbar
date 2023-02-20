from TaskbarCenter import TaskbarCenter, win11_center
from TaskbarStyle import TaskbarStyler
from threading import Thread
import platform
import time
import os


OS_NAME = f"{platform.system()} {platform.release()}"

config_path = ".cfg"
deafult_config = [
    'animation=True',
    'align_center=True',
    'align_primary=True',
    'align_secondary=True',
    'refresh_rate=0.2',
    'speed=200',
    'offset=0',
    'style=0'
]



def UpdateConfig(new_config):
    with open(config_path, "w") as file:
        file.write(new_config)


def ReadConfig():
    if os.path.exists(config_path):
        with open(config_path, "r") as file:
            text = file.read()
    else:
        UpdateConfig("\n".join(deafult_config))
        return ReadConfig()

    config_dict = {}
    for element in [i.split('=') for i in text.split('\n')]:
        key, value = element
        config_dict[key] = eval(value)
    
    return config_dict


class TaskbarClient(TaskbarCenter, TaskbarStyler):
    def __init__(self) -> None:
        TaskbarCenter.__init__(self)
        TaskbarStyler.__init__(self)
        self.load_config()
        self.interval= self.interval
        self.running = True
        self.threads = [None, None]
        
        
        if self.align_center:
            if OS_NAME == "Windows 11":
                win11_center(True)
            else:
                if self.align_primary:
                    self.PrimaryTaskBarLoop()

                if self.align_secondary and self.detect_secondary():
                    self.SecondaryTaskBarLoop()
        else:
            win11_center(False)


        self.StylingLoop()


    def load_config(self):
        config = ReadConfig()
        self.speed = config["speed"]
        self.animation = bool(config["animation"])
        self.align_center = bool(config["align_center"])
        self.align_primary = bool(config["align_primary"])
        self.align_secondary = bool(config["align_secondary"])
        self.interval = config["refresh_rate"]
        self.offset = config["offset"]
        self.style = config["style"]
        self.load_style()


    def load_style(self):
        if self.style == 0: #deafult
            self.style_func = None
        elif self.style == 1: #blured
            self.style_func = self.blurred
        elif self.style == 2: #transparent
            self.style_func = self.transparent

    def PrimaryTaskBarLoop(self):
        def callback():
            while self.running:
                try:
                    self.CenterPrimary()
                except Exception as err:                 
                    self.load_handles()


                time.sleep(self.interval)
        

        self.threads[0] = Thread(target=callback)
        self.threads[0].start()


    def SecondaryTaskBarLoop(self):
        def callback():
            while self.running:
                try:
                    self.CenterSecondary()
                except: pass
                
                time.sleep(self.interval)

        self.threads[1] = Thread(target=callback)
        self.threads[1].start()


    def detect_secondary(self):
        return bool(self.Shell_SecondaryTrayWnd) 


    def StylingLoop(self):
        if self.style_func:
            delay = 1/self.fps
            while self.running:
                self.style_func()
                time.sleep(delay)