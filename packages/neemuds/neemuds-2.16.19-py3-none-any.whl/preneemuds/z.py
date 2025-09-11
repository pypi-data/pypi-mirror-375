import os
from os.path import dirname, isdir, basename
from posix import getcwd
import re
from shutil import move
from sys import argv
import traceback, sys

from preneemuds.preneem import filcut, remove_instru_resp, decimate
from preneemuds.ddt import save_ddt, read_ddt, parse_ddt
from py3toolset.file_backup import work_on_copies
from py3toolset.fs import glob_files, all_files_in_same_dir, check_files
from py3toolset.cmd_interact import is_help_switch
from py3toolset.txt_color import Color, col, print_frame, print_big_frame

# Min frequency for instrumental response deconvolution ONLY
FMIN = .001666  # (T = 600 s)
FMAX = .0333  # (T = 30 s)

def preneem_z(sac_file, resp_file, dt, t1="T1", t2="T2", answer="", fmin=FMIN, fmax=FMAX, cutting=True):
    """
    Executes the whole data process for the vertical component, given the SAC and instrumental response files.
    The final result will be stored in the file RAYZ.sac in the current working directory.
    There are five steps: 0. SAC backup, 1. Signal window time cut, 2. Instrumental response deconvolution, 3. Decimation, 4. Saving file result.
    sac_file -- SAC input to process.
    resp_file -- SAC associated instrumental file.
    dt -- The delta for the decimation stage.
    Optional arguments:
    t1 -- Start of the cut in seconds if you don't want to pick the time manually.
    t2 -- End of the cut in seconds if you don't want to pick the time manually.
    answer -- To automatically respond to the questions prompting on terminal (regarding the SAC files backup/restoration).
    fmin -- Min. frequency used for instrumental deconvolution (FMIN by default).
    fmax -- Max. frequency used for instrumental deconvolution (FMAX by default).
    cutting -- Set it to False if you want to skip the cut stage for the signal.
    """
    print_big_frame("Z-DATA PROCESSING " + basename(sac_file) + ", " + basename(resp_file) +
                "\n\t\t (from " + (dirname(sac_file) or "./") + ")")
    print_frame("0. BACKUP")
    work_on_copies(sac_file, answer=answer)
    check_files(sac_file, resp_file)
    pdir = dirname(sac_file)
    if(re.match(pdir, r"\s") != None): pdir = "."
    cut_sac_file = sac_file + 'c'
    if(cutting):
        print_frame("1. CUTTING THE SIGNAL")
        filcut(sac_file, cut_sac_file, t1=t1, t2=t2, deleting_filtered_sacs=True)
        # print('Offset time=' + t1 + ' End time=' + t2) # to decomment this,
                                                        # set t1,t2 to filcut() returned tuple
    # else: the function assumes that the cut sac trace has been created before elsewhere
    print_frame("2. REMOVING INSTRUMENTAL RESPONSE")
    remove_instru_resp(cut_sac_file, resp_file, fmin, fmax)
    # TODO : variable for sac filename
    print_frame("3. DECIMATION")
    decimate(cut_sac_file, dt)
    move(cut_sac_file, "RAYZ.sac")
    print_frame("4. OUTPUTTING FILE IN " + "RAYZ.sac")

