#!python

from getopt import getopt
import os
from os.path import dirname, exists, basename
from re import split
from sys import argv
import sys
import traceback
from shutil import copyfile

from neemuds import BASH_AUTOCOMP_SCRIPT, ndata_dir_ne
from neemuds.updf import build_updf, get_uminmax, set_uminmax,\
    enforce_fminmax_domain, calc_auto_narrow_filter_amount, set_ubinwidth,\
    EARTH_CIRC, MARS_CIRC, set_bin_uminmax
from py3toolset.bash_autocomp import propose_bashautocomp
from py3toolset.file_backup import work_on_copies, ask_yes_or_no
from py3toolset.fs import (check_file, get_prog_parent_dir,
                        infer_path_rel_and_abs_cmds)
from py3toolset.cmd_interact import contains_help_switch, contains_switch
from py3toolset.txt_color import col, Color, bold, frame, print_frame, warn


def about():
    print(
    frame("About this program") + """
        Neemuds stands for Nonlinear Explorations of Elastic Models Using Dispersive Signals.
        It explores the dispersion of surface waves by McMC in terms of 1D velocity models
        (with or without anisotropy, using Herrmann for local or Mineos for global)
        Authors: Éric Beucler, Mélanie Drilleau, Ianis Gaudot, Antoine Mocquet.
        Ported from Bash to Python by Hakim Hadj-Djilani (hakim.lpgn at gmail dot com).
    """)

def examples():
    # set cmd to use in usage
    cwd_cmd = infer_path_rel_and_abs_cmds(argv)[0]
    print(frame("EXAMPLES", Color.RED) + """
    """ + col(Color.BLUE, "$") + " " + col(Color.RED,bold(cwd_cmd)) + " "+col(Color.RED,bold("-s"))+" Earth "+col(Color.RED,bold("-d"))+" 40030.2 "+col(Color.RED,bold("-r"))+" "+col(Color.RED,bold("-n"))+" 20 "+col(Color.RED,bold("-f"))+" 0.00250:.0250 "+col(Color.RED,bold("-u"))+" 1:6 "+ col(Color.RED,bold("--o-ma")) + " "+ndata_dir_ne+"""/sismos/2006319BFOBHZ.sac
    which is equivalent to the command: """ + col(Color.BLUE, "$") + " " + col(Color.RED,bold(cwd_cmd)) +" "+  col(Color.RED,bold("-p"))+" params "+ndata_dir_ne+"""/sismos/2006319BFOBHZ.sac
    where `params' file contains:"""+col(Color.GREEN,"""
        scale=Earth
        dist=40030.2
        rayl
        narrow-filter-amount=20
        freqs=0.00250:.0250
        uminmax=1:6
        o-ma""")+"""
    Or you can use the interactive mode which will ask you all these values:
    """+ col(Color.BLUE, "$") + " " + col(Color.RED,bold(cwd_cmd)) +" "+  col(Color.RED,bold("-i"))+"""
    Example for local scale (working on a sac file resulting from """+col(Color.RED,bold("preneem_cc.py"))+""" pre-processing):
    """+ col(Color.BLUE, "$") + " " + col(Color.RED,bold(cwd_cmd)) + " "+col(Color.RED,bold("-s"))+" local "+col(Color.RED,bold("-d"))+" 697.148804 "+col(Color.RED,bold("-r"))+" "+col(Color.RED,bold("-n"))+" 20 "+col(Color.RED,bold("-f"))+" 0.002:0.05 "+col(Color.RED,bold("-w"))+" .05 "+ndata_dir_ne+"""/sismos/cc/cc_sum_E137_PY48n_cc.sac
    """)

def usage():
    # set cmd to use in usage
    cwd_cmd = infer_path_rel_and_abs_cmds(argv)[0]
    print (frame("USAGE") + """

Alternative ways of use:""" + col(Color.BLUE, """

    1/ """ + col(Color.RED, bold(cwd_cmd)) + " "+
col(Color.RED, bold("-s|--scale")) + " Mars|Earth|local [" +
col(Color.RED, bold("-n|--narrow-filter-amount")) + " <integer>] " +
col(Color.RED, bold("-f|--freqs")) + " <min_number>[:<max_number>] " +
col(Color.RED, bold("-d|--dist")) + " <km_number> " +
col(Color.RED, bold("--ma|--Ma|--o-ma|--o-Ma ")) +
col(Color.RED, bold("-r|--rayl|-l|--love")) +
" [" + col(Color.RED, bold("-g|--globnorm")) + " <number>] " +
" [" + col(Color.RED, bold("-u|--uminmax")) + " <min_number>:<max_number> ]" +
" [" + col(Color.RED, bold("-w|--ubinwidth")) + " <number_km/s> ]" +
" [" + col(Color.RED, bold("-t|--timer")) + "]" +" <trace.sac|.asc> " + """
    2/ """ + col(Color.RED, bold(cwd_cmd + " -i|--interactive")) + """
    3/ """ + col(Color.RED, bold(cwd_cmd + " -p|--file-params")) + """ <file> <trace.sac|.asc>
    4/ """ + col(Color.RED, bold(cwd_cmd + " -e|--examples")) + """
    5/ """ + col(Color.RED, bold(cwd_cmd + " -a|--about")) + """
    6/ """ + col(Color.RED, bold(cwd_cmd + " -h|--help|--details"))) + """

    Syntax notes:
        - Parameters enclosed by brackets (`[]') are optional parameters (not mandatory).
        - The pipe character `|' represents an alternative between two options or values.
          For example, `-s|--scale' means that you can use -s (short option) or --scale (long option).
        - The chevron characters `<>' designate a value the user has to set.
          The inner text gives sense to this value.
 """)

def details():
    usage()
    print("""    Usage details:
        """ + col(Color.BLUE, "1/") + """ """ + col(Color.RED, bold(argv[0])) + """
    """ + col(Color.BLUE, "\t<trace.sac|.asc>") + """ the trace filepath, format is probed through file extension (sac for SAC, asc for ASCII -- not implemented yet).
    """ + col(Color.RED, bold("\t-s|--scale")) + col(Color.BLUE, " Mars|Earth|local") + """ the scale of work, Earth, Mars, or local (values not case sensitive).
    """ + col(Color.RED, bold("\t-n|--narrow-filter-amount")) + col(Color.BLUE, " <integer>") + """ amount of narrow filters (optional parameter, if not set or less or equal than zero, then the program will compute it auto.).
    """ + col(Color.RED, bold("\t-f|--freqs")) + col(Color.BLUE, " <min_number>[:<max_number>]") + """ the frequency (Hz) range to be computed by Mineos for global scale, specified like this fmin:fmax.""" +
    """ It's also used for narrow filters (fmin only) for both global and local scales. In the latter you can specify only fmin (if fmax specified, it will be ignored).
    """ + col(Color.RED, bold("\t-d|--dist")) + col(Color.BLUE, " <km_number>") + """ the event-station distance in km.
    """ + col(Color.RED, bold("\t--ma|--Ma|--o-ma|--o-Ma")) + """ the targeted wavetrain temporal window.
    Option meanings:
    --ma: minor arc (e.g. R1 for rayleigh)
    --Ma: Major arc (e.g. R2 for rayleigh),
    --o-ma: orbit minus minor arc (e.g. R3-R1 for rayleigh),
    --o-Ma: orbit minus major arc (e.g. R4-R2 for rayleigh).
    N.B.: these options are case sensitive.
    Extra environment variable: PLOT_WHITENING=1 will enable a visual "debug mode" for option --ma and --Ma. The whitening operation will be plotted for each frequency band.
    """ + col(Color.RED, bold("\t-r|--rayl|-l|--love")) + """ the wave type (Rayleigh or Love).
    """ + col(Color.RED, bold("\t-g|--globnorm")) + col(Color.BLUE, " <number>") + """ (not mandatory) global normalization, 0 for strong to  3 for smooth. """ + col(Color.RED, "[DEPRECATED, NOT IMPLEMENTED]") + """
    """ + col(Color.RED, bold("\t-u|--uminmax")) + col(Color.BLUE, " <min_number>[:<max_number>]") + """ (optional) PDF umin and umax to override default values.
    """ + col(Color.RED, bold("\t-w|--ubinwidth")) + col(Color.BLUE, " <number_km/s>") + """ (optional) bin width for U in histogram.
    """ + col(Color.RED, bold("\t-t|--timer")) + col(Color.BLUE, "") + """ (optional) enables computation timing for band processing (CPU profiling).

        """ + col(Color.BLUE, "2/") + " " + col(Color.RED, bold(argv[0] + " -i|--interactive")) + """
            This is an interactive mode in which options/parameters are asked directly to user.
            However the options of mode """ + col(Color.BLUE, "1/") + """ can be used concurrently and will be prioritary if so done.

        """ + col(Color.BLUE, "3/") + " " + col(Color.RED, bold(argv[0] + " -p|--file-params")) + " " + col(Color.BLUE, "<file>  <trace.sac|.asc>") + """
            This is a file mode. All parameters are set from the file specified.
            However the options of mode """ + col(Color.BLUE, "1/") + """ can be used concurrently and will be prioritary if so done.

            Syntax of parameter file is straight-forward, the typical line is of the form: option_name=value.
            Where `option_name' is one of the mode """ + col(Color.BLUE, "1/") + """ options.
            For example:
                scale=Earth
                dist=40000
                rayl
            The last one line option has no value, that's just a switch.

        """ + col(Color.BLUE, "4/") + " " + col(Color.RED, bold(argv[0] + " -e|--examples")) + """ shows command line examples.

        """ + col(Color.BLUE, "5/") + " " + col(Color.RED, bold(argv[0] + " -a|--about")) + """ displays information about this program.

        """ + col(Color.BLUE, "6/") + " " + col(Color.RED, bold(argv[0] + " -h|--help|--details")) + """ displays this help message,
        --details switch gives detailed help.
""")
    examples()

def warn_opt_override(short_opt=None, long_opt=None):
    if(short_opt):
        msg = " option -" + short_opt +"|"
    else:
        msg = "option "
    if(long_opt):
        warn(msg+"--" + long_opt + " set more than once. Overriding old value.")

def parse_opts(opts):
    global scale, narrow_fil_amount, fmin, fmax, dist, wavetype, globnorm, interactive, \
           param_file, umin, umax, ubinwidth, wavetrain, timer
    for opt, val in opts:
        if(opt in ("-s", "--scale")):
            if (scale) : warn_opt_override("s", "scale")
            scale = val
            check_opt("scale")
        elif(opt in ("-n", "--narrow-filter-amount")):
            if (narrow_fil_amount) : warn_opt_override("n", "narrow-filter-amount")
            narrow_fil_amount = val
            check_opt("narrow_fil_amount")
        elif(opt in ("-f", "--freqs")):
            if(fmin): warn_opt_override("f", "freqs")
            if(":" in val and not val.endswith(":")):
                fmin, fmax = split(":", val)
                check_opt("fmax")
            else:
                fmin = val.replace(":", "")
                check_opt("fmin")
        elif(opt in ("-u", "--uminmax")):
            if(umin): warn_opt_override("u", "uminmax")
            if(":" in val and not val.endswith(":")):
                umin, umax = split(":", val)
                check_opt("uminmax")
        elif(opt in ("-w", "--ubinwidth")):
            if(ubinwidth): warn_opt_override("w", "ubinwidth")
            ubinwidth = val
            check_opt("ubinwidth")
        elif(opt in ("-d", "--dist")):
            if(dist): warn_opt_override("d", "dist")
            dist = val
            check_opt("dist")
        elif(opt in ("-r", "--rayl")):
            if(wavetype): warn_opt_override("r|-l", "rayl|--love")
            wavetype = "RAYL"
        elif(opt in ("-l", "--love")):
            if(wavetype): warn_opt_override("r|-l", "rayl|--love")
            wavetype = "LOVE"
        elif(opt in ("-g", "--globnorm")):
            if(globnorm): warn_opt_override("g", "globnorm")
            globnorm = val
            check_opt("globnorm")
        elif(opt in ("-i", "--interactive")):
            interactive = True
        elif(opt in ("-p", "--file-params")):
            param_file = val
        elif(opt in ("--ma", "--Ma", "--o-ma", "--o-Ma")):
            if(wavetrain): warn_opt_override(long_opt="--ma|--Ma|--o-ma|--o-Ma")
            wavetrain = opt.replace("--", "")
        elif(opt in ["--timer", "-t"]):
            timer = True

def parse_file_opts(param_file):
    for line in open(param_file):
        if("=" in line and not line.endswith("=")):
            opt, value = line.split("=")
            if(opt in [long_opt.replace("=", "") for long_opt in long_opts]):
                parse_opts([("--" + opt, value.strip())])
        else:
            parse_opts([("--" + line.strip(), "")])

def print_params():
    print_frame("PARAMETERS")
    for p in ["sac_file", "scale", "wavetype", "dist", "fmin", "fmax",
              "narrow_fil_amount", "globnorm", "umin", "umax", "ubinwidth",
              "wavetrain", "timer" ]:
        if(eval(p) != None):
            print(p + " = " + str(eval(p)))

def check_opt(opt):
    global sac_file, scale, narrow_fil_amount, fmin, fmax, dist, wavetype, \
           globnorm, interactive, param_file, umin, umax, ubinwidth, \
            wavetrain, timer
    if(opt == "scale"):
        scale = str(scale).lower()
        if(scale not in ("mars", "earth", "local")): raise Exception("Scale must be Earth, Mars or local.")
    elif(opt == "narrow_fil_amount"):
        narrow_fil_amount = int(narrow_fil_amount)
    elif(opt == "fmin"):
        fmin = float(fmin)
        if(fmax != None and float(fmax) <= fmin): raise Exception("min freq. must be lower than max freq.")
    elif(opt == "fmax"):
        fmax = float(fmax)
        if(fmin != None and fmax <= float(fmin)): raise Exception("max freq. must be greater than min freq.")
    elif(opt == "uminmax"):
        umin = float(umin)
        umax = float(umax)
        if(umax != None and umax <= umin): raise Exception("umin must be lower than umax.")
    elif(opt == "ubinwidth"):
        ubinwidth = float(ubinwidth)
    elif(opt == "dist"):
        dist = float(dist)
    elif(opt == "globnorm"):
        globnorm = int(globnorm)
    elif(opt == "wavetype"):
        if(wavetype.upper() not in ["RAYL", "LOVE"]):
                raise Exception("Wave type must be RAYL or LOVE.")
    elif(opt == "sac_file"):
        check_file(sac_file)
        if(sac_file.lower().endswith("asc")):
            raise Exception("ASC format not handled yet.")
        if(not sac_file.lower().endswith("sac")):
            raise Exception("A sac filename must end with .sac extension. Invalid file: " + sac_file)

def check_mandatory_opts(interactive):
    global sac_file, scale, narrow_fil_amount, fmin, fmax, dist, wavetype, \
            globnorm, param_file
    gen_msg = "mandatory parameter not set: "
    if(not sac_file):
        if(interactive):
            sac_file = input("Enter sac file path (No shell special char. or variable) : ")
        else:
            raise Exception(gen_msg + " sac file")
    check_opt("sac_file")
    if(not scale):  # and narrow_fil_amount and fmin and (fmax or scale == "local") )):
        if(interactive):
            scale = input("Enter scale (Mars/Earth/local): ")
        else:
            raise Exception(gen_msg + " scale (-s|--scale).")
    check_opt("scale")
    if(not fmin):
        if(interactive):
            fmin = input("Enter fmin: (float, Hz): ")
            check_opt("fmin")
        else:
            raise Exception(gen_msg + " min frequency (-f|--freqs).")
    check_opt("fmin")
    if(not fmax and scale != "local"):
        if(interactive):
            fmax = input("Enter fmax: (float, Hz): ")
            check_opt("fmax")
        else:
            raise Exception(gen_msg + " max frequency (-f|--freqs).")
    check_opt("fmax")
    if(not dist):
        if(wavetrain in ["o-ma", "o-Ma"]):
            if(scale.lower() == "earth"):
                dist = EARTH_CIRC
            elif(scale.lower() == "mars"):
                dist = MARS_CIRC
        elif(interactive):
            dist = input("Enter distance : (float, km): ")
            check_opt("dist")
        else:
            raise Exception(gen_msg + " distance (-d|--dist).")
    check_opt("dist")
    if(not wavetype):
        if(interactive):
            wavetype = input("Enter wave type: (RAYL, LOVE): ")
            check_opt("wavetype")
        else:
            raise Exception(gen_msg + " wave type (-r|--rayl|-l|--love).")
    check_opt("wavetype")
    if(not wavetrain and scale != "local" ):
        raise Exception(gen_msg + " you must set a wave train to work on "
                "with one option among: --ma, --Ma, --o-ma, --o-Ma.")

def check_not_mandatory_opts(interactive):
    #TODO: umin, umax and ubinwidth should be at their default values if user just type enter on prompt
    global globnorm, umin, umax, narrow_fil_amount, ubinwidth, timer, scale, wavetype
    if(interactive):
        if(not globnorm):
            globnorm = input("Enter global normalization (integer or enter for disabling): ")
            if(globnorm):
                check_opt("globnorm")
            else:
                globnorm = None
        if(not umin or not umax):
            umin, umax = input("Enter umin, umax values (separated by a blank character) : ").split()
            check_opt("uminmax")
        if(not ubinwidth):
            ubinwidth = input("Enter ubinwidth: ")
            check_opt("ubinwidth")
    if(not umin or not umax):
        # user didn't set values, get back default ones
        umin, umax = get_uminmax(scale, wavetype)
    else:
        set_uminmax(scale, wavetype, umin, umax) # overwriting the default values
        umin, umax = get_uminmax(scale, wavetype) # adjusted values
        set_bin_uminmax(umin, umax) # U domain bounds for the final PDF
    if(ubinwidth): set_ubinwidth(ubinwidth)
    if(interactive):
        if(not narrow_fil_amount):
            narrow_fil_amount = input("Enter narrow filter amount: (integer or enter for automatic way): ")
    if(not narrow_fil_amount):
        narrow_fil_amount = calc_auto_narrow_filter_amount(fmin,fmax)
    else:
        check_opt("narrow_fil_amount")
        if(narrow_fil_amount <= 0):
            narrow_fil_amount = calc_auto_narrow_filter_amount(fmin,fmax)



short_opts = "s:n:f:d:rlg:ip:eahu:w:t"
long_opts = ["scale=", "narrow-filter-amount=",
                        "freqs=", "uminmax=", "ubinwidth=", "dist=", "rayl", "love", "globnorm=",
                        "interactive", "file-params=",
                        "examples", "about", "help", "details", "ma",
                        "Ma", "o-ma", "o-Ma",
                        "timer" ]

scale = None
narrow_fil_amount = None
fmin = None
fmax = None
dist = None
wavetype = None
wavetrain = None
globnorm = None
interactive = None
param_file = None
sac_file = None
timer = False



umin, umax = None, None
ubinwidth = None

if __name__ == '__main__':
    try:
        propose_bashautocomp(BASH_AUTOCOMP_SCRIPT)
        opts, remaining = getopt(argv[1:], short_opts, long_opts)
        r_len = len(remaining)
        if(contains_switch(None, "details", argv[1:])):
            details()
        elif (len(argv) < 2 or contains_help_switch(argv[1:])):
            usage()
        elif (contains_switch("e", "examples", argv[1:])):
            examples()
        elif (contains_switch("a", "about", argv[1:])):
            about()
        else:
#             check_neemuds_deps() # dependencies are auto-tested on import stage
            # prog deps ok
            parse_opts(opts)
            if(param_file): parse_file_opts(param_file)
            if(r_len > 0):
                sac_file = remaining[0]
                check_opt("sac_file")
                if(r_len > 1): warn("Remaining command line arguments ignored: " + repr(remaining[1:r_len]))
            check_mandatory_opts(interactive)
            check_not_mandatory_opts(interactive)
            fmin, fmax = enforce_fminmax_domain(sac_file, fmin, fmax)
            print_params()
            orig_sac_file = sac_file
            sac_file = orig_sac_file.replace(".sac",
                                             "-tmp.sac").replace(".SAC",
                                                                 "-tmp.SAC")
            copyfile(orig_sac_file, sac_file)
            warn("Original file: "+orig_sac_file+" copied to :"+sac_file+" (original file won't be touched, "+basename(argv[0])+" will work on the copy).")
            build_updf(scale, narrow_fil_amount, fmin, fmax, dist, wavetype,
                    sac_file, wavetrain, timing=timer)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        msg = str(e)
        if(not msg.lower().startswith("error")):
            msg = "Error: " + msg
        print_frame(msg, Color.RED, centering=False)
        print(col(Color.GREEN, "Use -h, --help option for help (--details for detailed help)."))
