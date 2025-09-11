from py3toolset.nmath import str_isfloat, str_isint
from neemuds.params import get_conf_filename, parse_params_conf_file, Params


class PlanetParams(Params):
    """
    Class representing the parameters associated to a planet for neemuds.
    Comes with field-parameter checking capabilities (input file parsing is handled externally, see: get_planet_conf_filename()).
    See also: parent class params.Params.
    """
    def __init__(self, planet, pmap):
        self.planet = planet
        self.rhobar = float(pmap["rhobar"])
        self.lmin = int(pmap["lmin"])
        self.lmax = int(pmap["lmax"])
        self.nmin = int(pmap["nmin"])
        self.nmax = int(pmap["nmax"])
        # self.jcom = int(pmap["jcom"]) # (love or rayleigh mode for mineos) useless, the program sets it as an option
        super().__init__(pmap)

    def get_fieldnames():  # static method (no self argument)
        return ["rhobar", "lmin", "lmax", "nmin", "nmax"]

    @staticmethod
    def check_field_value(name, value):
        """
        Checks parameter domain/format validity.
        """
        if name == "rhobar" and not str_isfloat(value):
            raise Exception("rhobar (" + value + ") must be a float > 0.")
        elif name in ["lmin", "lmax", "nmin", "nmax"] and not str_isint(value):
            raise Exception(name + " (" + value + ") must be a int >= 0.")

    def print_params(self):
        """
        Prints planet parameters.
        """
        print("Parameters for planet:", self.planet)
        super().print_params()


def parse_planet_conf_file(planet):
    """
    Given a planet name, finds the conf file and gets back parameters for storing in instance attributes.
    Returns a PlanetParams object.
    """
    return parse_params_conf_file(planet, PlanetParams)


def get_planet_conf_filename(planet):
    """
    Given a planet name, returns the filename for its parameters.
    E.g. neemuds_earth.conf for Earth.
    """
    return get_conf_filename(planet)
