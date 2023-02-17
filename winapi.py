import ctypes
from ctypes.wintypes import RECT


user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

HWND_BOTTOM = 1
SWP_ASYNCWINDOWPOS = 0x4000

def FindWindow(class_name:str=None, window_name:str=None) -> int:
    return user32.FindWindowW(class_name, window_name)


def FindWindowEx(parent_hwnd:int, child_after:int, class_name:str=None, window_name:str=None) -> int:
    return user32.FindWindowExW(parent_hwnd, child_after, class_name, window_name)


def GetWindowRect(handle:int):
    rect = RECT()
    user32.GetWindowRect(handle, ctypes.byref(rect))
    return (rect.left, rect.top, rect.right, rect.bottom)


def SetWindowPos(hwnd:int, x:int, y:int, width:int, height:int, flags=SWP_ASYNCWINDOWPOS, insert_after=HWND_BOTTOM):
    user32.SetWindowPos(hwnd, insert_after, x, y, width, height, flags)


def GetClassName(handle:int) -> str:
    class_name = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(handle, class_name, ctypes.sizeof(class_name))
    return class_name.value


def GetWindowText(hwnd:int) -> str:
    length = user32.GetWindowTextLengthW(hwnd)
    title = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, title, length + 1)
    return title.value


def GetSystemMetrics(index:int) -> int:
    return user32.GetSystemMetrics(index)


def GetDC(_NamedFuncPointer=None):
    return user32.GetDC(_NamedFuncPointer)


def ReleaseDC(hdc):
    user32.ReleaseDC(None, hdc)


def GetDeviceCaps(hdc:int, index:int) -> int:
    return gdi32.GetDeviceCaps(hdc, index)

