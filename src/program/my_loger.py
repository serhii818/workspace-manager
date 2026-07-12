
from . import config

import os
from typing import Literal, List
from enum import Enum
from colorama import Fore, Back, Style

# ========================================================================================
if __name__ != "__main__": print("importing logger")

def whoami(obj : object) -> str:
    return obj.__class__.__name__


class LogType(Enum):
    INFO = 3
    WARNING = 2
    ERROR = 1
log_type_labels = ["", "error", "warning", "info"]
log_type_color = ["", Fore.RED, Fore.YELLOW, ""]



def dprint(
    *values: object,
    who : str | object = "",
    _type : LogType = LogType.INFO,
    sep: str | None = " ",
    end: str | None = "\n",
    file = None, # type: ignore
    flush: Literal[False] = False,
    ):
    if config.DEBUG_PRINT_LEVEL >= _type.value: 
        if not isinstance(who, str): who = whoami(who)
        print(f"{log_type_color[_type.value]}[{log_type_labels[_type.value].upper()} : {who}] ", end="")
        print(*values, sep=sep, end=Style.RESET_ALL+end, file=file, flush=flush)
 
class Logger:
    def __init__(self, name : str):
        self.name = name

    def _log(self, msg_list : List[object], type : LogType):
        dprint(*msg_list, who=self.name, _type=type)

    def log_info(self, *msg):
        self._log(msg, LogType.INFO)

    def log_warning(self, *msg):
        self._log(msg, LogType.WARNING)

    def log_error(self, *msg):
        self._log(msg, LogType.ERROR)

if __name__ == "__main__":
    class A:
        pass

    dprint(f"info", "info", _type=LogType.INFO)
    dprint(f"warning", who="main", _type=LogType.WARNING)
    dprint(f"error", who=whoami(A()), _type=LogType.ERROR)

    l1 = Logger("program")
    l1.log_error("bad msg")
    l1.log_info("info")
    l1.log_warning("warning")
