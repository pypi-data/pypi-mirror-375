#!python

from os.path import isdir, dirname, basename, join
from sys import argv
import sys, traceback
from posix import getcwd

from preneemuds.preneem import filcut
from preneemuds.ddt import read_ddt, save_ddt, parse_ddt
from preneem_h import DEFAULT_HFILES, preneem_h
from preneem_z import DEFAULT_ZFILES
from preneemuds.z import preneem_z
from py3toolset.fs import (glob_files, set_abs_or_relative_path,
                        all_files_in_same_dir, check_files, infer_path_rel_and_abs_cmds)
from py3toolset.cmd_interact import is_help_switch
from py3toolset.file_backup import work_on_copies
from py3toolset.txt_color import Color, col, print_frame, print_big_frame
from neemuds import ndata_dir_ne


def usage():
    # set script paths needed in usage (which vary depending if the script is in path or
    # not)
    cwd_cmd, other_dir_cmd = infer_path_rel_and_abs_cmds(argv)
    print (col(Color.BLUE, """
--------------------------------------------------------------------
USAGE: """ + cwd_cmd + """ [<DIRECTORY>] <SACZ_file> <RESPZ_file> <SACH1_file> <RESPNH1_file> <SACH2_file> <RESPH2_file> [-d|--ddt value]
Or: """ + cwd_cmd + """ <DIRECTORY> [<SACZ_file> <RESPZ_file> <SACH1_file> <RESPNH1_file> <SACH2_file> <RESPH2_file>] [-d|--ddt value]""") + """

Parameters enclosed by brackets [] are optional parameters.

- DIRECTORY must contain:
    The two SACZ and RESPZ files.
    The four SACN, RESPN and SACE, SACN files.
    If DIRECTORY is set you just need to pass the sac and resp filenames (assuming SAC and RESP files exist in it), but if not you need to pass the full paths of these files (relative or absolute).

--ddt or -dt switch sets the delta value used to decimate the sac traces: if not set, the program will search the value in DELTA.x (in the same directory as your sac file).
    If set, the program will save it to DELTA.x, overriding the previous value.

""" + col(Color.RED, """---------
Examples:
---------""") + """
    """ + col(Color.BLUE, "$") + " " + cwd_cmd + """ """ + ndata_dir_ne + """/sismos/#03_1999.228.23.02 1999.228.23.02.20.0370.II.KDAK.00.BHZ.M.SAC RESP.II.KDAK.00.BHZ 1999.228.23.02.20.0370.II.KDAK.00.BHN.M.SAC RESP.II.KDAK.00.BHN 1999.228.23.02.20.0369.II.KDAK.00.BHE.M.SAC RESP.II.KDAK.00.BHE
    Or, shorter way, with glob patterns:
    """ + col(Color.BLUE, "$") + " " + cwd_cmd + """ """ + ndata_dir_ne + """/sismos/#03_1999.228.23.02 *.BHZ.M.SAC RESP*.BHZ *.BHN.M.SAC RESP*.BHN *.BHE.M.SAC RESP*.BHE

    Or, alternatively, going in the sac files parent folder:
    """ + col(Color.BLUE, "$") + """ cd """ + ndata_dir_ne + """/sismos/#03_1999.228.23.02
    """ + col(Color.BLUE, "$") + " " + other_dir_cmd + """ 1999.228.23.02.20.0370.II.KDAK.00.BHZ.M.SAC RESP.II.KDAK.00.BHZ 1999.228.23.02.20.0370.II.KDAK.00.BHN.M.SAC RESP.II.KDAK.00.BHN 1999.228.23.02.20.0369.II.KDAK.00.BHE.M.SAC RESP.II.KDAK.00.BHE
    Or, with glob patterns:
    """ + col(Color.BLUE, "$") + """ cd """ + ndata_dir_ne + """/sismos/#03_1999.228.23.02
    """ + col(Color.BLUE, "$") + " " + other_dir_cmd + """ *.BHZ.M.SAC RESP*.BHZ *.BHN.M.SAC RESP*.BHN *.BHE.M.SAC RESP*.BHE

    Or, using the default SAC and RESP files specifying just the indirect parent folder:
    """ + col(Color.BLUE, "$") + """ """ + cwd_cmd + """ """ + ndata_dir_ne + """/sismos/#03_1999.228.23.02
    (The default files match the patterns *.BHZ.M.SAC RESP*.BHZ *.BHN.M.SAC RESP*.BHN *.BHE.M.SAC RESP*.BHE)
""")


def preneem_zh(sacz_file, respz_file, sach1_file, sach2_file, resph1_file, resph2_file, dt, answer="", t1="T1", t2="T2"):
    """
    Executes the whole data process for vertical and horizontal components, given the SAC and instrumental response files.
    The final result will be stored in the files RAYZ.sac, RAYL.sac and LOVE.sac in the same folder than SAC files in arguments.
    This function relies on preneem_z(), and preneem_h() to process respectively the vertical and horizontal components.
    Refers to these for more details.
    Nevertheless this function allows users to cut the horizontal and vertical components in one time (seeing also the three components filtered).
    sacz_file -- SAC input to process for the vertical component.
    respz_file -- SAC associated instrumental file.
    sach1_file -- SAC input to process, for North component.
    resph1_file -- SAC associated instrumental file.
    sach2_file -- SAC input to process, for East component.
    resph2_file -- SAC associated instrumental file.
    dt -- The delta for the decimation stage.
    Optional arguments:
    t1 -- Start of the cut in seconds if you don't want to pick the time manually.
    t2 -- End of the cut in seconds if you don't want to pick the time manually.
    answer -- To automatically respond to the questions prompting on terminal (regarding the SAC files backup/restoration).
    """
    print_big_frame("H-and-Z-DATA PROCESSING ")
    work_on_copies(sacz_file, answer=answer)
    work_on_copies(sach1_file, sach2_file, answer="yes")
    print_frame("1. CUTTING THE SIGNALS for Z and H components")
    filcut(sacz_file, sacz_file+"c", sach1_file, sach1_file+"c", sach2_file, sach2_file+"c", deleting_filtered_sacs=True, t1=t1, t2=t2)
    # preneem_z/h() re-does a work_on_copies() but that's not a problem
    # because it works after on the cut file made above
    preneem_z(sacz_file, respz_file, dt, cutting=False, answer="yes",t1=t1, t2=t2)
    preneem_h(sach1_file, resph1_file, sach2_file, resph2_file, dt, answer="yes", cutting=False,t1=t1, t2=t2)

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
            if (isdir(argv[1])):  # first arg is a directory
                sac_dir = argv[1]
                file_arg_pos += 1
            else:
                sac_dir = getcwd()  # may change later
                # if full sac file path passed

            if(argc <= file_arg_pos):
                print_frame("USING DEFAULT Z SAC AND RESP FILES IN: " + sac_dir)
                sacz_file = set_abs_or_relative_path(sac_dir, DEFAULT_ZFILES["SAC"])
                respz_file = set_abs_or_relative_path(sac_dir, DEFAULT_ZFILES["RESP"])
                print_frame("USING DEFAULT H SAC AND RESP FILES IN: " + sac_dir)
                sach1_file = set_abs_or_relative_path(sac_dir, DEFAULT_HFILES["SACH1"])
                sach2_file = set_abs_or_relative_path(sac_dir, DEFAULT_HFILES["SACH2"])
                resph1_file = set_abs_or_relative_path(sac_dir, DEFAULT_HFILES["RESPH1"])
                resph2_file = set_abs_or_relative_path(sac_dir, DEFAULT_HFILES["RESPH2"])
            else:
                sacz_file = set_abs_or_relative_path(sac_dir, argv[file_arg_pos])
                respz_file = set_abs_or_relative_path(sac_dir, argv[file_arg_pos + 1])
                sach1_file = set_abs_or_relative_path(sac_dir, argv[file_arg_pos + 2])
                resph1_file = set_abs_or_relative_path(sac_dir, argv[file_arg_pos + 3])
                sach2_file = set_abs_or_relative_path(sac_dir, argv[file_arg_pos + 4])
                resph2_file = set_abs_or_relative_path(sac_dir, argv[file_arg_pos + 5])

            # expand wildcards in filenames
            sacz_file, respz_file, sach1_file, resph1_file, sach2_file, resph2_file = \
            glob_files(sacz_file, respz_file, sach1_file, resph1_file, sach2_file, resph2_file)

            check_files(sacz_file, respz_file, sach1_file, resph1_file, sach2_file, resph2_file)

            if(not all_files_in_same_dir(sacz_file, respz_file, sach1_file, sach2_file, resph1_file, resph2_file)):
                print("Error: SAC and RESP files must all be in the same parent directory.")
                print("\t\t" + sach1_file + ", " + resph1_file)
                print("\t\t" + sach2_file + ", " + resph2_file)
                usage()
                exit(1)

            # get decimation delta from file if not provided in command line
            # otherwise save it in file
            sac_dir = dirname(sach1_file)
            if(dt == -1):
                dt = read_ddt(sac_dir)
                if (dt == -1):
                    print(col(Color.RED, "Error: no decimation delta defined."))
                    usage()
                    exit()
            else:
                save_ddt(sac_dir, dt)
            print(argv[0]+": dt=" + str(dt))

            # ready to process
            preneem_zh(sacz_file, respz_file, sach1_file, sach2_file, resph1_file, resph2_file, dt)

        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            print(col(Color.RED, str(e)))
            usage()
