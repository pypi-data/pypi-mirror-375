#!python

from os.path import exists
from posix import system
from posixpath import basename, dirname
import sys
from os import sep, environ
import traceback
from py3toolset.txt_color import col, Color, bold, print_frame  # ,frame, warn
import re
import neemuds  # imported to load libs (neemuds/__init__.py)
import mcmc
from neemuds.mcmc_config_parser import MCMCConfig
from py3toolset.fs import infer_path_rel_and_abs_cmds

# TODO: check that the file conf_file (-p option) is well formed


def usage():
    cwd_cmd = infer_path_rel_and_abs_cmds(sys.argv)[0]
    print_frame("USAGE: ")
    print(col(Color.RED, bold(cwd_cmd))+" "+col(Color.BLUE,
                                                    "<URpdffrq.xyz> ") +
          col(Color.BLUE, "[<ULpdffrq.xyz>] [")+col(Color.RED, "-p ") +
          col(Color.BLUE, "<param_file>]")+"""
     You must at least specify the pdf file for Rayleigh group velocity/freqs variables.
     The second file (Love group velocity pdf for Love waves) is optional.
     `param_file' is the configuration file for the MCMC, defaultly it is neemuds_mcmc.ini.
     This last option (-p) is also optional.
    """)

# This function launches the MCMCInv_clt program instead of using
# the python wrapper of MCMCInv_lib. [DEPRECATED]
def external_binary_mcmc(param_file, UPDF_rayl, UPDF_love=None):
    # find binary neemuds_mcmc, launch it if found
    # or otherwise ask user to do a make for building
    MCMC_BIN = dirname(sys.argv[0])+sep+"MCMCInv_clt/bin/neemuds_mcmc"
    if exists(MCMC_BIN):
        #cmd = MCMC_BIN + " " + \
        #        repr(sys.argv[1:])[1:-1].replace("'", "").replace(",", "")
        # do it the more readable way
        cmd = MCMC_BIN + " -p "+param_file+" "+UPDF_rayl
        if(UPDF_love):
            cmd+= " "+UPDF_love
        print_frame("Launching command from Python: " + cmd)
        exit_status = system(cmd)
        if(exit_status > 0):
            raise Exception(basename(MCMC_BIN) + " terminated"
                            " with an internal error or was "
                            "interrupted (see above).")
    else:
        raise Exception(basename(MCMC_BIN) + " not found. Type `make -C " +
                        re.sub(r'/.*', '', dirname(MCMC_BIN)) +
                        "' for compiling then execute " +
                        sys.argv[0] + " again.")


if __name__ == '__main__':
    try:
        if(len(sys.argv) == 1 or "-h" in sys.argv or "--help" in sys.argv):
            usage()
            exit(0)
        # parse command options: 2 PDF files
        # (including one optional) plus optional -p conf_file
        conf_file = "neemuds_mcmc.ini"
        default_conf_fp = True
        for i, arg in enumerate(sys.argv[:]):
            if(arg == "-p"):
                if(i < len(sys.argv)):
                    conf_file = sys.argv[1+i]
                    default_conf_fp = False
                else:
                    raise Exception("No filepath found after -p switch.")
        try:
            sys.argv.remove("-p")
        except:
            pass
        try:
            sys.argv.remove(conf_file)
        except:
            pass
        if(len(sys.argv) == 1):
            raise Exception("No UPDF file found on the command line.")
        if(len(sys.argv) > 3):
            raise Exception("The command line is not valid. "
                            "Too many arguments.")
        UPDF_rayl = sys.argv[1]
        UPDF_love = None
        # check that command's argument files exist
        # (exception raised otherwise)
        if(not exists(UPDF_rayl)):
            raise Exception(UPDF_rayl+" doesn't exist.")
        if(not exists(conf_file)):
            raise Exception("conf. file "+conf_file+" doesn't exist.")
        if(len(sys.argv) > 2):
            UPDF_love = sys.argv[2]
            if(not exists(UPDF_love)):
                raise Exception(UPDF_love+" doesn't exist.")
        if(default_conf_fp):
            print("Using the default conf. filepath: " + conf_file +
                  " (because -p switch wasn't used.")
        if('NEEMUDS_MCMC_CLT' in environ.keys() and
           environ['NEEMUDS_MCMC_CLT'] == "1"):
            print(col(Color.RED, bold("WARNING: the MCMCInv_clt program is deprecated and no longer maintained.")))
            if conf_file.endswith('.ini'):
                raise ValueError('Can\'t use mcmc binary program with new .ini'
                                 ' configuration file')
            external_binary_mcmc(conf_file, UPDF_rayl, UPDF_love)
        else:
            if conf_file.endswith('.ini'):
                parsed_conf = MCMCConfig(conf_file)
                mcmc.mcmc_struct(parsed_conf.__dict__, UPDF_rayl, UPDF_love)
            else:
                mcmc.mcmc(conf_file, UPDF_rayl, UPDF_love)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        msg = str(e)
        if(not msg.lower().startswith("error")):
            msg = "Error: " + msg
        print_frame(msg, Color.RED, centering=False)

