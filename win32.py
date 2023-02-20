import ctypes
from ctypes.wintypes import DWORD, RECT


user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32


SWP_ASYNCWINDOWPOS = 0x4000
SWP_NOSIZE = 0x0001

WM_PAINT = 15
WM_REPAINT = 11

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 3
INVALID_HANDLE_VALUE = -1

PIPE_ACCESS_DUPLEX = 0x00000003
PIPE_TYPE_MESSAGE = 0x00000004
PIPE_WAIT = 0x00000000
INVALID_HANDLE_VALUE = -1




class ACCENTPOLICY(ctypes.Structure):
    _fields_ = [('nAccentState', DWORD),
                ('nFlags', DWORD),
                ('nColor', DWORD),
                ('nAnimationId', DWORD)]


class WINCOMPATTRDATA(ctypes.Structure):
    _fields_ = [('nAttribute', DWORD),
                ('pData', ctypes.POINTER(ACCENTPOLICY)),
                ('ulDataSize', DWORD)]

class SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ('nLength', ctypes.c_ulong),
        ('lpSecurityDescriptor', ctypes.c_void_p),
        ('bInheritHandle', ctypes.c_bool)
    ]


def FindWindow(class_name:str=None, window_name:str=None) -> int:
    return user32.FindWindowW(class_name, window_name)


def FindWindowEx(parent_hwnd:int, child_after:int, class_name:str=None, window_name:str=None) -> int:
    return user32.FindWindowExW(parent_hwnd, child_after, class_name, window_name)


def GetWindowRect(handle:int):
    rect = RECT()
    user32.GetWindowRect(handle, ctypes.byref(rect))
    return (rect.left, rect.top, rect.right, rect.bottom)


def SetWindowPos(hwnd:int, x:int, y:int, width:int, height:int, flags=SWP_ASYNCWINDOWPOS, insert_after=0):
    return user32.SetWindowPos(hwnd, insert_after, x, y, width, height, flags)


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


def GetDC(hwnd:int=None) -> int:
    return user32.GetDC(hwnd)


def ReleaseDC(hdc:int):
    return user32.ReleaseDC(None, hdc)


def SendMessage(hwnd:int, idMessage:int, wparam, lparam):
    return user32.SendMessageW(hwnd, idMessage, wparam, lparam)


def ShowWindow(hwnd, flags):
    return user32.ShowWindow(hwnd, flags)


def SetWindowCompositionAttribute(handle:int, wincompattrdata:WINCOMPATTRDATA):
    user32.SetWindowCompositionAttribute(handle, ctypes.byref(wincompattrdata))


def GetDeviceCaps(hdc:int, index:int) -> int:
    return gdi32.GetDeviceCaps(hdc, index)


def CreateNamedPipe(PipeName:str, OpenMode:int, PipeMode:int, MaxInstances:int, OutBufferSize:int, InBufferSize:int, Timeout:int=0, SecurityAttributes:SECURITY_ATTRIBUTES=None):
    return kernel32.CreateNamedPipeW(PipeName, OpenMode, PipeMode, MaxInstances, OutBufferSize, InBufferSize, Timeout, SecurityAttributes)


def ConnectNamedPipe(handle:int, lparam):
    return kernel32.ConnectNamedPipe(handle, None)


def CreateFile(PipeName:str, acces:int, sharemode:int, SecurityAtributes:SECURITY_ATTRIBUTES, CreationDisposition:int, flags:int, templatefile):
    return kernel32.CreateFileW(PipeName, acces, sharemode, SecurityAtributes, CreationDisposition, flags, templatefile)


def WriteFile(handle:int, message:bytes):
    kernel32.WriteFile(handle, message, len(message), ctypes.byref(ctypes.c_ulong(0)), None)


def ReadFile(handle:int, buffer_len:int, overlapped=None) -> bytes:
    buffer = ctypes.create_string_buffer(buffer_len)
    kernel32.ReadFile(handle, buffer, ctypes.sizeof(buffer), ctypes.c_ulong(0), overlapped)
    return buffer.value


def FlushFileBuffers(handle:int):
    kernel32.FlushFileBuffers(handle)


def DisconnectNamedPipe(handle:int):
    kernel32.DisconnectNamedPipe(handle)


def CloseHandle(handle:int):
    kernel32.CloseHandle(handle)