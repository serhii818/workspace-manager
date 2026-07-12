from __future__ import annotations
from subprocess import Popen, DEVNULL
from time import sleep
import subprocess
import pathlib
from typing import List

from .Jsonnable import *
from .my_loger import *
from . import config

# ========================================================================================

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
si = subprocess.STARTUPINFO()
si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
si.wShowWindow = 7  # SW_SHOWMINNOACTIVE

# =======================================================================================
#                                       RunTask
# =======================================================================================



class RunTask(Jsonable):

    def __init__(self, prog : Program, arg : str, delay=2, cwd=None, termination_command : RunTask = None):
        
        if isinstance(prog, Program):
            self.program : Program = prog
        else:
            self.program = None
            dprint("cant use program name for runtask", who=whoami(self), _type=LogType.ERROR)

        self.argument : str = arg
        self.delay = delay
        if cwd == None: cwd = os.getcwd()
        if pathlib.Path(cwd).exists():
            self.cwd = cwd
        else:
            dprint(f"path {cwd} does exists", who=whoami(self), _type=LogType.ERROR)
        self.termination_commnad = termination_command

    def run(self):
        dprint(f"running {self.program.name}", who=self)
        l = [self.program.path]
        if self.argument != "":
            l += self.argument.split(" ")
        dprint(f"running command : {l}")
        p = None
        if config.DO_RUN: 
            p = Popen(l, startupinfo=si, cwd=self.cwd)
        if config.DO_DELAY: sleep(self.delay)
        return RunTaskInstance(self, p)

    def to_dict(self):
        return {
            "program" : self.program.name, 
            "argument" : self.argument,
            "delay" : self.delay,
            "cwd" : self.cwd,
            "term": 
                self.termination_commnad 
                if self.termination_commnad == None 
                else self.termination_commnad.to_dict(),
            }
    
    def __repr__(self):
        return f"{whoami(self)}({self.program}, {self.argument}, {self.delay})"
    
    @staticmethod
    def from_dict(dict, resolver=None):
        cwd_ = dict.get("cwd")
        if cwd_ == None: cwd_ = os.getcwd()
        termination_comm = dict.get("term")
        if termination_comm != None:
            termination_comm = RunTask.from_dict(termination_comm, resolver=resolver)
        return RunTask(resolver(dict["program"]), dict["argument"], dict["delay"], cwd_, termination_command=termination_comm)
    
# =======================================================================================
#                                   RunTaskInstance
# =======================================================================================
class RunTaskInstance:
    def __init__(self, run_task_ref_ : RunTask, proc_: Popen):
        self.run_task_ref = run_task_ref_
        self.proc = proc_

    def terminate(self):
        if self.run_task_ref.termination_commnad == None:
            self.proc.terminate()
        else:
            self.run_task_ref.termination_commnad.run()

# =======================================================================================
#                                     RunScript
# =======================================================================================

class RunScript(Jsonable):
    def __init__(self, _name, _tasks : List[RunTask] = None):
        self.name = _name
        self.tasks : List[RunTask] = _tasks if _tasks is not None else []

    def __repr__(self):
        return f"{whoami(self)}({self.name}, [\n{'\n'.join(['\t'+str(t) for t in self.tasks])}\n])"
    
    def add_task(self, task):
        self.tasks.append(task)

    def run(self) -> List[Popen|None]:
        dprint(f"running run sequence {self.name}", who=f"RunScript({self.name})")
        processes = []

        for t in self.tasks:
            processes.append(t.run())

        return processes

    def to_dict(self):
        return {
            "name": self.name,
            "tasks": [t.to_dict() for t in self.tasks],
        }
        
    @staticmethod
    def from_dict(dict, resolver=None):
        return RunScript(dict["name"], [RunTask.from_dict(t, resolver) for t in dict["tasks"]])

# =======================================================================================
#                                      PROGRAM
# =======================================================================================

class NotAProgram(Exception):pass
class Program(Jsonable):

    def __init__(self, _name : str, _path : str):
        self.name = _name
        self.path = pathlib.Path(_path)
        if self.path.suffix != ".exe":
            raise NotAProgram(f"file {self.path.name} is not a program")

    def __repr__(self):
        return f"{whoami(self)}({self.name}, {self.path})"
    
    def run(self):
        dprint(f"runnig program {self.name}")
        p = None
        if config.DO_RUN:
            p = Popen(self.path)
        return p
    
    def to_dict(self):
        return {
            "name": self.name,
            "path": str(self.path),
        }
    
    @staticmethod
    def from_dict(dict):
        return Program(dict["name"], dict["path"])