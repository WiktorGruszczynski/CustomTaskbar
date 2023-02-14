from threading import Thread
import uiautomation
import winreg
import process
import platform
import winapi
import time


BUTTON = 0xc350
SCREEN = winapi.GetSystemMetrics(0), winapi.GetSystemMetrics(1)
ADVANCED = "SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
DEAFULT_SPEED = 50
OS_NAME = f"{platform.system()} {platform.release()}"



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




class TaskbarCenter:
    def __init__(self, animation=False, speed=DEAFULT_SPEED) -> None:
        self.animation = animation
        self.speed = speed
        self.frames = 100
        self.load_handles()


    def load_handles(self):
        self.Shell_TrayWnd = Window(class_name="Shell_TrayWnd")
        self.Shell_SecondaryTrayWnd = Window(class_name="Shell_SecondaryTrayWnd")
        self.ReBarWindow32 = self.Shell_TrayWnd.child(class_name="ReBarWindow32")
        self.MSTaskSwWClass = self.ReBarWindow32.child(class_name="MSTaskSwWClass")
        self.MSTaskListWClass = self.MSTaskSwWClass.child(class_name="MSTaskListWClass")
        self.StartButton = self.Shell_TrayWnd.child(class_name="Start")
        self.control = uiautomation.ControlFromHandle(self.MSTaskListWClass.hwnd)
        
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

    def clickable(self, elements):
        for e in elements:
            isclickable = e.GetClickablePoint()[2]
            if isclickable == False:
                return False
        return True

    def icons(self, control) -> list[uiautomation.Control]:
        icons = control.GetChildren()
        icons = [i for i in icons if i.ControlType == BUTTON]

        if self.clickable(icons) == False:
            return self.icons(control)

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

    def CalcDelay(self, distance):
        delay = (distance/self.speed)/1000
        if delay<0:
            delay = -delay
        return delay


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


    def AnimateMovement(self, handle, x, y, rect, icons_rect):
        deltaX = x-icons_rect[0]
        deltaY = y-icons_rect[1]
        width = rect[2]-rect[0]
        height = rect[3]-rect[1]

        if deltaX!=0 and y==0:
            delay = self.CalcDelay(deltaX)
            start = time.time()
            timings = [start+(delay*i) for i in range(1, self.frames+1)]

            for i in range(1, self.frames+1):
                winapi.SetWindowPos(handle, round(i/self.frames*deltaX)-rect[0]+icons_rect[0], y, width, height)
                while time.time()<timings[i-1]:   
                    pass
        
        elif deltaY!=0 and x==0:
            delay = self.CalcDelay(deltaY)
            start = time.time()
            timings = [start+(delay*i) for i in range(1, self.frames+1)]

            for i in range(1, self.frames+1):
                winapi.SetWindowPos(handle, x, round(i/self.frames*deltaY)-rect[1]+icons_rect[1], width, height)
                print(i)
                while time.time()<timings[i-1]:   
                    pass

    def center(self, taskbar:Window, tasklist:Window, control, MonitorAdjustment=False):
        if OS_NAME == "Windows 11":
            pass
        else:
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
                x = self.Xcenter(control)
                deltaX = x-icons_rect[0]

                if deltaX!=0:
                    if not self.animation:
                        winapi.SetWindowPos(handle, x-taskrect[0], 0, taskrect[2]-taskrect[0]+AdjustX, taskrect[3]-taskrect[1])
                    else:
                        self.AnimateMovement(handle, x+AdjustX, 0, taskrect, icons_rect)
            else:
                y = self.Ycenter(self.control)
                deltaY = y-icons_rect[1]

                if deltaY!=0:
                    if not self.animation:
                        winapi.SetWindowPos(handle, x-taskrect[0], 0, taskrect[2]-taskrect[0]+AdjustY, taskrect[3]-taskrect[1])
                    else:
                        self.AnimateMovement(handle, 0, y+AdjustY, taskrect, icons_rect)
    
    def CenterPrimary(self):
        self.center(self.MSTaskSwWClass, self.MSTaskListWClass, self.control)

    def CenterSecondary(self):
        self.center(self.workew, self.MSTaskListWClass_2, self.control_2, MonitorAdjustment=True)
    
   
if __name__ == "__main__":
    task=TaskbarCenter(animation=True, speed=50)

    def loop_primary():
        while True:
            try:
                task.CenterPrimary()
            except:
                task.load_handles()

    def loop_secondary():
        while True:
            try:
                task.CenterSecondary()
            except:
                pass

    primary=Thread(target=loop_primary)
    secondary=Thread(target=loop_secondary)

    primary.start()
    secondary.start() 
