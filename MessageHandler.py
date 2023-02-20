import time
import win32
import ctypes
from win32 import *


pipe = r'\\.\pipe\my_pipe'


class Listener:
    def __init__(self, pipe_name:str) -> None:
        self.pipe_name:str = pipe_name
        self.message:str = None

    def listen(self):
        security = SECURITY_ATTRIBUTES(ctypes.sizeof(SECURITY_ATTRIBUTES), None, True)
        handle = win32.CreateNamedPipe(self.pipe_name,  PIPE_ACCESS_DUPLEX, PIPE_TYPE_MESSAGE | PIPE_WAIT, 1, 65536, 65536, 0, ctypes.byref(security))

        while True:
            if win32.ConnectNamedPipe(handle, None):
                data = win32.ReadFile(handle, 4096)
                if data:
                    self.message = data.decode(encoding="utf-8")

                win32.FlushFileBuffers(handle)
                win32.DisconnectNamedPipe(handle)
                
    
            time.sleep(0.1)


def SendMessage(pipe_name, message):
    handle = win32.CreateFile(pipe_name, GENERIC_READ | GENERIC_WRITE, 0, None, OPEN_EXISTING, 0, None)

    if handle == INVALID_HANDLE_VALUE:
        exit(1)

    win32.WriteFile(handle, message)
    win32.CloseHandle(handle)
    

