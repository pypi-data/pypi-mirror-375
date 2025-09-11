import os
import re
from py3toolset.fs import get_prog_parent_dir
from py3toolset.txt_color import warn
from os.path import expanduser, dirname

NEEMUDS_DIR = get_prog_parent_dir() + os.sep

class Params:
    def __init__(self, pmap):
        self._pmap = pmap
        
    def get_fieldnames():# static method (no self argument)
        # must be redefined by child class (abstract function)
        """
        Static method to get the list of valid attributes for this class.
        """
        raise Exception("Params class error: get_fieldnames() must be redefined by child class.")
    
    def check_field_value(name, value): # static method (no self argument)
        # must be redefined by child class (abstract function)
        raise Exception("Params class error: check_field_value() must be redefined by child class.")
    
    def print_params(self):
        for k,v in self._pmap.items():
            print(" "+k+": "+v)

def get_conf_filename(scale):
    """
    Given a scale name, returns the filename for its parameters.
    E.g. neemuds_earth.conf for Earth.
    """
    prefix = "neemuds_"
    scale = scale.lower()
    suffix = ".conf"
    if(scale not in ["mars", "earth", "local"]):
        raise Exception("Error scale must be local, Earth or Mars")
    return prefix + scale + suffix


def parse_params_conf_file(scale, ParamsClass, filepath=None):
    """
    Given a scale name, finds the conf file and gets back parameters for storing in instance attributes.
    Returns a ParamsClass object (ParamsClass must be a Params subclass).
    """
    from os.path import exists
    if(not filepath):
        filename = get_conf_filename(scale)
        filepath = get_working_dir(filename, suf=True)
#     print_frame("Parsing conf. file "+filepath)
    # read file
    if(not exists(filepath)):
        raise Exception("failed to find configuration file to parse it "
                "("+filename+"). It should be in current working directory or "
                "at least in Neemuds directory.")
    f = open(filepath, "r")
    lines = f.readlines()
    f.close()
    param_map = {}
    for pname in ParamsClass.get_fieldnames():
        param_map[pname] = None
    for l in [ re.sub(r"\s+", "", re.sub(r"#.*", '', line)) for line in lines]:
        if(len(l) == 0):
            continue
        # comments and blank chars removed from line and line isn't empty
        field_name = l.split("=")[0]
        g = re.match('^\[(.*)]\s*', field_name)
        if g != None:
            # (not a field) this is the section title in python configparser
            param_map['title'] = g.groups(1)[0]
            # print("conf. title:", param_map['title'])
            continue
        if(field_name not in ParamsClass.get_fieldnames()):
            raise Exception("field " + field_name + " found in " + filepath + " isn't valid.")
        # get field value from right hand side
        field_val = l.split("=")[1]
        ParamsClass.check_field_value(field_name, field_val)
        param_map[field_name] = field_val
    # each parameter is mandatory, not found/set => Exception
    missing_params = [v for v in param_map.keys() if param_map[v] == None]
    if(missing_params != []):
        raise Exception("One or several parameters are missing in conf. file "
                        + filepath + ".\nMissing params: " + repr(missing_params))
    # create a struct instance with parameters inside
    params = ParamsClass(scale, param_map)
    return params


gwd_warnings = [] # global var belonging to get_working_dir

def get_working_dir(target, suf=False, w=False):
    """
    Searches the target in the current working directory.

    What we call the working directory is where to find configuration files,
    the folder to retrieve ref. models, read and edit the priors or
    the sismos files. It can be the current working directory or NEEMUDS_DIR.

    Parameters:
        - target: the folder or filename targeted or its path relatively to the
        current or Neemuds directory. If the target exists in the
        current working directory then the function returns os.getcwd() otherwise
        it returns NEEMUDS_DIR, the Neemuds base directory (where the Neemuds
        scripts are located). The idea is to give the priority to CWD and to fallback
        to NEEMUDS_DIR if target is not located in CWD.
        Note: if the target doesn't exist neither in NEEMUDS_DIR the function
        still returns NEEMUDS_DIR and the caller will have the responsibility to
        verify the existence of the target on its own.
        - suf(fixing): if True then the working directory is returned with target
        path as a suffix. It's handy to get directly the filepath when calling the function.
        - w(arning): True to warn user if target has not been found in cwd but in NEEMUDS_DIR.
        The warning is displayed only the first time the function is called for one target.

    Returns: (depending on arguments) NEEMUDS_DIR or current working directory,
suffixed with target or not.

    """
    from os import getcwd, sep
    from os.path import exists
    target = expanduser(target)
    if target.startswith('/'):
        # already an absolute path
        if suf:
            return target
        else:
            return dirname(target)
    full_path = getcwd()+sep+target
    global gwd_warnings
    if(exists(full_path)):
        if(suf):
            return full_path
        else:
            return getcwd()
    else:
        warn_msg="File "+target+" comes from "+NEEMUDS_DIR+(" because it hasn't been found "
        "in current working directory.")
        if(warn_msg not in gwd_warnings):
            warn(warn_msg)
            gwd_warnings.append(warn_msg)
        if(suf):
            return NEEMUDS_DIR+sep+target
        else:
            return NEEMUDS_DIR

