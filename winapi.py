import ctypes
from ctypes.wintypes import RECT


user32 = ctypes.windll.user32


def FindWindow(class_name:str=None, window_name:str=None) -> int:
    return user32.FindWindowW(class_name, window_name)


def FindWindowEx(parent_hwnd:int, child_after:int, class_name:str=None, window_name:str=None) -> int:
    return user32.FindWindowExW(parent_hwnd, child_after, class_name, window_name)


def GetWindowRect(handle:int):
    rect = RECT()
    user32.GetWindowRect(handle, ctypes.byref(rect))
    return (rect.left, rect.top, rect.right, rect.bottom)


def MoveWindow(hwnd:int, x:int, y:int, width:int, height:int, repaint:bool):
     user32.MoveWindow(hwnd, x, y, width, height, repaint)


def SetWindowPos(hwnd:int, x:int, y:int, width:int, height:int, flags=0x4000):
    user32.SetWindowPos(hwnd, 0, x, y, width, height, flags)


def GetClassName(handle:int):
    class_name = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(handle, class_name, ctypes.sizeof(class_name))
    return class_name.value


def getWindowText(hwnd:int):
    length = user32.GetWindowTextLengthW(hwnd)
    title = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, title, length + 1)
    return title.value


def IsWindowVisible(handle:int):
    return user32.IsWindowVisible(handle)


def EnumWindows(callback, param=None):
    user32.EnumWindows(callback, param)


def GetSystemMetrics(index:int):
    return user32.GetSystemMetrics(index)