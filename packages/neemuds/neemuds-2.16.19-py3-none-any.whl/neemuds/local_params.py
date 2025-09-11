from py3toolset.nmath import str_isfloat, str_isint
from neemuds.params import get_conf_filename, parse_params_conf_file, Params


class LocalParams(Params):
    """
    Class representing the parameters associated to local scale for neemuds.
    Comes with field-parameter checking capabilities (input file parsing is handled externally, see: get_local_conf_filename()).
    See also: parent class params.Params.
    """
    def __init__(self, planet, pmap):
        # see disper.pyx for types
        self.fS = int(pmap["fS"])
        self.fU = int(pmap["fU"])
        self.fM = int(pmap["fM"])
        self.ic = float(pmap["ic"])
        self.f1 = float(pmap["f1"])
        self.f2 = float(pmap["f2"])
        self.f3 = float(pmap["f3"])
        self.h = float(pmap["h"])
        self.use_slu_disp96 = pmap["use_slu_disp96"] == 'True'
        super().__init__(pmap)

    def get_fieldnames():  # static method (no self argument)
        return ["fS", "fU", "ic", "h", "f1", "f2", "f3", "fM", "use_slu_disp96"]

    @staticmethod
    def check_field_value(name, value):
        """
        Checks parameter domain/format validity.
        """
        if name in ["ic", "f1", "h", "f2", "f3"] and not str_isfloat(value):
            raise ValueError(name+" (" + value + ") must be a non-negative float.")
        elif name in ["fS", "fU", "fM"] and not str_isint(value):
            raise ValueError(name + " (" + value + ") must be a non-negative int.")
        elif name in ["use_slu_disp96"] and value not in ['False', 'True']:
            raise ValueError(name + " (" + value + ") must be a bool (True or"
                             " False).")

    def print_params(self):
        """
        Prints local scale parameters.
        """
        print("Parameters for local scale: ")
        super().print_params()


def parse_local_conf_file():
    """
    Finds the local scale conf file and gets back parameters for storing in instance attributes.
    Returns a LocalParams object.
    """
    return parse_params_conf_file("local", LocalParams)


def get_local_conf_filename():
    """
    Returns the local scale configuration filename.
    """
    return get_conf_filename("local")
