from typing import Dict, List
import json

from . import run_script as RS
from .my_loger import *
from .config import Config

class Singleton(type):
    _instances = {}

    def __call__(self, *argc,  **kwargs):
        if self not in self._instances:
            instance = super().__call__(*argc, **kwargs)
            self._instances[self] = instance
        return self._instances[self]

#[ ] remove singleton and make it into a module
#[ ] add load data function
#[ ] finish save to save scripts
#[ ] move loading logic to __init__
class InvalidConfiguration(Exception):pass
class DataMgr(metaclass=Singleton):
    def __init__(self):
        # init DataManager
        dprint("DataManger instantiated", who="DataMgr")
        self.data_path : str = None
        #with open("./config.yaml", "r") as  config_file:
            #self.c = yaml.load(config_file.read(), Loader=Loader)
        self.data_path = Config["data_path"]["wsmgr"]    

        self.APP_VERSION = Config["app"]["version"]
        if self.data_path != None and self.data_path.startswith("%"):
            sp = self.data_path.split("%")
            var = sp[1]
            #dprint(f"var is {var}")
            self.data_path = os.path.join(os.getenv(var), sp[2][1:].replace("/", "\\"))
            #dprint(f"{self.data_path}")
        if not os.path.isdir(self.data_path):
            dprint("created data folder")
            os.makedirs(self.data_path)
        else:
            dprint("opened data folder")

        # variables
        self.programs : Dict[str, RS.Program] = {}
        self.runscripts : Dict[str, RS.RunScript] = {}
        self._data_loaded = False
        self._is_data_changed = False
        self._default_run : List[str] = ["wsmgr", "-v"]
        self.cur_proc = []

    

    @property
    def defaut_run(self): return self._default_run

    @defaut_run.setter
    def default_run(self, v):
        self._default_run = v
        self._is_data_changed = True
        

    def get_program(self, prog_name : str):
        prog = self.programs.get(prog_name)
        if prog is None:
            dprint(f"failed to find \"{prog_name}\" RS.Program!!!", who=self, _type=LogType.ERROR)
        return prog
    
    def reg_program(self, prog : RS.Program):
        dprint(f"registering RS.Program {prog.name}", who=self)
        self.programs.update({prog.name: prog})
        self.save()

    def reg_runscript(self, rs : RS.RunScript):
        dprint(f"registering script \"{rs.name}\"", who=self)
        self.runscripts.update({rs.name: rs})
        self.save()

    def get_runscript(self, rs_name : str):
        rs = self.runscripts.get(rs_name)
        if rs is None:
            dprint(f"failed to find \"{rs_name}\" run script!!!", who=self, _type=LogType.ERROR)
        return rs

    def to_dict(self):
        save_dict = {
            "programs" : [],
            "run_scripts" : [], 
            "default-run" : self._default_run
        }

        for name, prog in self.programs.items():
            prog_ser = prog.to_dict()
            save_dict["programs"].append(prog_ser)

        for name, sc in self.runscripts.items():
            sc_ser = sc.to_dict()
            save_dict["run_scripts"].append(sc_ser)

        return save_dict

    def save(self):
        dprint("saving to file", who=self)
        save_dict = self.to_dict()
        with open(os.path.join(self.data_path, "save1.json"), "w") as file:
            json.dump(save_dict, file)

    def load(self):
        if self._data_loaded: return
        self._data_loaded = True
        dprint(f"loading all save data", who=self)
        file = open(os.path.join(self.data_path, "save1.json"), "r")
        datadict = json.load(file)
        file.close()
        for pdict in datadict["programs"]:
            p = RS.Program.from_dict(pdict)
            #dprint(f"reed RS.Program : {p}", who=self)
            self.programs.update({p.name : p})

        for rsdict in datadict["run_scripts"]:
            rs = RS.RunScript.from_dict(rsdict, self.get_program)
            #dprint(f"reed script : {rs}", who=self)
            self.runscripts.update({rs.name : rs})
        
        d_ = datadict.get("default-run")
        if d_ != None: self._default_run = d_
        


    def print_state(self):
        dprint(f"{json.dumps(self.to_dict(), indent=4)}", who=self)



DataMgr().load()