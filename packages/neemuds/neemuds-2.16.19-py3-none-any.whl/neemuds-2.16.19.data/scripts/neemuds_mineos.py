#!python
from neemuds.planet_params import parse_planet_conf_file
import sys
from py3toolset.txt_color import warn, print_frame, Color, col
try:
    # dev mode
    from mineos import main, usage
except Exception:
    # pkg installed via pip
    from pymineos.mineos import main, usage
from sys import argv
import traceback
import re

if __name__ == '__main__':
    if (re.match(str.encode('.*earth.*', 'utf-8'),
                 str(argv[:]).encode('utf-8'), re.I)):
        planet = "earth"
    elif (re.match(str.encode('.*mars.*', 'utf-8'),
                   str(argv[:]).encode('utf-8'), re.I)):
        planet = "mars"
    else:
        planet = ""
    p = None
    try:
        if planet != "":
            p = parse_planet_conf_file(planet)
            warn("If Neemuds stops at this point, Mineos is responsible. "
                 "Check your reference model or the translation coefficients."
                 " Both are set in the file neemuds_" + planet + ".conf.")
        if p is None:
            main()
        else:
            main(p.nmin, p.nmax,  p.rhobar, p.lmin, p.lmax)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        msg = str(e)
        if not msg.lower().startswith("error"):
            msg = "Error: " + msg
        print_frame(msg, Color.RED, centering=False)
        print(col(Color.GREEN, "Use -h, --help option for help"
                  " (--details for detailed help)."))
        usage()
