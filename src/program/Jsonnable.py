from abc import ABC, abstractmethod
import json
from typing import Dict

class AbstractMethodException(Exception):pass
class Jsonable(ABC):
    @abstractmethod
    def to_dict(self):
        raise AbstractMethodException("this mathod is not implemented")
        return {}

    @staticmethod
    @abstractmethod
    def from_dict(dict : Dict, resolver=None):
        raise AbstractMethodException("this mathod is not implemented")
        return None
    
    def to_json(self):
        return json.dumps(Jsonable.to_dict())

    @staticmethod
    def from_json(json_str : str):
        return Jsonable.from_dict(json.loads(json_str))