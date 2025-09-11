from math import cos, pi, sin
from os.path import os, dirname
from posix import remove
from shutil import move

from py3sac.sac import Sac, getsacinfo


# filcut() constants (for filtering)
FILMIN = 0.002
MAX_FILMIN = 0.01

def filcut(sac_file, cut_sac_file,
           sac_file2=None, cut_sac_file2=None,
           sac_file3=None, cut_sac_file3=None,
           t1="T1", t2="T2", filmin=FILMIN, deleting_filtered_sacs=False):
    """
    Using SAC, Plots filtered sac files (except if t1 and t2 specified) and cuts sac traces on t1 and t2.
    sac_file -- The sac file to filter and cut.
    fil_sac_file --  The filtered output sac file.
                     The filtering is a bandpass bessel, done with sac command:
                     bandpass bessel corners filmin 0.01 passes 2 npoles 4
    cut_sac_file -- The cut output sac file.
    Optional arguments:
    filmin -- corner lower frequency for filtering (default is FILMIN)
    t1 -- start time for cutting (by default, picked by user).
    t2 -- end time for cutting (by default, picked by user).
    sac_file2 -- Optional second file to cut (as the same time points than sac_file).
    cut_sac_file2 -- Output sac file for cut sac_file2.
    sac_file3 -- Optional third file to cut (as the same time points than sac_file).
    cut_sac_file3 -- Output sac file for cut sac_file3.
    """
    def get_fil_name(cut_sacname):
        if(cut_sacname != None): return cut_sacname +"f"
        return None
    def lcut(sacf, cut_sacf, t1, t2):
        sac.cut(t1, t2)
        sac.read(sacf)
        sac.write(cut_sacf)
    def check_filmin():
        if(filmin > MAX_FILMIN): raise Exception("filcut(): filmin argument is too high. Max value is: "+str(MAX_FILMIN))
    ######## filter
    fil_sac_file = get_fil_name(cut_sac_file)
    fil_sac_file2 = get_fil_name(cut_sac_file2)
    fil_sac_file3 = get_fil_name(cut_sac_file3)
    check_filmin()
    sac = Sac()
    # if sac_file2/3 == None, Sac.read/write() will ignore them
    sac.read(sac_file, sac_file2, sac_file3)
    sac.bandpass("bessel", 4, 2, filmin, 0.01)
    sac.write(fil_sac_file, fil_sac_file2, fil_sac_file3)
    sac.quit()
    sac.exec(echo=True)
    ######### cut
    if(t1 == "T1" or t2 == "T2"):
        sac.qdp("off")
        sac.read(sac_file, sac_file2, sac_file3, fil_sac_file, fil_sac_file2, fil_sac_file3)
        sac.title(
            ("R1, R2 and R3 BETWEEN T1 and T2: PICK T1 AND T2 ON THE UPPER TRACE "
             "- PRESS Q TO USE DEFAULT VALUES B AND E"), "bottom", "small")
        sac.ppk("off")
        sac.write()
        sac.quit()
        sac.exec(echo=True)
        t1, t2 = getsacinfo(sac_file, "T1"), getsacinfo(sac_file, "T2")
    for sacf, cut_sacf in zip([sac_file, sac_file2, sac_file3],
                                      [cut_sac_file, cut_sac_file2, cut_sac_file3]):
        if(sacf):
            lcut(sacf, cut_sacf, t1, t2)
    sac.quit()
    sac.exec(echo=True)
#     for cut_sacf in [cut_sac_file, cut_sac_file2, cut_sac_file3]:
#         if(cut_sacf): sac2asc(cut_sacf)
    if(deleting_filtered_sacs):
        for fil_sacf in [fil_sac_file, fil_sac_file2, fil_sac_file3]:
            if(fil_sacf): remove(fil_sacf)
    return t1, t2

def remove_instru_resp(sac_file, resp_file, fmin, fmax):
    """
    Using SAC TRANSFER command, does an instrument response removal on sac_file trace regarding seed response RESP_FILE.
    The four TRANSFER frequency limits are defined with fmin and fmax as: fmin * .9, fmin * .95, fmax * 1.1, fmax * 1.2.
    The deconvoluated trace is written in sac_file.
    """
    sac = Sac()
    sac.read(sac_file)
    sac.rmean()
    sac.taper("cosine", .05)
    sac.transfer("evalresp", "none", [fmin * .9, fmin * .95, fmax * 1.1, fmax * 1.2],
                 {"fname" : resp_file})
    sac.div(1e3)
    sac.write()
    sac.quit()
    sac.exec(echo=True)

def decimate(sac_file, dt):
    """
    Performs a decimation on sac_file, using dt parameter and SAC decimate command.
    The decimated trace is written in sac_file.
    """
    delta = int(float(getsacinfo(sac_file, "DELTA")) * 1000) / 1000
    dt = float(dt)
    dd = int(dt / delta)
    if(dd > 1):
        sac = Sac()
        sac.read(sac_file)
        while(dd != 1):
            for i in range(7, 1, -1):
                #print(str(dd) + " " + str(i))
                r = dd % i
                if(r == 0):
                    sac.decimate(i)
                    dd /= i
                    #print("dd=" + str(dd))
                    if(dd < 1):
                        print("Error: problem with the decimation cascade computation.")
                        return False
                    break
    sac.write(sac_file)
    sac.quit()
    sac.exec(echo=True)

def check_orthogonality(nsac_file, esac_file):
    """
    Checks orthogonality of two sac traces.
    nsac_file -- north/first sac trace.
    esac_file -- east/first sac trace.
    """
    aza = float(getsacinfo(nsac_file, "CMPAZ"))
    azb = float(getsacinfo(esac_file, "CMPAZ"))
    #print("difaz="+str(90-abs(aza-azb)))
    if abs(90-abs(aza-azb)) > 0.1:
        raise Exception('N and E components must be orthogonal, please correct'
                        'your SAC (including metadata CMPAZ field).')

def rotate(angle, in_sac_files, out_sac_files):
    """
    Rotates SAC traces (SAC rotate command). It must be horizontal components.
    angle -- Angle in degrees.
    in_sac_files -- list of input sac traces to rotate.
    out_sac_files -- list of output sac files corresponding to the input (same order).
    """
    sac = Sac()
    sac.read(*in_sac_files)
    sac.rotateTo(angle)
    sac.write(*out_sac_files)
    sac.quit()
    sac.exec(echo=True)
