import numpy as np
from math import log
import os

from py3toolset.txt_color import (
    warn,
    print_big_frame,
    print_frame,
    Color,
    col,
    bold,
    print_center,
)
from py3sac.sac import Sac, getsacinfo, sacio_sac2asc as sac2asc
from py3toolset.fs import remove_files
from py3toolset.nmath import calc_moving_average_list, str_isfloat
from . import load_lib, LIBS_INFO
from os import environ

assert LIBS_INFO[3]["name"].startswith("Gaussianfilter")
installed_from_pip = (
    __file__.count("site-packages") > 0 or __file__.count("dist-packages") > 0
)
if not installed_from_pip:
    load_lib(LIBS_INFO[3])

RUNNING_AVG_MINPTS = 5  # minimum value for the running average

# below is the list of max and min group velocities regarding the scale/planet and wave type
# N.B.: *UMIN/*UMAX are not really constants (they can change dynamically with set_uminmax())
EARTH_RAYL_UMIN = 1.0
EARTH_RAYL_UMAX = 7.0
EARTH_LOVE_UMIN = 1.0
EARTH_LOVE_UMAX = 7.0

MARS_RAYL_UMIN = MARS_LOVE_UMIN = 1.0
MARS_RAYL_UMAX = MARS_LOVE_UMAX = 7.0

LOCAL_RAYL_UMIN = 1.0
LOCAL_RAYL_UMAX = 7.0
LOCAL_LOVE_UMIN = 1.0
LOCAL_LOVE_UMAX = 7.0

# N.B.: UBIN_WIDTH not really a constant, can change with set_ubinwidth()
UBIN_WIDTH = 0.1  # width for U (group vel.) bins
MAX_UBIN_WIDTH = 1
# umin and umax bounds are independent for the PDF (not the same as that used
# for the all the processing before building the PDF ; the next values are only
# used in bin_ufile and can be edited on the command line by option -u)
BIN_UMIN = 1
BIN_UMAX = 7

# NWMIN = 5  # minimum amount of narrow filters
# NWMAX = 40  # maximum amount of narrow filters
SIGFLOGMIN = (
    0.01  # minimum half-width (in log) for gaussian filters (-> which defines nwmax)
)
SIGFLOGMAX = (
    0.05  # maximum half-width (in log) for gaussian filters (should be never reached)
)

# planet equatorial perimeters in km
EARTH_CIRC = 40030.2
MARS_CIRC = 21296.9

WRONG_WAVETRAIN_MSG = "Invalid wavetrain. Must be ma, Ma, o-ma or o-Ma."


class Freq:
    """
    Represents a frequency (f) and its period (T), given the frequency logarithm (flog).
    """

    def __init__(self, flog):
        self.flog = flog
        self.f = 10**flog
        self.T = 1 / self.f


def enforce_fminmax_domain(sac_file, fmin, fmax):
    """
    Returns modified fmin, fmax if needed regarding the sac trace.
    In order to respect Nyquist limit for fmax (f/2, with f the sampling frequency of sac trace).
    Minimizes also fmin to have at least two oscillations at this frequency for the sac trace duration.
    """
    dt = getsacinfo(sac_file, "DELTA")
    nbpt = getsacinfo(sac_file, "NPTS")
    cfmin = 2 / (nbpt * dt)  # critical f (lowest acceptable value)
    cfmax = 1 / (2 * dt)
    if fmin < cfmin:
        fmin = cfmin
        warn("fmin adjusted to its minimal value for this sac trace: " + str(cfmin))
    if fmax > cfmax:
        fmax = cfmax
        warn("fmax adjusted to its maximal value for this sac trace: " + str(cfmax))
    return fmin, fmax


def calc_auto_narrow_filter_amount(fmin, fmax, only_n=True):
    """
    NOTE: this function is deprecated, it was used in a previous version of narrow_filter().
    Auto-calculates narrow filter amount regarding fmin and fmax.
    Returns the computed number of filters (variable n).
    and also dflog and siglog if only_n equals False.
    with dflog = (log(fmax) - log(fmin)) / (n - 1)
    and siglog = dflog/6
    """
    fmaxlog = log(fmax, 10)
    fminlog = log(fmin, 10)
    lenlog = fmaxlog - fminlog
    n = int(lenlog / (SIGFLOGMIN * 6))  # 6 sigmas between two frequencies
    dflog = (fmaxlog - fminlog) / (n - 1)
    sigflog = dflog / 6
    if sigflog > SIGFLOGMAX:
        raise Exception(
            "narrow_filter(): The width of filters will be too large to be used for group velocities."
            "Hint: adjust fmin, fmax to have (log(fmax) - log(fmin) / (n - 1) / 6) >  "
            + SIGFLOGMAX
            + " or set the number of narrow filters manually."
        )
    if only_n:
        return n
    else:
        return n, dflog, sigflog


def narrow_filter(fmin, fmax, sac_file, n=10, verbose=False, gf_trunc=False):
    """
    Narrow (gaussian) filters the SAC trace sac_file.
    Returns two lists with n elements:
    - The 1st contains filenames of SAC traces resulting from filtering (one per band),
    - The 2nd contains the Freq corresponding objects (with attributes for frequency, period and log(frequency).
    Args:
        fmin: min. frequency (for first band).
        fmax: max. frequency (for last band).
        sac_file: SAC trace.
        n: (optional) Number of bands (default is 10).
        verbose: boolean for verbose mode.
        gf_trunc: Optional truncation digits number of sigma and freq.
    """
    from gaussianfilter import gaussianfilter  # python wrapper

    NFWIN_MIN = 6
    NFWIN_MAX = 40
    XSIG = 0.55  # factor to multiply dflog --> width of gaussian filters (if independant data then should not be greater than 0.55)
    # check_executable("gaussianfilter", get_prog_parent_dir() + os.sep + "gaussianfilter", info_msg="gaussianfilter executable not found")
    fmaxlog = log(fmax, 10)
    fminlog = log(fmin, 10)
    if n < NFWIN_MIN:
        print(
            col(Color.RED, bold("Warning:")),
            "number of frequency bands too small --> set to:",
            NFWIN_MIN,
        )
        n = NFWIN_MIN
    elif n > NFWIN_MAX:
        print(
            col(Color.RED, bold("Warning:")),
            "number of frequency bands too large --> set to:",
            NFWIN_MAX,
        )
        n = NFWIN_MAX
    dflog = (fmaxlog - fminlog) / (n - 1)
    sigflog = dflog * XSIG  # sigma value around each central freq value
    filog = fminlog
    freqs = []
    fsac_traces = []
    print_frame(
        "Narrow Filtering n=" + str(n) + " fmin=" + str(fmin) + " fmax=" + str(fmax)
    )
    if verbose:
        print(
            "fmax="
            + str(fmax)
            + " Hz, Tmin="
            + str(1 / fmax)
            + " s, fmaxlog="
            + str(fmaxlog)
        )
        print(
            "fmin="
            + str(fmin)
            + " Hz, Tmax="
            + str(1 / fmin)
            + " s, fminlog="
            + str(fminlog)
        )
    for i in range(1, n + 1):
        str_index = str("0" * (len(str(n)) - len(str(i))) + str(i))
        nb = Freq(filog)
        if verbose:
            print("line # %d : filog=%f, fi=%f Hz, Ti=%f s" % (i, nb.flog, nb.f, nb.T))
        sigma = abs(10 ** (filog - sigflog) - 10 ** (filog + sigflog))
        if gf_trunc:
            nb.f = int(nb.f * 10**gf_trunc) / 10**gf_trunc
            nb.T = 1 / nb.f
            sigma = int(sigma * 10**gf_trunc) / 10**gf_trunc
        out_sac_file = sac_file.replace(".sac", "") + str_index + ".sac"
        # subprocess.call(["gaussianfilter", 's2s', sac_file, str(nb.f), str(sigma), out_sac_file])
        gaussianfilter("s2s", sac_file, out_sac_file, nb.f, sigma)
        if verbose:
            print(
                "gaussianfilter "
                + "s2s "
                + sac_file
                + " "
                + str(nb.f)
                + " "
                + str(sigma)
                + " "
                + out_sac_file
                + "\n"
            )
        filog += dflog
        freqs.append(nb)
        fsac_traces += [out_sac_file]
    print_center(col(Color.GREEN, bold("[DONE]")))
    return freqs, fsac_traces


def get_uminmax(scale, wavetype, adjust_with_ubinwidth=False):
    """
    Returns umin, umax values for a specific scale and wave type.

    See the underlying constants EARTH_LOVE_UMIN, etc. in header of module.

    scale -- "earth", "mars" or "local".
    wavetype -- "rayl" or "love".
    """
    ubinwidth = UBIN_WIDTH  # binning value for U
    if scale.lower() == "mars":
        if wavetype.lower() == "love":
            umin, umax = MARS_LOVE_UMIN, MARS_LOVE_UMAX
        else:  # rayl
            umin, umax = MARS_RAYL_UMIN, MARS_RAYL_UMAX
    elif scale.lower() == "earth":
        if wavetype.lower() == "love":
            umin, umax = EARTH_LOVE_UMIN, EARTH_LOVE_UMAX
        else:  # rayl
            umin, umax = EARTH_RAYL_UMIN, EARTH_RAYL_UMAX
    elif scale == "local":
        if wavetype.lower() == "love":
            umin, umax = LOCAL_LOVE_UMIN, LOCAL_LOVE_UMAX
        else:  # rayl
            umin, umax = LOCAL_RAYL_UMIN, LOCAL_RAYL_UMAX
    if adjust_with_ubinwidth:
        # modify values in order to match desired value after binning
        umax += ubinwidth / 2
        umin -= ubinwidth / 2
    return umin, umax


def get_umin(scale, wavetype, adjust_with_ubinwidth=True):
    """
    Helper function to get just umin from get_uminmax().
    scale -- "earth", "mars" or "local".
    wavetype -- "rayl" or "love".
    """
    return get_uminmax(scale, wavetype, adjust_with_ubinwidth)[0]


def get_umax(scale, wavetype, adjust_with_ubinwidth=True):
    """
    Helper function to get just umax from get_uminmax().
    scale -- "earth", "mars" or "local".
    wavetype -- "rayl" or "love".
    """
    return get_uminmax(scale, wavetype, adjust_with_ubinwidth)[1]


def set_uminmax(scale, wavetype, umin, umax):
    """
    Changes the default values of constants *UMIN, *UMAX (declared in module header).

    scale -- "earth", "mars" or "local".
    wavetype -- "rayl" or "love".
    umin -- New value for *UMIN constant.
    umax -- New value for *UMAX constant.
    """
    global MARS_LOVE_UMIN, MARS_LOVE_UMAX, MARS_RAYL_UMIN, MARS_RAYL_UMAX, EARTH_LOVE_UMIN, EARTH_LOVE_UMAX, EARTH_RAYL_UMIN, EARTH_RAYL_UMAX, LOCAL_LOVE_UMIN, LOCAL_LOVE_UMAX, LOCAL_RAYL_UMIN, LOCAL_RAYL_UMAX
    if umin >= umax:
        raise Exception(
            "Error set_uminmax(): umin must be strictly lower than umax."
            " Given values are umin=" + str(umin) + " umax=" + str(umax)
        )
    if scale.lower() == "mars":
        if wavetype.lower() == "love":
            MARS_LOVE_UMIN, MARS_LOVE_UMAX = umin, umax
        else:  # rayl
            MARS_RAYL_UMIN, MARS_RAYL_UMAX = umin, umax
    elif scale.lower() == "earth":
        if wavetype.lower() == "love":
            EARTH_LOVE_UMIN, EARTH_LOVE_UMAX = umin, umax
        else:  # rayl
            EARTH_RAYL_UMIN, EARTH_RAYL_UMAX = umin, umax
    elif scale == "local":
        if wavetype.lower() == "love":
            LOCAL_LOVE_UMIN, LOCAL_LOVE_UMAX = umin, umax
        else:  # rayl
            LOCAL_RAYL_UMIN, LOCAL_RAYL_UMAX = umin, umax


def set_bin_uminmax(bin_umin, bin_umax):
    global BIN_UMIN, BIN_UMAX
    BIN_UMIN = bin_umin
    BIN_UMAX = bin_umax


def set_ubinwidth(ubwidth):
    """
    Changes the default value for UBIN_WIDTH.
    """
    global UBIN_WIDTH
    if ubwidth > MAX_UBIN_WIDTH:
        raise Exception(
            "Error set_ubinwidth(): too big value for ubinwidth."
            " Given value is "
            + str(ubwidth)
            + "and max value is "
            + str(MAX_UBIN_WIDTH)
        )
    UBIN_WIDTH = ubwidth


def get_ubinwidth():
    """
    Returns the bin width for U in histogram.
    """
    return UBIN_WIDTH


def build_updf(
    scale,
    narrow_fil_amount,
    fmin,
    fmax,
    dist,
    wavetype,
    sac_file,
    wavetrain,
    t1a="T1",
    t2a="T2",
    t1b="T1",
    t2b="T2",
    timing=False,
):
    """
    Processes all needs to build UPDF.

    Output file :
        pdf_frq_file = "U" + wavetype[0].upper() + "pdffrq.xyz"

    scale -- "local", "mars" or "earth".
    narrow_fil_amount -- number of bands/narrow filters.
    fmin -- (only for global scale) Start of frequency range for Mineos (Hz). The frequency really used in mineos input is 0.9*fmin.
    fmax -- (only for global scale) End of frequency range for Mineos (Hz). The frequency really used in mineos input is 1.2*fmin.
    wavetype -- "rayl" or "love".
    sac_file -- SAC trace to base computation of UPDF on.
    wavetrain -- ma, Ma, o-ma, o-Ma
    t1a -- T1 time for fsac_traces[0] (where fsac_traces is the list of SAC traces produced by narrow_filter()),
           by default it'll be picked manually through SAC.
    t2a -- T2 time for fsac_traces[0], picked with SAC if not specified.
    t1b -- T1 time for fsac_traces[-1].
    t2b -- T2 time for fsac_traces[-1].
    """
    t1a, t2a, t1b, t2b = (
        try_getting_times_from_env()
    )  # for reproducing time pickings if set in the environment (testing purpose)
    print_big_frame("Building of U Probability Density Function")
    sac = Sac()
    sac.read(sac_file)
    sac.rtrend()
    sac.rmean()
    sac.taper()
    sac.write()
    sac.quit()
    sac.exec(echo=True)
    if scale == "local":
        pdf_frq_file = "U" + wavetype[0].lower() + "pdffrq.xyz"
    else:
        wt_str = ""
        if wavetrain == "ma":
            wt_str = "1"
        elif wavetrain == "Ma":
            wt_str = "2"
        elif wavetrain == "o-ma":
            wt_str = "3-1"
        elif wavetrain == "o-Ma":
            wt_str = "4-2"
        pdf_frq_file = "U" + wavetype[0].lower() + wt_str + "pdffrq.xyz"
    if wavetrain in ["ma", "Ma"] and getsacinfo(sac_file, "O") is None:
        # raise Exception(sac_file+" must contain field O in its header because wavetrain option is: "+wavetrain+".")
        Ofield = None
        while Ofield is None or not str_isfloat(Ofield):
            print(
                "No origin time was found in SAC file header (O field). Please enter"
                " a valid event origin time (in seconds): ",
                end="",
            )
            Ofield = input()
        sac = Sac()
        sac.read(sac_file)
        sac.chnhdr(Ofield=float(Ofield))
        sac.writehdr()
        sac.quit()
        sac.exec()
        warn("Ofieldrigin time " + Ofield + " added in header of SAC file: " + sac_file)
    freqs, fsac_traces = narrow_filter(
        fmin, fmax, sac_file, narrow_fil_amount, verbose=False, gf_trunc=8
    )

    if scale == "local":
        # TODO: freqs not necessary
        calc_local_scale_T1T2(fsac_traces, freqs, dist, scale, wavetype)
    else:
        if wavetrain in ["o-ma", "o-Ma"]:
            ppktype = "o"
            pickT1T2(sac_file, fsac_traces, wavetrain, scale, wavetype, ppktype, dist)
        ppktype = "p"
        pickT1T2(sac_file, fsac_traces, wavetrain, scale, wavetype, ppktype, dist)

    # taper + temporal whitening + envelopes --------
    sac = Sac()
    for i, fsac in enumerate(fsac_traces):
        t1 = getsacinfo(fsac, "t1")
        t2 = getsacinfo(fsac, "t2")
        sac.cut(t1, t2)
        sac.read(fsac)
        sac.mul(0)
        sac.add(1)
        sac.taper()
        sac.write(fsac + "t")
        sac.cut_off()
        sac.read(fsac)
        sac.envelope()
        sac.write()
    sac.quit()
    sac.exec(echo=True)

    # convert into ascii and paste (head/tail) in order to taper the envelope files
    delta = getsacinfo(sac_file, "delta")
    fsac_nrj_xy = []
    for i, fsac in enumerate(fsac_traces):
        sac2asc(fsac, "/tmp/foo.xy")
        fsac_xy = np.loadtxt("/tmp/foo.xy")
        fsact_xy = fsac_xy.copy()
        tt = fsact_xy[0, 0]
        ttmin = tt - 0.6 * delta
        ttmax = tt + 0.6 * delta
        tt = fsac_xy[fsac_xy[:, 0] <= ttmax]
        tt = tt[tt[:, 0] >= ttmin][:, 0]
        nhead = np.argmin(np.abs(fsac_xy[:, 0] - tt))
        head_xy = fsac_xy[:nhead]  # null part of the signal
        head_xy[:, 1] = 0
        tt = fsact_xy[-1, 0]
        ttmin = tt - 0.6 * delta
        ttmax = tt + 0.6 * delta
        tt = fsac_xy[fsac_xy[:, 0] <= ttmax]
        tt = tt[tt[:, 0] >= ttmin][:, 0]
        ntail = np.argmin(np.abs(fsac_xy[:, 0] - tt)) + 1
        nnln = fsac_xy.shape[0]
        # ntail = nnln - ntail
        tail_xy = fsac_xy[ntail:]  # null part of the signal
        n = head_xy.shape[0] + fsact_xy.shape[0] + tail_xy.shape[0]
        if n != nnln:
            raise Exception("Pb with n, nnln checking.")
        foo_xy = np.vstack((head_xy, fsact_xy, tail_xy))
        foot_xy = foo_xy.copy()
        foot_xy[:, 1] = np.square(foot_xy[:, 1])  # taper is applied
        npts = max(int(freqs[i].T / delta), 2)
        print("running_avg T=", freqs[i].T, "s", "npts=", npts)
        foo_xy = np.array(
            calc_moving_average_list(foot_xy[1:], npts, x_start=int((npts + 1) / 2))
        )
        # force values to be positive
        foo_xy[foo_xy[:, 1] < 0, 1] = 0
        fsac_nrj_xy += [foo_xy]

    # convert into group velocities pdf (normalization by the sum after linear interpolation in U)
    umin, umax = get_uminmax(scale, wavetype)
    ubinwidth = get_ubinwidth()
    updf = np.empty((0, 3))
    for i, fsac in enumerate(fsac_traces):
        f = freqs[i].f
        fnrj = fsac_nrj_xy[i]
        if scale == "local":
            otime = 0
        elif wavetrain in ["o-ma", "o-Ma"]:
            otime = getsacinfo(fsac, "t0")
        else:
            otime = getsacinfo(fsac, "o")
        gvels_u = fnrj[fnrj[:, 0] - otime > 0.1]
        gvels_u[:, 0] = dist / (gvels_u[:, 0] - otime)
        I = np.argsort(gvels_u[:, 0], axis=0)
        gvels_u = gvels_u[I]
        gvels_u_interpo = np.empty((0, 2))
        j1 = 0
        j2 = 1
        u1 = gvels_u[j1, 0]
        u2 = gvels_u[j2, 0]
        uref = umin
        while u1 < umax and uref < umax and j2 < gvels_u.shape[0] - 1:
            if u2 <= uref:
                j1 += 1
                j2 += 1
                u1 = gvels_u[j1, 0]
                u2 = gvels_u[j2, 0]
            else:
                interpo_u = np.array(
                    [uref, np.linspace(gvels_u[j1, 1], gvels_u[j2, 1], 3)[1]]
                )
                gvels_u_interpo = np.vstack((gvels_u_interpo, interpo_u))
                uref += ubinwidth
        s = np.sum(gvels_u_interpo[:, 1])
        gvels_u_interpo[:, 1] = gvels_u_interpo[:, 1] / s
        fs = np.empty((gvels_u_interpo.shape[0], 1))
        fs[:] = f
        gvels_u_interpo = np.hstack((fs, gvels_u_interpo))
        updf = np.vstack((updf, gvels_u_interpo))
        updf = regularize_updf(updf)
        if len(updf) == 0:
            raise ValueError(
                "The UPDF is empty, verify the frequency domain or" " the time picking."
            )
        np.savetxt(pdf_frq_file, updf, fmt="%16.8f")

    print_big_frame("Output file: " + pdf_frq_file, centering=False)
    remove_files(*fsac_traces)


def _find_longest_vel_series(updf):
    # utility function to find (cf. regularize_updf) the longest of series of
    # increasing velocities in updf[:,1] (remember that they are repeated
    # along the PDF)
    v = updf[:, 1]
    # find longest serie lvs
    i = 0
    j = 1
    lsij = [i, j]
    while j < len(v):
        while j < len(v) and v[i] < v[j]:
            j += 1
        if j <= len(v):
            if lsij[1] - lsij[0] < j - i:
                lsij = [i, j]
            i = j
            j = i + 1
    lsv = v[lsij[0]: lsij[1]]
    return lsv


def regularize_updf(updf):
    """
    Regularizes with zero probabilities for the UPDF to have the same number of rows for all frequencies.
    """
    lsv = _find_longest_vel_series(updf)
    #    print(lsv)
    # add missing zero prob (freq, vels) rows
    for frq in np.unique(updf[:, 0]):
        I = np.arange(len(updf))
        frq_rows = I[updf[:, 0] == frq]
        b = frq_rows[0] - 1  # before
        a = frq_rows[-1] + 1  # after freq rows
        #        print(len(frq_rows), len(lsv))
        if len(frq_rows) < len(lsv):
            new_updf_rows = np.zeros((len(lsv) - len(frq_rows), 3))
            new_updf_rows[:, 0] = updf[b + 1, 0]
            new_updf_rows[:, 1] = lsv[len(frq_rows): len(lsv)]
            new_updf_rows = np.vstack((updf[frq_rows], new_updf_rows))
            assert len(new_updf_rows) == len(lsv)
            new_updf = np.vstack((updf[0: b + 1], new_updf_rows, updf[a: len(updf)]))
            updf = new_updf
    #    np.savetxt('new_updf.txt', updf, fmt="%16.8f")
    return updf


def try_getting_times_from_env():
    from os import environ as env

    # try to get T1, T2 times from environment (useful for debugging/testing)
    flist = ["T1A", "T2A", "T1B", "T2B"]
    if all([var in env.keys() for var in flist]):
        t1a, t2a, t1b, t2b = [float(env[f]) for f in flist]
    else:
        # not in env, set vars to strs meaning we'll pick times manually through sac
        (t1a, t2a), (t1b, t2b) = [("T1", "T2") for i in range(2)]
    return t1a, t2a, t1b, t2b


def calc_local_scale_T1T2(fsac_traces, freqs, dist, scale, wavetype):
    """
    This function computes T1 and T2 automatically in the case of local scale.

    Args:
        fsac_traces: the filenames of the traces returned by narrow_filter (gaussian filters).
        freqs: the frequencies (Freq objects) corresponding to the fsac_traces.
        dist: epicentral distance.
        scale: must always be 'local' here.

    """
    if scale.lower() != "local":
        raise ValueError("calc_T1T2_for_local_scale handle only local scale case.")
    otime = 0  # cross-correlation => origin time set to zero
    umin, umax = get_uminmax(scale, wavetype)
    T1 = dist / umax
    T2 = dist / umin
    sac = Sac()
    sac.qdp("off")
    for sac_trace in fsac_traces:
        sac.read(sac_trace)
        sac.chnhdr(T1=T1)
        sac.chnhdr(T2=T2)
        sac.chnhdr(T0=otime)
        sac.write()
    sac.quit()
    sac.exec(echo=False)


def pickT1T2(osac_trace, fsac_traces, wavetrain, scale, wavetype, ppktype, dist):
    """
    This function picks T1 and T2 (for the origin time and real T1, T2 and depending of the wavetrain).

    Args:
        osac_trace: original SAC trace (which band filtering result is fsac_traces).
        fsac_traces: trace results of osac_trace's narrow filters (see narrow_filter()).
        scale: must be not be local.
        wavetrain: ma, Ma, o-ma, o-Ma
        ppktype: 'o' for origin time case and 'p' for the T1, T2 picking case.
        dist: epicentral distance.

    Environment variables:
        T1A, T2A for the first trace and T1B, T2B for the last trace allow to
        skip manual picking by setting values before script execution (it is
        thought to make automatic tests).

    Outputs:
        The fsac_traces are modified, precisely their headers to set T1 and T2
        arrival times.
    """
    auto = (
        "T1A" in environ and "T2A" in environ and "T1B" in environ and "T2B" in environ
    )
    if auto:
        T1A = float(environ["T1A"])
        T2A = float(environ["T2A"])
        T1B = float(environ["T1B"])
        T2B = float(environ["T2B"])

    pickT1T2_debug = (
        "PICKT1T2_DEBUG" in os.environ.keys() and os.environ["PICKT1T2_DEBUG"] == "1"
    )
    scale = scale.lower()
    nfwin = len(fsac_traces)
    delta = getsacinfo(osac_trace, "delta")

    if scale == "local":
        raise ValueError(
            "this function is dedicated to global scale case (earth, mars, ...)"
        )

    # indices of the five traces we use
    q = nfwin / 4
    inds = [0, q - 1, q * 2 - 1, q * 3 - 1, nfwin - 1]
    inds = [int(i) for i in inds]

    sac = Sac()
    sac.qdp("OFF")
    sac.color(on=True, increment=True, inc_list="BLACK BLUE BLACK BLACK BLACK BLUE")

    if ppktype == "p" and wavetrain in ["o-ma", "o-Ma"]:
        for i in [0, -1]:
            # get the otime computed in a previous call of pickT1T2
            sac.read(fsac_traces[inds[i]])
            otime = getsacinfo(fsac_traces[inds[i]], "T0")
            umin, umax = get_uminmax(scale, wavetype)
            T1 = otime + dist / umax
            T2 = otime + dist / umin
            if pickT1T2_debug:
                print("dist u1 u2 otime", dist, umin, umax, otime)
                print("T1, T2=", T1, T2)
            # chndr writes the headers for all the open files
            sac.chnhdr(T1=T1)
            sac.chnhdr(T2=T2)
            sac.write()

    sac.read(osac_trace, *[fsac_traces[inds[i]] for i in range(5)])

    if ppktype == "o":
        sac.taper()
        sac.envelope()
        otitle_start = "otime computation: pick "
        otitle_end = " with T1 and T2 on traces #2 and #6 (+ on other traces if needed) - raw data on top - Q to quit"
        if wavetrain == "o-ma":
            sac.title(
                "R3/L3 " + otitle_start + " R1/L1" + otitle_end,
                location="bottom",
                size="small",
            )
        elif wavetrain == "o-Ma":
            sac.title(
                "R4/L4 " + otitle_start + " R2/L2" + otitle_end,
                location="bottom",
                size="small",
            )
        # if wavetrain in ['ma', 'Ma', 'o-ma', 'o-Ma']:
    elif ppktype == "p":
        ptitle = "T1 and T2 mandatory for traces #2 and #6 - additional pick T1 and/or T2 on other traces if needed - raw data on top - Q to quit"
        if wavetrain == "ma":
            sac.title("R1/L1: " + ptitle, location="bottom", size="small")
        elif wavetrain == "Ma":
            sac.title("R2/L2: " + ptitle, location="bottom", size="small")
        elif wavetrain == "o-ma":
            sac.title("R3/L3: " + ptitle, location="bottom", size="small")
        elif wavetrain == "o-Ma":
            sac.title("R4/L4: " + ptitle, location="bottom", size="small")

    if not auto:
        sac.ppk(bell="off")
    foo_files = ["/tmp/foo" + str(i) + ".sac" for i in range(5)]
    # maybe already existing, delete them
    remove_files(*foo_files)
    sac.write("/tmp/foo.sac", *foo_files)
    sac.quit()
    sac.exec(echo=pickT1T2_debug)

    if auto:
        for sacf, ptimes in zip(
            [foo_files[0], foo_files[-1]], [(T1A, T2A), (T1B, T2B)]
        ):
            sac = Sac()
            sac.read(sacf)
            sac.chnhdr(T1=ptimes[0])
            sac.chnhdr(T2=ptimes[1])
            sac.writehdr()
            sac.quit()
            sac.exec()

    j = 0  # counts the mandatory picks (foo0.sac, foo4.sac)
    pickls = [[], []]  # first list for T1 picks, second for T2'
    for i, foofile in enumerate(foo_files):
        t1 = getsacinfo(foofile, "t1")
        t2 = getsacinfo(foofile, "t2")
        if i == 0 or i == 4:  # first or last traces
            if t1 is not None and t2 is not None:
                pickls[0] += [foofile]
                pickls[1] += [foofile]
                j += 1
            else:
                print(col(Color.RED, "cannot find T1 and T2 in" + str(foofile)))
        else:  # i == 1, 2, or 3
            if t1 is not None:
                pickls[0] += [foofile]
            if t2 is not None:
                pickls[1] += [foofile]
    print(col(Color.GREEN, "pickls:" + str(pickls)))

    if j < 2:
        raise Exception(
            "You must pick T1 and T2 at least in the first and last " "traces."
        )

    # linearly interpolates T1 and T2 for all nfwin traces according to the points
    # picked by user
    interpo_pts = np.empty(
        (nfwin, 3)
    )  # columns 0: sac trace index, 1: T1 list, 2: T2 list
    interpo_pts[:, 0] = np.arange(nfwin)
    test = (
        "PICKT1T2_TEST" in os.environ.keys()
        and os.environ["PICKT1T2_TEST"] == "1"
        and ppktype == "o"
    )
    if test:
        test_ts = [[7644.21484, 8124.99561], [11660.15234, 10613.74512]]
    for tj, tname in [(0, "t1"), (1, "t2")]:
        for i in range(len(pickls[tj]) - 1):
            foofile1 = pickls[tj][i]
            foofile2 = pickls[tj][i + 1]
            if pickT1T2_debug:
                print("foofile1=", foofile1, "foofile2=", foofile2)
            if test:
                tj_1 = test_ts[tj][i]
                tj_2 = test_ts[tj][i + 1]
            else:
                tj_1 = getsacinfo(foofile1, tname)
                tj_2 = getsacinfo(foofile2, tname)
            i1 = int(foofile1.split("foo")[1].split(".")[0])
            i2 = int(foofile2.split("foo")[1].split(".")[0])
            if pickT1T2_debug:
                print("%% tj=", tj, "i1=", i1, "i2=", i2)
            i1 = inds[i1]
            i2 = inds[i2]
            if pickT1T2_debug:
                print("%% i1=", i1, "i2=", i2)
                print("%% tj_1=", tj_1, "tj_2=", tj_2)
            # computes all intermediate points of traces by lin. interpolation
            if i == 0:
                interpo_pts[i1: i2 + 1, 1 + tj] = np.linspace(tj_1, tj_2, i2 - i1 + 1)
            else:
                interpo_pts[i1 + 1: i2 + 1, 1 + tj] = np.linspace(
                    tj_1, tj_2, i2 - i1 + 1
                )[
                    1:
                ]  # i1 time was already added in previous iteration

    if pickT1T2_debug:
        print("%% interpo_pts=", interpo_pts)

    # Write picks either on traces or on copy for otime computation:
    fsacls = []
    sac = Sac()
    sac.qdp("OFF")
    for i in range(nfwin):
        fsac = fsac_traces[i]
        fcpsac = fsac_traces[i].split(".sac")[0] + "cp.sac"
        sac.read(fsac)
        t1, t2 = interpo_pts[i, 1:]
        if pickT1T2_debug:
            print("t1=", t1, "t2=", t2)
        sac.chnhdr(T1=t1)
        sac.chnhdr(T2=t2)
        if ppktype == "o":
            sac.taper()
            sac.envelope()
            sac.write(fcpsac)
            fsacls += [fcpsac]
        elif ppktype == "p":
            sac.write()
            fsacls += [fsac]
    sac.quit()
    sac.exec(echo=pickT1T2_debug)

    if pickT1T2_debug:
        print("%% fsacls=", fsacls)
        for fsac in fsacls:
            print("%%fsac:", fsac)
            print("%% T1, T2", getsacinfo(fsac, "T1"), getsacinfo(fsac, "T2"))

    # Pick checking with possibility to modify them (last run)
    sac = Sac()
    sac.qdp("OFF")
    sac.read(*fsacls)
    sac.title(
        "Check and modify T1 and/or T2 if signal is cut by automatic picks - Q TO QUIT",
        location="bottom",
        size="small",
    )
    if not auto:
        sac.ppk(bell="OFF")
    sac.write()
    sac.quit()
    sac.exec(echo=pickT1T2_debug)

    if pickT1T2_debug:
        for fsac in fsacls:
            print("%%fsac:", fsac)
            print("%% T1, T2", getsacinfo(fsac, "T1"), getsacinfo(fsac, "T2"))

    if ppktype == "o":
        # compute the origin time for --o-ma|--o-Ma
        sac = Sac()
        for i in range(nfwin):
            fcpsac = fsac_traces[i].split(".sac")[0] + "cp.sac"
            sac.read(fcpsac)
            sac.cut("T1", "T2")
            sac.read(fcpsac)
            sac.taper()
            sac.write()
            sac.cut_off()
        sac.quit()
        sac.exec(echo=pickT1T2_debug)

        for i, fcpsac in enumerate(fsacls):
            fsac = fsac_traces[i]
            sac2asc(fcpsac, "/tmp/foo.xy")
            xy = np.loadtxt("/tmp/foo.xy")
            xo2 = xy[np.argmax(xy[:, 1]), 0]  # position of the maximum
            xy_1 = np.empty(xy.shape)
            xy_1[:, 0] = xy[:, 0]
            xy_1[0, 1] = xy[0, 1]
            xy_1[1:, 1] = (xy[1:, 1] - xy[:-1, 1]) / (xy[1:, 0] - xy[:-1, 0])
            xy_1[2:, 1] = xy_1[2:, 1] * xy[1:-1, 1]
            xy_1 = xy_1[2:, :]
            xy_1 = xy_1[xy_1[:, 1] <= 0]
            xy_1[:, 1] = np.sqrt((xy_1[:, 0] - xo2) ** 2)
            xo1 = (
                xy_1[np.argmin(xy_1[:, 1])][0] - delta
            )  # position of the extremum which gives the lowest difference (sqrt of the square difference in order to take into account before and after cases) - should be the same as xo2 or very close
            if pickT1T2_debug:
                print(fcpsac, "xo1=", xo1, "xo2=", xo2)
            if np.sqrt((xo2 - xo1) ** 2) <= delta * 2:
                sac.read(fsac)
                sac.chnhdr(T0=xo1)
                sac.write()
            else:
                raise Exception(
                    "pickT1T2 - perhaps something went wrong in the detection of origin time"
                    + "(i="
                    + str(i)
                    + ") xo1="
                    + str(xo1)
                    + " vs xo2="
                    + str(xo2)
                )
        sac.quit()
        sac.exec(echo=False)
