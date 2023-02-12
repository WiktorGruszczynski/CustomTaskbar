import uiautomation as auto
import winapi
import time
import winreg
import process


SCREEN = (winapi.GetSystemMetrics(0), winapi.GetSystemMetrics(1))
ADVANCED = "SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced"


def apply():
    pid = process.find("explorer.exe")[1]
    process.refresh(pid)

def opacity(value:int):
    registry = winreg.OpenKey(winreg.HKEY_CURRENT_USER, ADVANCED, 0, access=winreg.KEY_ALL_ACCESS)
    key = "TaskbarAcrylicOpacity"
    values = []

    for i in range(1024):
        try:
            values.append(winreg.EnumValue(registry, i))
        except: break

    if not "TaskbarAcrylicOpacity" in [i[0] for i in values]:
        winreg.CreateKey(registry, key)

    winreg.SetValueEx(registry, key, 0, winreg.REG_DWORD, value)




class Window:
    def __init__(self, name:str=None, class_name:str=None, hwnd:int=None) -> None:
        self.name = name
        self.class_name = class_name

        if not hwnd:
            hwnd = winapi.FindWindow(class_name, name)

        self.hwnd=hwnd

    @property
    def rect(self):
        return winapi.GetWindowRect(self.hwnd)

    def child(self, window_name=None, class_name=None):
        ChildHwnd = winapi.FindWindowEx(self.hwnd, None, class_name, window_name)
        name = winapi.getWindowText(ChildHwnd)
        class_name = winapi.GetClassName(ChildHwnd)
        return Window(name, class_name, ChildHwnd)





class TaskbarCenter:
    def __init__(self, animation=False) -> None:
        self.animation = animation
        self.Shell_TrayWnd = Window(class_name="Shell_TrayWnd")
        self.Shell_SecondaryTrayWnd = Window(class_name="Shell_SecondaryTrayWnd")
        self.ReBarWindow32 = self.Shell_TrayWnd.child(class_name="ReBarWindow32")
        self.MSTaskSwWClass = self.ReBarWindow32.child(class_name="MSTaskSwWClass")
        self.MSTaskListWClass = self.MSTaskSwWClass.child(class_name="MSTaskListWClass")
        self.control = auto.ControlFromHandle(self.MSTaskListWClass.hwnd)

        
        if self.Shell_SecondaryTrayWnd:
            self.workew = self.Shell_SecondaryTrayWnd.child(class_name="WorkerW")
            self.MSTaskListWClass_2 = self.workew.child(class_name="MSTaskListWClass")


    def icons(self):
        icons = self.control.GetChildren()
        zeros = [i for i in [icon.BoundingRectangle.width() for icon in icons] if i == 0]

        if zeros != []:
            return self.icons()
        else:
            return icons 

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
    def icons_width(self):
        icons = self.icons()
        left = icons[0].BoundingRectangle.left
        right = icons[-2].BoundingRectangle.right
        return right-left


    @property 
    def icons_height(self):    
        icons = self.icons()
        top = icons[0].BoundingRectangle.top
        bot = icons[-2].BoundingRectangle.bottom
        return bot-top

    def centerX(self):
        return (SCREEN[0]-self.icons_width)//2


    def centerY(self):
        return (SCREEN[1]-self.icons_height)//2



    def center(self):
        rect = self.MSTaskListWClass.rect
        width = rect[2]-rect[0]
        height = rect[3]-rect[1]
        startX, startY, _, __ = self.MSTaskSwWClass.rect

        if self.orientation ==  "horizontal":
            x, y = self.centerX()-startX, 0
        else:
            x, y = 0, self.centerY()-startY
        
        curX, curY, _, _ = self.MSTaskListWClass.rect


        deltaX = x-curX+startX
        deltaY = y-curY+startY


        if deltaY!=0 or deltaX!=0:
            hwnd = self.MSTaskListWClass.hwnd
            if not self.animation:
                winapi.SetWindowPos(hwnd, x, y, width, height)
            else:
                fps = 60
                speed = 0.5
                sleep_time = ((((deltaX-deltaY)**2)**.5))/100000*speed

                for i in range(1,fps+1):
                    x = round((i/fps)*deltaX)+curX-startX
                    y = round((i/fps)*deltaY)+curY-startY
                    
                    winapi.SetWindowPos(hwnd, x, y, width, height)
                    time.sleep(sleep_time)

            
        

