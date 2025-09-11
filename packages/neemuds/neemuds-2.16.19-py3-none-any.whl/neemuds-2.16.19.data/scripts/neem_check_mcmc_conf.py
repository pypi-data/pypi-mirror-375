#!python

from sys import argv
from os import environ
from py3toolset.txt_color import r, g, bold
environ['NEEMUDS_LOAD_LIBS'] = '0'
from neemuds.mcmc_config_parser import MCMCConfig

if '__main__' == __name__:
    if len(argv) > 1:
        MCMCConfig(argv[1])
        print(bold(g("The configuration file "+argv[1]+" was tested OK"
                     " (warnings are not errors).")))
    else:
        print(bold(r("USAGE:")), argv[0], "<neemuds_mcmc_config.ini>")
        print("This script verifies a NEEMUDS McMC configuration is correct"
              " (.ini format).")
