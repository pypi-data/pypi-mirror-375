from colorama import Fore, Back
from enum import Enum, auto
import time
import os
import inspect


class LogLevel(Enum):
    CRITICAL = 1
    ERROR = 2
    WARN = 3
    INFO = 4
    DEBUG = 5
    TRACE = 6

class Log():
    def __init__(self, level: LogLevel, logMs:bool = True, logCaller:bool = True):
        self.clear()
        self.level = level
        self.startTime = time.time()
        self.logMs = logMs
        self.logCaller = logCaller

    def clear(self):
        for i in range(100):
            print(Fore.WHITE + Back.BLACK)

    def c(self, inputStr):
        if self.level.value >= LogLevel.CRITICAL.value:
            print(Fore.RED + Back.WHITE + self.getRunTimeAsStr() +  "[CRITICAL]" + self._get_caller_name() + inputStr + Back.BLACK + Fore.WHITE)

    def e(self, inputStr): 
        if self.level.value >= LogLevel.ERROR.value:
            print(Fore.RED + Back.BLACK + self.getRunTimeAsStr() +  "[ERROR   ]" + self._get_caller_name() + inputStr + Back.BLACK + Fore.WHITE)

    def w(self, inputStr):
        if self.level.value >= LogLevel.WARN.value:
            print(Fore.YELLOW + Back.BLACK + self.getRunTimeAsStr() +  "[WARN    ]" + self._get_caller_name() + inputStr + Back.BLACK + Fore.WHITE)

    def i(self, inputStr):
        if self.level.value >= LogLevel.INFO.value:
            print(Fore.GREEN + Back.BLACK + self.getRunTimeAsStr() + "[INFO    ]" + self._get_caller_name() + inputStr + Back.BLACK + Fore.WHITE)

    def d(self, inputStr):
        if self.level.value >= LogLevel.DEBUG.value:
            print(Fore.BLUE + Back.BLACK + self.getRunTimeAsStr() +  "[DEBUG   ]" +  self._get_caller_name() +  inputStr + Back.BLACK + Fore.WHITE)

    def t(self, inputStr):
        if self.level.value >= LogLevel.TRACE.value:
            print(Fore.CYAN + Back.BLACK + self.getRunTimeAsStr()  + "[TRACE   ]" + self._get_caller_name() + inputStr + Back.BLACK + Fore.WHITE)

    def getRunTimeAsStr(self):
        if self.logMs == False:
            return ""
        
        microseconds = (time.time() - self.startTime) * 1_000_000
        return f"[{microseconds:010.0f}]"

    def _get_caller_name(self):
        if self.logCaller == False:
            return ""
        frame = inspect.currentframe().f_back.f_back
        filename = frame.f_code.co_filename
        return "[" + os.path.splitext(os.path.basename(filename))[0] +"] "


if __name__ == "__main__":
    Log = Log(LogLevel.TRACE)
    Log.clear()
    Log.c("This is a critical message")
    Log.e("This is an error message")
    Log.w("This is a warning message")
    Log.i("This is an info message")
    Log.d("This is a debug message")
    Log.t("This is a trace message")






