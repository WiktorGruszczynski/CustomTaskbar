import time
import win32
import uiautomation
import winreg


BUTTON = 0xc350
MENU_ITEM = 0xc35b
VREFRESH = 0x74

SCREEN = win32.GetSystemMetrics(0), win32.GetSystemMetrics(1)
ADVANCED = "SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced"


def GetMonitorFrequency():
    hdc = win32.GetDC(0)
    frequency = win32.GetDeviceCaps(hdc, VREFRESH)
    win32.ReleaseDC(hdc)
    return frequency

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


def win11_center(value:bool):
    SetRegistryValue(ADVANCED, "TaskbarAl", int(value))

class Window:
    def __init__(self, name:str=None, class_name:str=None, hwnd:int=None) -> None:
        if not hwnd:
            hwnd = win32.FindWindow(class_name, name)

        self.name = name
        self.class_name = class_name
        self.hwnd=hwnd

    @property
    def rect(self):
        return win32.GetWindowRect(self.hwnd)


    def child(self, window_name=None, class_name=None):
        ChildHwnd = win32.FindWindowEx(self.hwnd, None, class_name, window_name)
        name = win32.GetWindowText(ChildHwnd)
        class_name = win32.GetClassName(ChildHwnd)
        return Window(name, class_name, ChildHwnd)


class TaskbarCenter:
    def __init__(self, animation=False, speed=50, offset=0) -> None:
        self.animation = animation
        self.speed = speed
        self.offset=offset
        self.GetFPS()
        self.load_handles()
        self.current_orientation = None

        if self.speed == 0:
            self.speed = 1

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
        
        win32.SendMessage(self.ReBarWindow32.hwnd, win32.WM_REPAINT, False, 0)

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
                win32.SetWindowPos(handle, round((i+1)/frames*deltaX)-rect[0]+icons_rect[0], y, 0, 0, flags=win32.SWP_NOSIZE)
                while time.time()<timings[i]:   
                    pass
                
        
        elif deltaY!=0 and x==0:
            frames = self.n_frames(deltaY)
            if deltaY>SCREEN[1]/5:
                frames = int(frames/4)+1

            start = time.time()
            timings = [start+(self.frametime*(i+1)) for i in range(frames)]
        
            for i in range(frames):
                win32.SetWindowPos(handle, x, round((i+1)/frames*deltaY)-rect[1]+icons_rect[1], 0, 0, flags=win32.SWP_NOSIZE)
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
        


        self.current_orientation = self.orientation
        if self.orientation == "horizontal":    
            x = self.Xcenter(control)+self.offset
            deltaX = x-icons_rect[0]
            if deltaX!=0 and abs(deltaX)>2:
                if not self.animation:
                    win32.SetWindowPos(handle, x-taskrect[0]+AdjustX, 0, 0, 0, flags=win32.SWP_NOSIZE)
                else:
                    self.AnimateMovement(handle, x+AdjustX, 0, taskrect, icons_rect)
        else:
            y = self.Ycenter(self.control)+self.offset
            deltaY = y-icons_rect[1]

            if deltaY!=0 and abs(deltaY)>2:
                if not self.animation:
                    win32.SetWindowPos(handle, 0, y+AdjustY-taskrect[1], 0, 0, win32.SWP_NOSIZE)
                else:      
                    self.AnimateMovement(handle, 0, y+AdjustY, taskrect, icons_rect)
    

    def CenterPrimary(self):
        self.center(self.MSTaskSwWClass, self.MSTaskListWClass, self.control)


    def CenterSecondary(self):
        self.center(self.workew, self.MSTaskListWClass_2, self.control_2, MonitorAdjustment=True)


