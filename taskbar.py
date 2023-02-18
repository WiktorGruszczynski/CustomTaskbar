from threading import Thread
import uiautomation
import platform
import winreg
import ctypes
import winapi
import time
import os



config_path = ".cfg"
deafult_config = [
    'animation=True',
    'align_center=True',
    'align_primary=True',
    'align_secondary=True',
    'refresh_rate=0.2',
    'speed=200',
    'offset=0']


BUTTON = 0xc350
MENU_ITEM = 0xc35b
VREFRESH = 0x74

SCREEN = winapi.GetSystemMetrics(0), winapi.GetSystemMetrics(1)
OS_NAME = f"{platform.system()} {platform.release()}"

ADVANCED = "SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
THEMES = "SOFTWARE\Microsoft\Windows\CurrentVersion\Themes"




class Window:
    def __init__(self, name:str=None, class_name:str=None, hwnd:int=None) -> None:
        if not hwnd:
            hwnd = winapi.FindWindow(class_name, name)

        self.name = name
        self.class_name = class_name
        self.hwnd=hwnd

    @property
    def rect(self):
        return winapi.GetWindowRect(self.hwnd)

    def child(self, window_name=None, class_name=None):
        ChildHwnd = winapi.FindWindowEx(self.hwnd, None, class_name, window_name)
        name = winapi.GetWindowText(ChildHwnd)
        class_name = winapi.GetClassName(ChildHwnd)
        return Window(name, class_name, ChildHwnd)


def GetMonitorFrequency():
    hdc = winapi.GetDC(0)
    frequency = winapi.GetDeviceCaps(hdc, VREFRESH)
    winapi.ReleaseDC(hdc)
    return frequency


def apply():
    process.refresh(pid=process.find("explorer.exe")[1])


def EnumRegistryValues(WinregObject):
    values = []
    for i in range(1024):
        try:
            values.append(winreg.EnumValue(WinregObject, i))
        except: 
            break
    return values
    

def SetRegistryValue(key, subkey, value, wtype=winreg.REG_DWORD):
    registry = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, access=winreg.KEY_ALL_ACCESS)
    values = EnumRegistryValues(registry)

    if not subkey in [i[0] for i in values]:
        winreg.CreateKey(registry, subkey)

    winreg.SetValueEx(registry, subkey, 0, wtype, value)


def enable_transparency():
    SetRegistryValue(THEMES+"\\Personalize", "EnableTransparency", int(True))

def disable_transparency():
    SetRegistryValue(THEMES+"\\Personalize", "EnableTransparency", int(False))



def win_button(hidden=False, index=0):
    if index == 0:
        class_name = "Shell_TrayWnd"
    elif index == 1:
        class_name = "Shell_SecondaryTrayWnd"
    else: return None

    taskbar = Window(class_name=class_name) 
    windows_button = taskbar.child("Start")
    winapi.SetWindowPos(windows_button.hwnd, taskbar.rect[0] - windows_button.rect[0], int(hidden)*10000, 0, 0, flags=winapi.SWP_NOSIZE)
    


def win11_center(value:bool):
    SetRegistryValue(ADVANCED, "TaskbarAl", int(value))


class TaskbarStyle:
    def __init__(self) -> None:
        self.style = None
        self.handle = Window(class_name="Shell_TrayWnd").hwnd
        self.secondary_handle = Window(class_name="Shell_SecondaryTrayWnd").hwnd
        
    #blur 3 #transparent 6
    def set_style(self, style:int):
        accent_policy = winapi.ACCENTPOLICY(style, 0, 0, 0)
        data = winapi.WINCOMPATTRDATA(19, ctypes.pointer(accent_policy), ctypes.sizeof(accent_policy))
        winapi.SetWindowCompositionAttribute(self.handle, data)
        if self.secondary_handle:
            winapi.SetWindowCompositionAttribute(self.secondary_handle, data)


class TaskbarCenter:
    def __init__(self, animation=False, speed=50, offset=0) -> None:
        self.animation = animation
        self.speed = speed
        self.offset=offset
        self.GetFPS()
        self.load_handles()


    def GetFPS(self):
        try:
            self.fps = GetMonitorFrequency()
            self.frametime = 1/self.fps
        except:
            time.sleep(0.5)
            return self.GetFPS()


    def load_handles(self):
        self.Shell_TrayWnd = Window(class_name="Shell_TrayWnd")
        self.StartButton = self.Shell_TrayWnd.child(class_name="Start")
        self.Shell_SecondaryTrayWnd = Window(class_name="Shell_SecondaryTrayWnd")
        self.ReBarWindow32 = self.Shell_TrayWnd.child(class_name="ReBarWindow32")
        self.MSTaskSwWClass = self.ReBarWindow32.child(class_name="MSTaskSwWClass")
        self.MSTaskListWClass = self.MSTaskSwWClass.child(class_name="MSTaskListWClass")
        self.control = uiautomation.ControlFromHandle(self.MSTaskListWClass.hwnd)
        
        winapi.SendMessage(self.ReBarWindow32.hwnd, winapi.WM_REPAINT, False, 0)

        if self.Shell_SecondaryTrayWnd:
            self.workew = self.Shell_SecondaryTrayWnd.child(class_name="WorkerW")
            self.MSTaskListWClass_2 = self.workew.child(class_name="MSTaskListWClass")
            self.control_2 = uiautomation.ControlFromHandle(self.MSTaskListWClass_2.hwnd)


    @property
    def orientation(self):
        rect = self.Shell_TrayWnd.rect
        width = rect[2]-rect[0]
        height = rect[3]-rect[1]
        if width>height:
            return "horizontal"
        else:
            return "vertical"

    @property
    def StartButtonSize(self):
        StartBtnRect = self.StartButton.rect
        return (StartBtnRect[2]-StartBtnRect[0], StartBtnRect[3]-StartBtnRect[1])


    def icons(self, control) -> list[uiautomation.Control]:
        icons:list[uiautomation.Control] = control.GetChildren()
        icons = [i for i in icons if i.ControlType == BUTTON or i.ControlType == MENU_ITEM]
        return icons 

    def icons_width(self, control):
        icons = self.icons(control)
    
        left = icons[0].BoundingRectangle.left
        right = icons[-1].BoundingRectangle.right

        btn = self.StartButtonSize[0]
        for icon in icons:
            icon_width = icon.BoundingRectangle.width()
            if icon_width<btn and right-left>0:
                return right-left-icon_width

        return right-left

    def icons_height(self, control):    
        icons = self.icons(control)
        top = icons[0].BoundingRectangle.top
        bot = icons[-1].BoundingRectangle.bottom

        btn = self.StartButtonSize[1]
        for icon in icons:
            icon_height = icon.BoundingRectangle.height()
            if icon_height<btn and bot-top>0:
                return bot-top-icon_height

        return bot-top


    def Xcenter(self, control):
        x = self.icons_width(control)

        if x<0:
            return self.Xcenter(control)
        return (SCREEN[0]-x)//2


    def Ycenter(self, control):
        y = self.icons_height(control)
        if y<0:
            return self.Ycenter(control)
        return (SCREEN[1]-y)//2


    def n_frames(self, distance):
        return round(abs(distance)*self.fps/self.speed)


    def AnimateMovement(self, handle, x, y, rect, icons_rect):
        deltaX = x-icons_rect[0]
        deltaY = y-icons_rect[1]

        if deltaX!=0 and y==0:  
            frames = self.n_frames(deltaX)
            if deltaX>SCREEN[0]/5:
                frames = int(frames/4)+1

            start = time.time()
            timings = [start+(self.frametime*(i+1)) for i in range(frames)]

            for i in range(frames):
                winapi.SetWindowPos(handle, round((i+1)/frames*deltaX)-rect[0]+icons_rect[0], y, 0, 0, flags=winapi.SWP_NOSIZE)
                while time.time()<timings[i]:   
                    pass
                
        
        elif deltaY!=0 and x==0:
            frames = self.n_frames(deltaY)
            if deltaY>SCREEN[1]/5:
                frames = int(frames/4)+1

            start = time.time()
            timings = [start+(self.frametime*(i+1)) for i in range(frames)]
        
            for i in range(frames):
                winapi.SetWindowPos(handle, x, round((i+1)/frames*deltaY)-rect[1]+icons_rect[1], 0, 0, flags=winapi.SWP_NOSIZE)
                while time.time()<timings[i]:   
                    pass

    def center(self, taskbar:Window, tasklist:Window, control, MonitorAdjustment=False):
        taskrect = taskbar.rect
        icons_rect = tasklist.rect
        handle = tasklist.hwnd

        if MonitorAdjustment:
            PrimaryTaskbarRect = self.Shell_TrayWnd.rect
            SecondaryTaskbarRect = self.Shell_SecondaryTrayWnd.rect
            AdjustX = SecondaryTaskbarRect[0]-PrimaryTaskbarRect[0]
            AdjustY = SecondaryTaskbarRect[1]-PrimaryTaskbarRect[1]
        else:
            AdjustX, AdjustY = 0,0
        

        if self.orientation == "horizontal":
            
            x = self.Xcenter(control)+self.offset
            deltaX = x-icons_rect[0]
            if deltaX!=0 and abs(deltaX)>2:
                if not self.animation:
                    winapi.SetWindowPos(handle, x-taskrect[0]+AdjustX, 0, 0, 0, flags=winapi.SWP_NOSIZE)
                else:
                    self.AnimateMovement(handle, x+AdjustX, 0, taskrect, icons_rect)
        else:
            y = self.Ycenter(self.control)+self.offset
            deltaY = y-icons_rect[1]

            if deltaY!=0 and abs(deltaY)>2:
                if not self.animation:
                    winapi.SetWindowPos(handle, 0, y+AdjustY-taskrect[1], 0, 0, winapi.SWP_NOSIZE)
                else:      
                    self.AnimateMovement(handle, 0, y+AdjustY, taskrect, icons_rect)
    

    def CenterPrimary(self):
        self.center(self.MSTaskSwWClass, self.MSTaskListWClass, self.control)


    def CenterSecondary(self):
        self.center(self.workew, self.MSTaskListWClass_2, self.control_2, MonitorAdjustment=True)



    
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



class TaskbarClient:
    def __init__(self) -> None:
        self.load_config()
        self.taskbar = TaskbarCenter(animation=self.animation, speed=self.speed, offset=self.offset)
        self.styler = TaskbarStyle()
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


    def load_config(self):
        config = ReadConfig()
        self.speed = config["speed"]
        self.animation = bool(config["animation"])
        self.align_center = bool(config["align_center"])
        self.align_primary = bool(config["align_primary"])
        self.align_secondary = bool(config["align_secondary"])
        self.interval = config["refresh_rate"]
        self.offset = config["offset"]


    def PrimaryTaskBarLoop(self):
        def callback():
            while self.running:
                try:
                    self.taskbar.CenterPrimary()
                except Exception as err:                 
                    self.taskbar.load_handles()

                time.sleep(self.interval)
        
        self.threads[0] = Thread(target=callback)
        self.threads[0].start()


    def SecondaryTaskBarLoop(self):
        def callback():
            while self.running:
                try:
                    self.taskbar.CenterSecondary()
                except: pass
                
                time.sleep(self.interval)

        self.threads[1] = Thread(target=callback)
        self.threads[1].start()

    def detect_secondary(self):
        return bool(self.taskbar.Shell_SecondaryTrayWnd) 


if __name__ == "__main__":
    TaskbarClient()
