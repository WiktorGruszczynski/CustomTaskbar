import uiautomation 
import winapi
import time
import winreg
import process
from threading import Thread


BUTTON = 0xc350
SCREEN = (winapi.GetSystemMetrics(0), winapi.GetSystemMetrics(1))
ADVANCED = "SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
DEAFULT_SPEED = 50

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


    def clickable(self, elements):
        for e in elements:
            isclickable = e.GetClickablePoint()[2]
            if isclickable == False:
                return False
        return True


    def icons(self, control) -> list[uiautomation.Control]:
        icons = control.GetChildren()
        icons = [i for i in icons if i.ControlType == BUTTON]
        zeros = [i for i in [icon.BoundingRectangle.width() for icon in icons] if i == 0]

        if zeros != []:
            return self.icons(control)

        if self.clickable(icons) == False:
            return self.icons(control)

        StartBtnRect = self.StartButton.rect
        Startbtn = StartBtnRect[2]-StartBtnRect[0], StartBtnRect[3]-StartBtnRect[1]

        for i, icon in enumerate(icons):
            if icon.BoundingRectangle.width()<Startbtn[0] or icon.BoundingRectangle.height()<Startbtn[1]:
                icons.pop(i)
                break
        
        return icons 


    def icons_width(self, control):
        icons = self.icons(control)
        left = icons[0].BoundingRectangle.left
        right = icons[-1].BoundingRectangle.right
        return right-left


    def icons_height(self, control):    
        icons = self.icons(control)
        top = icons[0].BoundingRectangle.top
        bot = icons[-1].BoundingRectangle.bottom
        return bot-top

    def Xcenter(self, control):
        return (SCREEN[0]-self.icons_width(control))//2

    def Ycenter(self, control):
        return (SCREEN[1]-self.icons_height(control))//2


    def CenterPrimary(self):
        rect = self.MSTaskSwWClass.rect
        width = rect[2]-rect[0]
        height = rect[3]-rect[1]
        icons_rect = self.MSTaskListWClass.rect

        if self.orientation == "horizontal":
            x = self.Xcenter(self.control)
            deltaX = x-icons_rect[0]

            if deltaX!=0:
                if not self.animation:
                    winapi.SetWindowPos(self.MSTaskListWClass.hwnd, x-rect[0], 0, width, height)
                else:
                    delay = (deltaX/self.speed)/1000
                    if delay<0:
                        delay = -delay

                    start = time.time()
                    timings = [start+(delay*i) for i in range(1, self.frames+1)]

                    for i in range(1, self.frames+1):
                        winapi.SetWindowPos(self.MSTaskListWClass.hwnd, round(i/self.frames*deltaX)-rect[0]+icons_rect[0], 0, width, height)
                        while time.time()<timings[i-1]:   
                            pass
                     
        else:
            y = self.Ycenter(self.control)
            deltaY = y-icons_rect[1]
            if deltaY!=0:
                if not self.animation:
                    winapi.SetWindowPos(self.MSTaskListWClass.hwnd, 0, y-rect[1], width, height)
                else:
                    delay = (deltaY/self.speed)/1000
                    if delay<0:
                        delay = -delay

                    start = time.time()
                    timings = [start+(delay*i) for i in range(1, self.frames+1)]

                    for i in range(1, self.frames+1):
                        winapi.SetWindowPos(self.MSTaskListWClass.hwnd, 0, round(i/self.frames*deltaY)-rect[1]+icons_rect[1], width, height)
                        while time.time()<timings[i-1]:   
                            pass

    def CenterSecondary(self):
        rect = self.workew.rect
        width = rect[2]-rect[0]
        height = rect[3]-rect[1]
        icons_rect = self.MSTaskListWClass_2.rect
        PrimaryTaskbarRect = self.Shell_TrayWnd.rect
        SecondaryTaskbarRect = self.Shell_SecondaryTrayWnd.rect
        

        if self.orientation == "horizontal":
            x = self.Xcenter(self.control_2)
            monitor_adjustment = SecondaryTaskbarRect[0]-PrimaryTaskbarRect[0]
            deltaX = x-icons_rect[0]+monitor_adjustment

            if deltaX!=0:
                if not self.animation:
                    winapi.SetWindowPos(self.MSTaskListWClass_2.hwnd, x-rect[0]+monitor_adjustment, 0, width, height)
                else:
                    delay = (deltaX/self.speed)/1000
                    if delay<0:
                        delay = -delay

                    start = time.time()
                    timings = [start+(delay*i) for i in range(1, self.frames+1)]

                    for i in range(1, self.frames+1):
                        x = round(i/self.frames*deltaX)-rect[0]+icons_rect[0]
                        winapi.SetWindowPos(self.MSTaskListWClass_2.hwnd, x, 0, width, height) 
                        while time.time()<timings[i-1]:   
                            pass
  
            
        else:
            y = self.Ycenter(self.control_2)
            monitor_adjustment = SecondaryTaskbarRect[1]-PrimaryTaskbarRect[1]
            deltaY = y-icons_rect[1]+monitor_adjustment

            if deltaY!=0:
                if not self.animation:
                    winapi.SetWindowPos(self.MSTaskListWClass_2.hwnd, 0, y-rect[1]+monitor_adjustment, width, height)
                else:
                    delay = (deltaY/self.speed)/1000
                    if delay<0:
                        delay = -delay

                    start = time.time()
                    timings = [start+(delay*i) for i in range(1, self.frames+1)]

                    for i in range(1, self.frames+1):
                        y = round(i/self.frames*deltaY)-rect[1]+icons_rect[1]
                        winapi.SetWindowPos(self.MSTaskListWClass_2.hwnd, 0, y, width, height)
                        while time.time()<timings[i-1]:   
                            pass



if __name__ == "__main__":
    task=TaskbarCenter(animation=True,speed=50)

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

