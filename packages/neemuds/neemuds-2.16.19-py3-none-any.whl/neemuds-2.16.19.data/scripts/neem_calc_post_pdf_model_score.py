#!python

from sys import argv
import numpy as np
from numpy.linalg import norm
from sys import stderr
from typing import Callable
from py3toolset.txt_color import r, g, b, bold
from py3toolset.fs import infer_path_rel_and_abs_cmds

# mineos columns
# NOTE: qk, qs, are never used here
MINEOS_COLS = {'radius': 0, 'RHO': 1, 'VPv': 2, 'VSv': 3, 'qk': 4, 'qs': 5,
               'VPh': 6, 'VSh': 7, 'ETA': 8}

# srfdis96/Herrmann format
# NOTE: qs is never used here
SRFDIS96_COLS = {'z': 0, 'VPv': 1, 'VSv': 2, 'RHO': 3, 'qs': 4}


def usage():
    """
    Prints script usage.
    """
    cwd_cmd = infer_path_rel_and_abs_cmds(argv)[0]
    print(bold(r("USAGE:")), end=' ')
    print(bold(r(cwd_cmd)), b("<post-pdf.txt>"), b("<model.txt>"))
    print("\tComputes the score of a model according to a McMC"
          " posterior PDF.")
    print("\tThree values are provided for the score: the sum of the")
    print("post-probabilities along depth, their median and mean.")
    print("\t", b("post-pdf.txt"), "is a file output from " +
          bold(r("neemuds_plot_Xpost_pdf.py")) +
          " (e.g. VPv_full_hist.txt).")
    print()
    print(bold(g('EXAMPLE:')))
    print(bold(r("./neem_calc_post_pdf_model_score.py")),
          b("~/16_procs-neemuds_benchmarks/2023-05-05-16procs/best-pdf/"
            "VPv_full_hist.txt"),
          b("~/16_procs-neemuds_benchmarks/2023-05-05-16procs/best-pdf/"
            "1544_neemuds-out_07-2336.txt"))
    print("Detected parameter: VPv")
    print("Mineos global scale model detected in"
          " ~/16_procs-neemuds_benchmarks/2023-05-05-16procs/best-pdf/"
          "1544_neemuds-out_07-2336.txt")
    print(bold("score (sum/median/mean)"), ": 2062.053 4.859 5.925\r\n")
    print()


def get_param_from_post_pdf(pdff):
    """
    Get parameter name from post-pdf pdff.

    The pdff is normally from neemuds_plot_Xpost_pdf.py (e.g
    VPv_full_hist.txt).

    Returns:
        Parameter name (VPv, VSv, etc.).
    """
    with open(pdff) as pdfd:
        row = pdfd.readline()
        if row.startswith("#"):
            param = row.split()[1]
            print("Detected parameter:", param)
        else:
            raise Exception("Couldn't detect parameter of interest from"
                            " header of " + pdff)
    return param


def get_nfields_in_mineos_mod(modf):
    """
    Returns the number of fields in header and in model body of mineos model
    modf.
    """
    with open(modf) as mfd:
        mod = mfd.readlines()  # model rows
        nh = len(mod[1].split())  # number of fields in header of mineos file
        nf = len(mod[-1].split())  # number of fields in depth model
    return nh, nf


def is_mineos_model(modf):
    """
    Detects non-formally that modf is a mineos model.
    """
    nh, nf = get_nfields_in_mineos_mod(modf)
    return nh != nf and nf == 9


def is_srfdis96_model(modf):
    """
    Detects non-formally that modf is a srdis96/Herrmann model.
    """
    mod = np.loadtxt(modf)
    return mod.shape[1] == 5


def mineos_zp_ite(mod: np.ndarray,
                  z1: float,
                  z2: float,
                  param: str):
    """
    Iterates on a mineos model from depth z1 to depth z2.

    Args:
        mod: the mineos model to iterate on.
        z1: (m) first depth bound to start iteration.
        z2: (m) last depth bound to stop iteration (included).
        param: the parameter of interest (see MINEOS_COLS).

    Returns:
        (z, p) item.
    """
    pla_r = mod[-1][0]  # planet radius
    r1, r2 = pla_r - z1, pla_r - z2
    mod_r = mod[:, 0]  # model radii
    # z1 <= z2 => r1 >= r2
    # get all model param points enclosed in depth z1, z2
    rp = mod[(r2 <= mod_r) & (mod_r <= r1)][:, [0, MINEOS_COLS[param]]]
    for rad, p in rp[::-1]:  # increasing z
        yield pla_r - rad, p


def srfdis96_zp_ite(mod: np.ndarray,
                    z1: float,
                    z2: float,
                    param: str):
    """
    Iterates on a srfdis96/Herrmann model from depth z1 to depth z2.

    Args:
        mod: the srfdis96/Herrmann model to iterate on.
        z1: (m) first depth bound to start iteration.
        z2: (m) last depth bound to stop iteration (included).
        param: the parameter of interest (see SRFDIS96_COLS).

    Returns:
        (z, p) item.
    """
    z1_km = z1 / 1000
    z2_km = z2 / 1000
    # depths are in km in mod
    for z, p in mod[(mod[:, 0] >= z1_km) &
                    (mod[:, 0] <= z2_km)][:, [0, SRFDIS96_COLS[param]]]:
        yield z, p


def calc_model_zprobs(pdf: np.ndarray,
                      mod: np.ndarray,
                      param: str,
                      zp_ite: Callable,
                      verbose=False) -> np.ndarray:
    """
    Calculates one probability for each z in model mod for parameter param.

    The probability is calculated by interpolation of the probabilies of the
    enclosing points found in pdf for each param(z).

    Args:
        pdf: posterior pdf for parameter param.
        mod: the model to get the probabilities (one at each z).
        param: parameter name (VPv, VSv, etc.).
        zp_ite: iterator on mod (z, p) points.

    Returns:
        2d array: 1st column for z, 2nd for corresponding probabilities.

    """
    pdfz = pdf[:, 1]  # pdf z's
    pdfzu = np.unique(pdfz)  # unique z series
    pdfnp = len(pdfz) // len(pdfzu)  # pdf param dim size
    zpr = []  # model prob wrt z
    for zi, (z1, z2) in enumerate(zip(pdfzu[0:-1], pdfzu[1:])):
        # get pdf param values and probs at depths z1, z2
        pdf_z1_pp = pdf[pdfnp * zi: pdfnp * (zi + 1)][:, [0, 2]]
        pdf_z2_pp = pdf[pdfnp * (zi + 1): pdfnp * (zi + 2)][:, [0, 2]]
        for z, p in zp_ite(mod, z1, z2, param):
            # get indices of pdf param vals enclosing p at depths z1 and z2
            ip1 = len(pdf_z1_pp[pdf_z1_pp[:, 0] <= p]) - 1
            if ip1 < 0:
                # p is out of param interval at depth z of pdf
                pr = 0
            else:
                ip2 = ip1 + 1
                p1 = pdf_z1_pp[ip1, 0]
                p2 = pdf_z1_pp[ip2, 0]
                assert p1 <= p and p <= p2
                # get probs of four points of pdf that enclose (z, p)
                pr1 = pdf_z1_pp[ip1, 1]
                pr2 = pdf_z2_pp[ip1, 1]
                pr3 = pdf_z1_pp[ip2, 1]
                pr4 = pdf_z2_pp[ip2, 1]
                # calc inv of dists between (z, p) and those points
                id1 = 1 / norm((z - z1, p - p1))
                id2 = 1 / norm((z - z2, p - p1))
                id3 = 1 / norm((z - z1, p - p2))
                id4 = 1 / norm((z - z2, p - p2))
                # calc (z, p) prob as interpolation of pr<i>'s
                s = np.sum([id1, id2, id3, id4])
                pr = (pr1 * id1 + pr2 * id2 + pr3 * id3 + pr4 * id4) / s
            if verbose:
                print("z=", z, "pr=", pr)
            zpr += [[z, pr]]
    zpr = np.array(zpr)
    return zpr


if __name__ == '__main__':
    narg = len(argv)
    if narg < 3:
        usage()
        exit(narg > 1)
    pdff = argv[1]  # post-pdff file
    modf = argv[2]  # model file
    param = get_param_from_post_pdf(pdff)
    if is_mineos_model(modf):
        print("Mineos global scale model detected in", modf)
        zp_ite = mineos_zp_ite
    elif is_srfdis96_model(modf):
        print("Srfdis96/Herrmann local scale model detected in", modf)
        zp_ite = srfdis96_zp_ite
    else:
        print("Cannot handle other model format than"
              " Mineos/srfdis96-Herrmann models'",
              file=stderr)
        exit(3)
    mod = np.loadtxt(modf, skiprows=3)  # mineos model without hdr
    # for each modf z find enclosing z's in pdff
    # and compute param prob interpolating those two z's probs
    pdf = np.loadtxt(pdff)
    zpr = calc_model_zprobs(pdf, mod, param, zp_ite)
    print(bold("score (sum/median/mean):"), "%.3f" % np.sum(zpr[:, 1]),
          "%.3f" % np.median(zpr[:, 1]),
          "%.3f" % np.mean(zpr[:, 1]))
