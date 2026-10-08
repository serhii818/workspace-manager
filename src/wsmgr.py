from __future__ import annotations
from typing import List, Tuple
from enum import StrEnum, Enum
import os
cwd = os.getcwd()
from sys import argv as sys_argv


import pathlib

#os.chdir(r"D:\projects\programing\python2\serious\project_mgr_proto\src")

from program.run_script import *
from program.DataMgr import *
from program.my_loger import *

dprint("setting datamgr to runtask", who="main")
RunTask.s_datamgr = DataMgr()


# =======================================================================================
#                                   MAIN
# =======================================================================================

class Command(StrEnum):
    RUN = "run"
    LIST = "list" # programs, scripts
    REGISTER = "register"
    DEFAULT = "default" # configure default
    HELP = "help"
    NEW = "new"
    EDIT = "edit"

# ====================================== UTILS ======================================

def print_help(args):
    path = pathlib.Path(args[0]).parent.parent
    path = str(path) + r"\data\help.txt"

    with open(path, "r") as f:
        print(f.read())


def is_flag(arg : str):
    return arg.startswith(("-", "--"))

def parse_flag_until_command(argv : List[str],  curr_idx: int):
    flags = []
    while curr_idx < len(argv) and is_flag(argv[curr_idx]):
        if argv[curr_idx].startswith("--"):
            flags.append(argv[curr_idx].replace("-", ""))    
        else:
            flags += argv[curr_idx].replace("-", "")
        curr_idx += 1
    #`dprint(f"{flags} idx={curr_idx}", who="flag parser")
    return flags,  curr_idx


def next_command(argv, curr_idx) -> Tuple[str, List[str], int]:
    """return -> (next_command, list of flags, current index in array)"""
    flags, idx = parse_flag_until_command(argv, curr_idx)
    what = ""
    if idx < len(argv):
        what = argv[idx]
        idx += 1
    return what, flags, idx

# ====================================== MAIN_LOGIC ======================================

class ProcessMgr:
    def __init__(self):
        self.processes = []

    def add(self, proc : Popen | List[Popen|None] | None):
        if proc == None: return
        if proc is Popen:
            print("addind Popen proc")
            self.processes.append(proc)
        if proc is list:
            for p in proc:
                self.add(p)

    def terminate(self):
        for p in self.processes:
            pass

com_proc = "command interpeter"

# ========================================================================================

def _handle_run_comm(args, arg_idx):
    what, flags, arg_idx = next_command(args, arg_idx)
            
    dprint("run command")
    if "p" in flags:
        pr : Program = DataMgr().get_program(what)
        if pr != None: 
            pr.run()
    else:
        sc : RunScript = DataMgr().get_runscript(what)
        if sc != None: 
            sc.run()

# ====================================== INTERPTER ======================================

def interpret_command_arr(args: List[str]):
    # delete
    dprint(f"pwd : {os.getcwd()}")
    dprint(f"changing cwd to {cwd}")
    os.chdir(cwd)
    dprint(f"pwd : {os.getcwd()}")
    # --
    if len(args) < 2:
        dprint("running wsmgr witout arguments", who=com_proc)
        if len(DataMgr()._default_run) < 2:
            dprint("Default run setting is empty", who=com_proc, _type=LogType.ERROR)
        else:
            interpret_command_arr(DataMgr()._default_run)
        return

    #dprint(args, who="command exec")
    for i in range(len(args)):
        args[i] = args[i].strip()
    #dprint(args, who="command exec")
    arg_idx = 1

    command, flags, arg_idx = next_command(args, arg_idx)
    #dprint(flags, args, arg_idx, command)

    for f in flags:
        match f:
            case "v": print(f" Work Spape Manager v{DataMgr().APP_VERSION}")
            case "h": print_help(args)

    match command:
        case "":
            pass
        case Command.RUN: _handle_run_comm(args, arg_idx)

        case Command.LIST:
            dprint("list")
            what, flags, arg_idx = next_command(args, arg_idx)
            

            if "p" in flags:
                print("programs:")
                i = 0
                for k in DataMgr().programs.keys():
                    print(f"\t({i}) {k}")
                    i+=1
            if "s" in flags:
                print("scripts")
                for k in DataMgr().runscripts.keys():
                    print(f"\t{k}:")
                    i = 0
                    for t in DataMgr().runscripts[k].tasks:
                        print(f"\t\t[{i}] {t.program.name:<20} {t.argument:>20}")
                        i+=1

        case Command.REGISTER | "reg" | Command.NEW:
            dprint("registering")
            what, flags, arg_idx = next_command(args, arg_idx)
            if "p" in flags:
                full_path = os.getcwd()
                name = what
                if name.endswith(".exe"):
                    name = name[:-4]
                    dprint(f"|{name}|")
                full_path = full_path+f"\\{what}"
                if not pathlib.Path(full_path).is_file():
                    full_path += ".exe"
                if not pathlib.Path(full_path).is_file():
                    dprint("this is not an executalbe file", _type=LogType.ERROR)
                dprint(f"reginng {full_path}")
                DataMgr().reg_program(Program(name, full_path))
            elif "s" in flags:
                rs = RunScript(what)
                DataMgr().reg_runscript(rs)

        case Command.DEFAULT | "def":
            dprint("default run")
            what, flags, arg_idx = next_command(args, arg_idx)
            if what == "get":
                print("default run settings")
                print(f"\t\"{" ".join(DataMgr()._default_run)}\"")
            elif what == "set":
                DataMgr().default_run = ["wsmgr"] + args[arg_idx:]

        case Command.EDIT:

            # wsmgr edit <name> add <program name/program path> [argument]
            # wsmgr edit <name> remove <index>
            # wmsgr esit <name> set_arg <index> <arguments>
            what, flags, arg_idx = next_command(args, arg_idx)

            rs = DataMgr().get_runscript(what)
            if rs == None:
                dprint(f"script {what} does't exists", _type=LogType.ERROR)
                return

            what, flags, arg_idx = next_command(args, arg_idx)
            match what:
                case "add":
                    what, flags, arg_idx = next_command(args, arg_idx)
                    p = DataMgr().get_program(what)
                    if p == None:
                        dprint(f"program {what} doesn't exists", _type=LogType.ERROR)
                        return
                    
                    p_arg = ""
                    if arg_idx < len(args):
                        what, flags, arg_idx = next_command(args, arg_idx)
                        p_arg = what

                        if "f" in flags:
                            if os.path.exists(p_arg):
                                p_arg = os.path.abspath(p_arg)
                            else:
                                dprint(f"argument {p_arg} doesn't exists", _type=LogType.ERROR)
                                return
                        elif "v":  # obsidian vault
                            p_arg = "obsidian://open?vault=" + p_arg
                            

                    r = RunTask(p, p_arg)
                    rs.add_task(r)
                    

                case "remove":
                    what, flags, arg_idx = next_command(args, arg_idx)
                    prog_idx = int(what)
                    if prog_idx >= len(rs.tasks):
                        dprint("index out of range", _type=LogType.ERROR)
                        return
                    
                    rs.tasks.pop(prog_idx)
                case "set_arg":pass
                case _:
                    dprint("unknowt option for edit", _type=LogType.ERROR)
            


        case Command.HELP:
            print_help(args)
        case _:
            dprint("unknown command", _type=LogType.ERROR)

    DataMgr().save()


def load_data():
    dprint("loading data", who="main")

    nginx_task = RunTask(DataMgr().get_program("nginx"), "", delay=1, cwd=r"D:\SOFTWARE\nginx-1.30.3")
    pyapi_task = RunTask(DataMgr().get_program("python"), "", delay=2, cwd=r"D:\projects\web\omega-pages\api")
    dprint(nginx_task, who="task")
    dprint(pyapi_task, who="task")
    web_dev_services = RunScript("web_services", [nginx_task, pyapi_task])
    DataMgr().reg_runscript(web_dev_services)

def test():
    pass

# =======================================================================================
#                                   ENTRY_POINT
# =======================================================================================

class Mode(Enum):
    MAIN = 0
    LOAD_DATA = 5
    TEST = 6

mode = Mode.MAIN

if __name__ == "__main__":
    dprint("debug print is active", who="main", _type=LogType.WARNING)
    match mode:
        case Mode.MAIN: interpret_command_arr(sys_argv)
        case Mode.LOAD_DATA: load_data()
        case Mode.TEST: test()
