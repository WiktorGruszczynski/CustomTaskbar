from taskbar.TaskbarCenter import Window
from taskbar import win32
import ctypes



class TaskbarStyler:
    def __init__(self) -> None:
        self.style = None
        self.handle = Window(class_name="Shell_TrayWnd").hwnd
        self.secondary_handle = Window(class_name="Shell_SecondaryTrayWnd").hwnd
   
    def set_style(self, style:int, nflags=0, ncolor=0, animationid=0):
        accent_policy = win32.ACCENTPOLICY(style, 0, 0, 0)
        data = win32.WINCOMPATTRDATA(19, ctypes.pointer(accent_policy), ctypes.sizeof(accent_policy))
        win32.SetWindowCompositionAttribute(self.handle, data)
        if self.secondary_handle:
            win32.SetWindowCompositionAttribute(self.secondary_handle, data)

    def blurred(self):
        self.set_style(3)

    def transparent(self):
        self.set_style(6)


def win_button(visible=True, index=0):
    if index == 0:
        class_name = "Shell_TrayWnd"
    elif index == 1:
        class_name = "Shell_SecondaryTrayWnd"
    else: return None

    taskbar = Window(class_name=class_name) 
    windows_button = taskbar.child("Start")
    win32.SetWindowPos(windows_button.hwnd, taskbar.rect[0] - windows_button.rect[0], int(abs(visible-1))*10000, 0, 0, flags=win32.SWP_NOSIZE)