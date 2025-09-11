#!python

import sys
from os.path import exists
from neemuds.mcmc_config_parser import MCMCConfig
if __name__ == "__main__":
    if len(sys.argv) < 2 or not sys.argv[1].lower() in ['earth', 'mars', 'local']:
        print('USAGE: '+sys.argv[0]+" <earth|mars|local>")
        exit(1)
    conf_file = "neemuds_mcmc_"+sys.argv[1]+".ini"
    any_conf = MCMCConfig()
    if exists(conf_file):
        raise Exception('The file already exists, please delete it to generate'
                        ' again ('+conf_file+')')
    eval('any_conf.gen_'+sys.argv[1].lower()+'_conf(conf_file)')
    # test the file
    any_conf = MCMCConfig()
