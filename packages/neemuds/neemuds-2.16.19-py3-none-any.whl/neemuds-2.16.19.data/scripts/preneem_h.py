#!python
import neemuds
import os
from os.path import dirname, isdir, basename, expanduser
from posix import getcwd, remove
import re
from sys import argv
import traceback, sys

from preneemuds.preneem import (filcut, remove_instru_resp, decimate,
                                check_orthogonality, rotate)
from preneemuds.ddt import read_ddt, save_ddt, parse_ddt
from py3sac.sac import getsacinfo
from py3toolset.file_backup import work_on_copies
from py3toolset.fs import glob_files, set_abs_or_relative_path, \
    all_files_in_same_dir, check_files, infer_path_rel_and_abs_cmds
from py3toolset.cmd_interact import is_help_switch
from py3toolset.txt_color import Color, col, print_big_frame, print_frame
from neemuds import ndata_dir_ne


# Min frequency:
FMIN = 0.0018  # (T=555s) Check with filmin
FMAX = 0.028  # (T=35.7s)

DEFAULT_HFILES = { "SACH1":"*BHN.M.SAC", "SACH2":"*BHE.M.SAC", "RESPH1":"RESP*.BHN", "RESPH2":"RESP*.BHE"}

def usage():
    # set script paths needed in usage (which vary depending if the script is in path or
    # not)
    cwd_cmd, other_dir_cmd = infer_path_rel_and_abs_cmds(argv)
    print (col(Color.BLUE, """
--------------------------------------------------------------------
USAGE: """ + cwd_cmd + """ [<DIRECTORY>] <SACH1_file> <RESPH1_file> <SACH2_file> <RESPH2_file> [-d|--ddt value]
Or: """ + cwd_cmd + """ <DIRECTORY> [<SACH1_file> <RESPH1_file> <SACH2_file> <RESPH2_file>] [-d|--ddt value]""") + """

Parameters enclosed by brackets [] are optional parameters.

""" + col(Color.BLUE, "DIRECTORY") + """ is the parent directory of SAC and RESP files.
    If DIRECTORY is set you just need to pass the sac and resp filenames, but if not you need to pass the full paths of these files (relative or absolute).
    N.B.: RESP and SAC files must be in the same folder.

""" + col(Color.BLUE, "--ddt or -dt") + """ switch sets the delta value used to decimate the sac traces: if not set, the program will search the value in DELTA.x (in the same directory as your sac file).
    If set, the program will save it to DELTA.x, overriding the previous value.

""" + col(Color.RED, """---------
Examples:
---------""") + """
    """ + col(Color.BLUE, "$") + " " + cwd_cmd + """ """ + ndata_dir_ne + """/sismos/#03_1999.228.23.02/ 1999.228.23.02.20.0370.II.KDAK.00.BHN.M.SAC RESP.II.KDAK.00.BHN 1999.228.23.02.20.0369.II.KDAK.00.BHE.M.SAC RESP.II.KDAK.00.BHE
    Or, shorter way, with glob patterns:
    """ + col(Color.BLUE, "$") + """ """ + cwd_cmd + """ """ + ndata_dir_ne + """/sismos/#03_1999.228.23.02/ *.BHN.M.SAC RESP.*.BHN *.BHE.M.SAC RESP.*.BHE

    Or, alternatively, going on sac files parent folder:
    """ + col(Color.BLUE, "$") + " cd """ + ndata_dir_ne + """/sismos/#03_1999.228.23.02
    """ + col(Color.BLUE, "$") + " " + other_dir_cmd + """ 1999.228.23.02.20.0370.II.KDAK.00.BHN.M.SAC RESP.II.KDAK.00.BHN 1999.228.23.02.20.0369.II.KDAK.00.BHE.M.SAC RESP.II.KDAK.00.BHE
    Or, with glob patterns:
    """ + col(Color.BLUE, "$") + " cd """ + ndata_dir_ne + """/sismos/#03_1999.228.23.02
    """ + col(Color.BLUE, "$") + " " + other_dir_cmd + """ *.BHN.M.SAC RESP*.BHN *.BHE.M.SAC RESP*.BHE

    Or, using the default SAC and RESP files specifying just the parent folder:
    """ + col(Color.BLUE, "$") + " """ + cwd_cmd + """ """ + ndata_dir_ne + """/sismos/#03_1999.228.23.02
    (The default files match the patterns *.BHN.M.SAC RESP*.BHN *.BHE.M.SAC RESP*.BHE)
""")

def preneem_h(sach1_file, resph1_file, sach2_file, resph2_file, dt, t1="T1", t2="T2", answer="", fmin=FMIN, fmax=FMAX, cutting=True):
    """
    Executes the whole data process for the horizontal components, given the SAC and instrumental response files.
    The final result will be stored in the file RAYL.sac and LOVE.sac in the current working directory.
    There are seven steps: 0. SAC backup, 1. Signal window time cuts, 2. Instrumental response deconvolution, 3. Decimation, 4. Enforcing components orthogonality, 5. Rotation by the backward azimuth angle, 6. Saving file result.
    sach1_file -- SAC input to process, for North component.
    resph1_file -- SAC associated instrumental file.
    sach2_file -- SAC input to process, for East component.
    resph2_file -- SAC associated instrumental file.
    dt -- The delta for the decimation stage.
    Optional arguments:
    t1 -- Start of the cut in seconds if you don't want to pick the time manually.
    t2 -- End of the cut in seconds if you don't want to pick the time manually.
    answer -- To automatically respond to the questions prompting on terminal (regarding the SAC files backup/restoration).
    fmin -- Min. frequency used for instrumental deconvolution (FMIN by default).
    fmax -- Max. frequency used for instrumental deconvolution (FMAX by default).
    cutting -- Set it to False if you want to skip the cut stage for the signal.
    """
    print_big_frame("H-DATA PROCESSING " + basename(sach1_file) + ", " + basename(resph1_file) + ", " + basename(sach2_file) + ", "
                + basename(resph2_file) + "\n\t\t (from " + (dirname(sach1_file) or "./") + ")")
    print_frame("0. BACKUP")
    work_on_copies(sach1_file, sach2_file, answer=answer)
    check_files(sach1_file, resph1_file, sach2_file, resph2_file)
    sac_dir = dirname(sach1_file)
    if(re.match(sac_dir, r"\s") != None): sac_dir = "."
    backaz = int(getsacinfo(sach1_file, "BAZ"))
    print("Back-azimuth: " + str(backaz) + " (for " + basename(sach1_file) + ")")
    cut_sach1_file, cut_sach2_file  =  sach1_file + "c", sach2_file + "c"
    if(cutting):
        print_frame("1. CUTTING THE SIGNAL")
        filcut(sach1_file, cut_sach1_file, sach2_file, cut_sach2_file , t1=t1, t2=t2, deleting_filtered_sacs=True)
    # else: the function assumes that the cut sac traces have been created before elsewhere
    print_frame("2. REMOVING INSTRUMENTAL RESPONSE")
    remove_instru_resp(cut_sach1_file , resph1_file, fmin, fmax)
    remove_instru_resp(cut_sach2_file , resph2_file, fmin, fmax)
    print_frame("3. DECIMATION")
    decimate(cut_sach2_file, dt)
    decimate(cut_sach1_file, dt)
    print_frame("4. ENFORCING ORTHOGONALITY")
    check_orthogonality(cut_sach1_file, sach2_file + "c")
    print_frame("5. ROTATION")
    rotate(backaz, [cut_sach1_file, cut_sach2_file], ["RAYL.sac", "LOVE.sac"])
    print_frame("6. OUTPUTTING FILES IN RAYL.sac, LOVE.sac")
    # remove tmp files
    remove(cut_sach1_file)
    remove(cut_sach2_file)

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
                sach1_file = set_abs_or_relative_path(sac_dir, DEFAULT_HFILES["SACH1"])
                sach2_file = set_abs_or_relative_path(sac_dir, DEFAULT_HFILES["SACH2"])
                resph1_file = set_abs_or_relative_path(sac_dir, DEFAULT_HFILES["RESPH1"])
                resph2_file = set_abs_or_relative_path(sac_dir, DEFAULT_HFILES["RESPH2"])
            else:
                sach1_file = set_abs_or_relative_path(sac_dir, argv[file_arg_pos])
                sach2_file = set_abs_or_relative_path(sac_dir, argv[file_arg_pos + 2])
                resph1_file = set_abs_or_relative_path(sac_dir, argv[file_arg_pos + 1])
                resph2_file = set_abs_or_relative_path(sac_dir, argv[file_arg_pos + 3])

            # expand wildcards in filenames
            sach1_file, resph1_file, sach2_file, resph2_file = glob_files(sach1_file, resph1_file, sach2_file, resph2_file)

            check_files(sach1_file, resph1_file, sach2_file, resph2_file)

            if(not all_files_in_same_dir(sach1_file, sach2_file, resph1_file, resph2_file)):
                print("Error: SAC and RESP files should all be in the same parent directory.")
                usage()
                exit(1)
            sac_dir = dirname(sach1_file)

            # get decimation delta from file if not provided in command line
            # otherwise save it in file
            if(dt == -1):
                dt = read_ddt(sac_dir)
                if (dt == -1): # delta file not found/properly readable
                    print("Error: no decimation delta defined.")
                    usage()
                    exit()
            else:
                save_ddt(sac_dir, dt)
            print(argv[0]+": dt=" + str(dt))

            # ready to process
            preneem_h(sach1_file, resph1_file, sach2_file, resph2_file, dt)

        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            print(col(Color.RED, str(e)))
            usage()

