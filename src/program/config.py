import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

if __name__ != "__main__": print("importing configs")

config_file_path = r"D:\projects\programing\python2\serious\project_mgr_proto\src\config.yaml"

DEBUG_PRINT_LEVEL = 0
DO_RUN = True
DO_DELAY = False
Config = {}

with open(config_file_path, "r") as  config_file:
    Config = yaml.load(config_file.read(), Loader=Loader)
    DEBUG_PRINT_LEVEL = Config["app"]["log_level"]  
    DO_RUN = Config["do_run"]  
    DO_DELAY = Config["do_delay"]  

