#!python
import os
from os.path import expanduser
from posix import remove
from sys import argv
import sys
from tempfile import gettempdir
import traceback

from py3sac.sac import Sac  # , getsacinfo
from py3toolset.file_backup import work_on_copies
from py3toolset.fs import check_file, infer_path_rel_and_abs_cmds
from py3toolset.cmd_interact import is_help_switch
from py3toolset.txt_color import col, Color
from neemuds import ndata_dir_ne


def usage():
    cwd_cmd = infer_path_rel_and_abs_cmds(argv)[0]
    print (col(Color.BLUE, """
--------------------------------------------------------------------
USAGE: """ + cwd_cmd  + """ <trace.sac|.asc> <wave_type> <BP_fmin> <BP_fmax> <mul_factor>

Pre-processes cross-correlation data.
The result trace is intended to be passed to Neemuds afterward.

"""+col(Color.BLUE,"<trace.sac|.asc>")+""" the trace filepath, probing format with file extension (sac for SAC, asc for ASCII -- not implemented yet).
""" +col(Color.BLUE,"<wave_type>")+""" R for Rayleigh, L for Love.
"""+col(Color.BLUE,"<BP_fmin>")+""" BUTTERWORTH filter, BP lower bound frequency (Hz).
"""+col(Color.BLUE,"<BP_fmax>")+""" BUTTERWORTH filter, BP upper bound frequency (Hz).
"""+col(Color.BLUE,"<mulfactor>")+""" multiplication factor.

""" + col(Color.RED, """---------
Example:
---------""") + """
    """ + col(Color.BLUE, "$") + " " + cwd_cmd + " " + ndata_dir_ne+"""/sismos/cc/cc_sum_E137_PY48.sacn R 0.002 0.05 3

    """))


def preprocess_cc_data(trace, fmin, fmax, mul_factor, del_tmp_files=True):
    """
    Pre-processes cross-correlation data.

    Returns a list containing the sac output filepath and the temporary sac filepaths if del_tmp_files is set to False.
    """
    #TODO: args doc
    tmp_prefix=gettempdir()+ os.sep + "cc_"
    tmp_files = [tmp_prefix+str(suffix)+".sac" for suffix in [1, 2]]
    out_file = trace.replace(".sac", "").replace(".SAC", "")+"_cc.sac"
    sac = Sac()
    sac.read(trace)
    print('WARNING: be aware that frequency domain is slightly increased for BP filter')
    fmin *= 0.9
    fmax *= 1.1
    print('fmin=%16.8f Hz fmax=%16.8f'%(fmin,fmax))
    sac.bandpass(npoles=4,passes=2,v1=fmin,v2=fmax)
    sac.write()
#     b = getsacinfo(trace, "B")
#     e = getsacinfo(trace, "E")
    c = 0
    sac.cut(start=c,end="E")
    sac.read(trace)
    sac.write(tmp_files[0])
    sac.cut_off()
    sac.read(trace)
    sac.reverse()
    sac.write(tmp_files[1])
    sac.cut(start=c,end="E")
    sac.read(tmp_files[1])
    sac.write()
    sac.cut_off()
    sac.read(tmp_files[0])
    sac.addf(tmp_files[1])
    sac.mul(mul_factor)
    sac.rtrend()
    sac.rmean()
    sac.taper("COSINE", width=.02)
    sac.write(out_file)
    sac.quit()
    sac.exec(echo=True)
    ret = [out_file]
    if(del_tmp_files):
        {remove(f) for f in tmp_files}
    else :
        ret += tmp_files
    return ret



if __name__ == '__main__':
    if(len(argv) < 6 or is_help_switch(argv[1])):
        usage()
    else:
        try:
            ### get/check all params
            trace = expanduser(argv[1])
            check_file(trace)
            wave_type=argv[2]
            if(wave_type not in ["L" , "R" , "l" , "r"]):
                raise Exception("Error: wave type "+wave_type+" is not valid (must be L or R).")
            bp_fmin = float('{:.6f}'.format(float(argv[3])))
            bp_fmax = float('{:.6f}'.format(float(argv[4])))
#            print(f"bp_min={bp_fmin:.6f}, bp_fmax={bp_fmax:.6f}")
            mul_factor = float(argv[5])
            ###
            work_on_copies(trace)
            preprocess_cc_data(trace, bp_fmin, bp_fmax, mul_factor,del_tmp_files=False)
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            print(col(Color.RED, str(e)))
            usage()
