#!python

import neemuds
import os
from os.path import dirname, isdir, basename, expanduser
from posix import getcwd
import re
from shutil import move
from sys import argv
import traceback, sys

from preneemuds.preneem import filcut, remove_instru_resp, decimate
from preneemuds.ddt import read_ddt, save_ddt, parse_ddt
from preneemuds.z import preneem_z
from py3toolset.file_backup import work_on_copies
from py3toolset.fs import (glob_files, set_abs_or_relative_path,
                        all_files_in_same_dir, check_files,
                        infer_path_rel_and_abs_cmds)
from py3toolset.cmd_interact import is_help_switch
from py3toolset.txt_color import Color, col, print_frame, print_big_frame
from neemuds import ndata_dir_ne


# Min frequency for instrumental response deconvolution ONLY
FMIN = .001666  # (T = 600 s)
FMAX = .0333  # (T = 30 s)

DEFAULT_ZFILES = { "SAC":"*BHZ.M.SAC", "RESP":"RESP*.BHZ"}

def usage():
    # set script paths needed in usage (which vary depending if the script is in path or
    # not)
    cwd_cmd, other_dir_cmd = infer_path_rel_and_abs_cmds(argv)
    print (col(Color.BLUE, """
--------------------------------------------------------------------
USAGE: """ + cwd_cmd + """ [<DIRECTORY>] <SACZ_file> <RESPZ_file> [-d|--ddt value]
Or: """ + cwd_cmd + """ <DIRECTORY> [<SACZ_file> <RESPZ_file>] [-d|--ddt value]""") + """

Parameters enclosed by brackets [] are optional parameters.

""" + col(Color.BLUE, "DIRECTORY") + """ is the parent directory of SAC and RESP files.
    If DIRECTORY is set you just need to pass the sac and resp filenames, but if not you need to pass the full paths of these files (relative or absolute).
    N.B.: RESP and SAC files must be in the same folder.

""" + col(Color.BLUE, "--ddt or -dt") + """ switch sets the delta value used to decimate the sac traces: if not set, the program will search the value in DELTA.x (in the same directory as your sac file).
    If set, the program will save it to DELTA.x, overriding the previous value.

""" + col(Color.RED, """---------
Examples:
---------""") + """
    """ + col(Color.BLUE, "$") + " " + cwd_cmd + """ """ + ndata_dir_ne + """/sismos/#03_1999.228.23.02 1999.228.23.02.20.0370.II.KDAK.00.BHZ.M.SAC RESP.II.KDAK.00.BHZ
    Or, shorter way, globing files :
    """ + col(Color.BLUE, "$") + " " + cwd_cmd + """ """ + ndata_dir_ne + """/sismos/#03_1999.228.23.02 *.BHZ.M.SAC RESP*.BHZ

    Or, alternatively, going in sac file parent folder:
    """ + col(Color.BLUE, "$") + " cd " + ndata_dir_ne + """/sismos/#03_1999.228.23.02
    """ + col(Color.BLUE, "$") + " " + other_dir_cmd + """ 1999.228.23.02.20.0370.II.KDAK.00.BHZ.M.SAC RESP.II.KDAK.00.BHZ
    Or, with glob patterns:
    """ + col(Color.BLUE, "$") + " cd " + ndata_dir_ne + """/sismos/#03_1999.228.23.02
    """ + col(Color.BLUE, "$") + " " + other_dir_cmd + """ *.BHZ.M.SAC RESP*.BHZ

    Or, using the default SAC and RESP files specifying just the parent folder:
    """ + col(Color.BLUE, "$") + " " + cwd_cmd + """ """ + ndata_dir_ne + """/sismos/#03_1999.228.23.02
    (The default files match the patterns *.BHZ.M.SAC RESP*.BHZ)
""")

if __name__ == '__main__':
    if(len(argv) < 2 or is_help_switch(argv[1])):
        usage()
    else:
        try:

            # try to get decimation delta from command line
            dt = parse_ddt(argv, clean_argv=True)  # warning: may change argv len

            argc = len(argv)

            # determine if sac/resp files are passed relatively to a directory or with full relative/absolute paths
            file_arg_pos = 1
            # verify if a sac dir is passed
            sac_dir = None
            if(isdir(argv[1])):  # first arg is a directory
                sac_dir = argv[1]
                file_arg_pos += 1
                sac_dir = expanduser(sac_dir)
            else:
                sac_dir = getcwd()  # may change later
                                    # if full sac file path passed

            if(argc <= file_arg_pos):
                print_frame("USING DEFAULT SAC AND RESP FILES IN: " + sac_dir)
                sac_file = set_abs_or_relative_path(sac_dir, DEFAULT_ZFILES["SAC"])
                resp_file = set_abs_or_relative_path(sac_dir, DEFAULT_ZFILES["RESP"])
            else:
                sac_file = set_abs_or_relative_path(sac_dir, argv[file_arg_pos])
                resp_file = set_abs_or_relative_path(sac_dir, argv[file_arg_pos + 1])

            # expand wildcards in filenames
            sac_file, resp_file = glob_files(sac_file, resp_file)

            check_files(sac_file, resp_file)

            if(not all_files_in_same_dir(sac_file, resp_file)):
                print("Error: SAC and RESP files should all be in the same parent directory.")
                usage()
                exit()

            # get decimation delta from file if not provided in command line
            # otherwise save it in file
            sac_dir = dirname(sac_file)
            if(dt == -1):
                dt = read_ddt(sac_dir)
                if (dt == -1):  # delta file not found/properly readable
                    print(col(Color.RED, "Error: no decimation delta defined."))
                    usage()
                    exit()
            else:
                save_ddt(sac_dir, dt)
            print("dt=" + str(dt))


            # ready to process
            preneem_z(sac_file, resp_file, dt)

        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            print(col(Color.RED, str(e)))
            usage()



