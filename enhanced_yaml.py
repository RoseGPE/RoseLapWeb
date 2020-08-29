import ruamel.yaml
import numpy as np

class ObjectDict:
    def __init__(self, **entries):
        self.__dict__.update(entries)

def syntax_expand(o):
    if isinstance(o, int):
        return float(o)

    elif isinstance(o, str): # try making strings numbers
        try:
            return float(o)
        except:
            pass

    elif isinstance(o, list):
        return [syntax_expand(x) for x in o]

    elif isinstance(o, dict):
        return ObjectDict(**{k:syntax_expand(x) for (k,x) in o.items()})
    return o

# Load a YAML file and apply enhancements
def load(stream):
  out = ruamel.yaml.safe_load(stream)
  return syntax_expand(out)