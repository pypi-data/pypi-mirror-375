#!python
from os import environ
environ['DONT_NEED_SAC'] = '1'
from neemuds.updf import (gen_neg_perturbation_mod, HIGH, LOW,
                          gen_neg_perturb_mod_with_coeffs,
                          derivate_mod_from_prem)
from getopt import getopt
from py3toolset.fs import infer_path_rel_and_abs_cmds
from py3toolset.txt_color import col, Color, bold, print_frame  # , frame, warn
from os.path import exists
from neemuds.params import parse_params_conf_file
from neemuds.planet_params import PlanetParams, RefModRadiusCoeff
from sys import argv
from re import search, match
from os.path import basename
from numpy import (loadtxt, linspace, savetxt, array, ndarray, allclose, zeros,
                   hstack, vstack, ones, all)
import matplotlib.pyplot as plt

long_opts = ["from-planet-conf=", "prem-file=", "lo=", "hi=", "plot",
             "vs2vp=", "vp2rho=", "layer-thickness=", "help"]
short_opts = "c:p:l:h:t:"

planet_conf_file = None
planet = None
planet_radius = None
prem_file = None
lo, hi = None, None
cwp_lo = None
cwp_hi = None
lin_lo = None
lin_hi = None
bz_lo = None
bz_hi = None
zmods_lo = None
zmods_hi = None
plotting = False
layer_thickness = None

flt_regx = r"([+-]?(\d+(\.\d*)?)|(\.\d+))"
cwp_regexp = (r"^cwp:((\s*"+flt_regx+r"\s*;\s*"+flt_regx+r",?\s*)?"
              r"\s*("+flt_regx+r",\s*){7}("+flt_regx+",?))+$")
lin_regexp = r"lin:((\s*"+flt_regx+r",)*(\s*"+flt_regx+"){1})"
fpair_regx = r"("+flt_regx+r",\s*"+flt_regx+")"
bz_regexp = \
        r"bz:"+fpair_regx+":"+fpair_regx + \
        "(;"+fpair_regx+"(:"+fpair_regx+")?){1,}"
zmod_regexp = r"zmod_files:(([^,]+,){2}([^,]+)((,[^,]+){4})*?)$"

DEFT_VP2RHO_COEFFS = [.328, .328]
DEFT_VP2RHO_OFFSETS = [768, 768]
DEFT_VS2VP_COEFFS = [1.73205080, 1.73205080]
DEFT_VS2VP_OFFSETS = [0, 0]
vs2vp_coeffs = DEFT_VS2VP_COEFFS
vs2vp_offsets = DEFT_VS2VP_OFFSETS
vp2rho_coeffs = DEFT_VP2RHO_COEFFS
vp2rho_offsets = DEFT_VP2RHO_OFFSETS  # kg/m^3

NPOINTS_PER_BCURVE = 100


def parse_opts(opts):
    global planet_conf_file, prem_file, lo, hi, vs2vp_coeffs,\
            vp2rho_coeffs, layer_thickness
    for opt, val in opts:
        if(opt in ["--from-planet-conf", "-c"]):
            planet_conf_file = val
            check_opt(opt)
        elif(opt in ["--prem-file", "-p"]):
            prem_file = val
            check_opt(opt)
        elif(opt in ["--lo", "-l"]):
            lo = val
            check_opt(opt)
        elif(opt in ["--hi", "-h"]):
            hi = val
            check_opt(opt)
        elif(opt in ["--plot"]):
            check_opt(opt)
        elif(opt == "--vs2vp"):
            # dirty tmp storage
            vs2vp_coeffs = val
            check_opt(opt)
        elif(opt == "--vp2rho"):
            # dirty tmp storage
            vp2rho_coeffs = val
            check_opt(opt)
        elif(opt in ["--layer-thickness", "-t"]):
#            print("parse_opts() layer_thickness=", val)
            layer_thickness = val
            check_opt(opt)


def check_file_exists(fp):
    if(not exists(fp)):
        raise Exception("The file "+fp+" doesn't exist or is"
                        " not readable.")


def split_colon_separated_list(l: str) -> list:
    sl = l.split(":")
    return [list(eval(sl[0])), list(eval(sl[1]))]


def parse_lin_arg(arg: str):
    z_vs = arg.replace("lin:", "")
    # separate depth and VS
    lin = split_colon_separated_list(z_vs)
    z = lin[0].copy()
    z.sort()
    if(z != lin[0]):
        raise ValueError("z-depths must be set in ascending order.")
    return lin


def parse_bz_arg(arg: str):
    arg = arg.replace("bz:", "")
    grad = None
    grad_sp = None
    z_coords = []
    vs_coords = []
    grad_coords = []
    for curve_def in arg.split(";"):
        point_grad = curve_def.split(":")
        point = point_grad[0]
        if(len(point_grad) == 1 and grad is None):
            raise ValueError("At least one gradient must be specified in bz"
                             " def.")
        elif(len(point_grad) > 1):
            grad = point_grad[1]
            grad_sp = grad.split(',')
        point = point.split(',')
        z_coords.append(float(point[0]))
        vs_coords.append(float(point[1]))
        grad_coords.append((float(grad_sp[0]), float(grad_sp[1])))
#    print("z_coords=", z_coords)
#    print("vs_coords=", vs_coords)
#    print("grad_coords=", grad_coords)
    return [z_coords, vs_coords, grad_coords]


def eval_bz3_pt(t, ctrl_pts):
    one_minus_t = 1-t
    one_minus_t_pow2 = one_minus_t*one_minus_t
    one_minus_t_pow3 = one_minus_t_pow2*one_minus_t
    t_pow2 = t*t
    t_pow3 = t_pow2*t
    pt = [0, 0]
    for i in [0, 1]:
        pt[i] = ctrl_pts[0][i] * one_minus_t_pow3 + \
                ctrl_pts[1][i] * 3 * one_minus_t_pow2 * t + \
                ctrl_pts[2][i] * 3 * one_minus_t * t_pow2 + \
                ctrl_pts[3][i] * t_pow3
    return pt


def eval_bz3_curve(n_pts, ctrl_pts):
    t_space = linspace(0, 1, n_pts)
    curve_pts = [eval_bz3_pt(t, ctrl_pts) for t in t_space]
    return curve_pts


def create_bz_prior_bound(out_file, z_vs_grad_coords, prem_file,
                          vs2vp_mul_offset,
                          vp2rho_mul_offset):

    vs = z_vs_grad_coords[1]
    z = z_vs_grad_coords[0]
    grad = z_vs_grad_coords[2]
    bz3_composite_curve = []

    for i in range(0, len(z)-1):  # one curve per point except for the last one
        ctrl_pts = [(z[i], vs[i]),  # first ctrl point
                    (z[i]+grad[i][0], vs[i]+grad[i][1]),  # 2nd ctrl point
                    (z[i+1]-grad[i][0], vs[i+1]-grad[i][1]),  # 3rd ctrl point
                    (z[i+1], vs[i+1])]    # 4th ctrl point

        # print("ctrl pts for one bz3:", ctrl_pts)
        bz3_composite_curve += eval_bz3_curve(NPOINTS_PER_BCURVE, ctrl_pts)

    # print(bz3_composite_curve)

    create_linear_prior_bound(out_file,
                              [[z for z, vs in bz3_composite_curve],
                               [vs for z, vs in bz3_composite_curve]],
                              prem_file,
                              vs2vp_mul_offset, vp2rho_mul_offset)


def create_linear_prior_bound(out_file, z_vs_pts, prem_file, vs2vp_mul_offset,
                              vp2rho_mul_offset):
    global planet_radius
    vs = z_vs_pts[1]
    z = z_vs_pts[0]
    # print("create_linear_prior_bound z=", z)
    # print("create_linear_prior_bound vs=", vs)

    def refmod_fields2linear_prior_fields(ref_fields: list):
        # out_fields = ref_fields.copy()
        out_fields = [float(ref_fields[i]) for i in range(len(ref_fields))]
        r = float(ref_fields[0])
        ref_depth = (planet_radius-r)/1000
        # find prior z index matching to ref_depth
        # print("z_vs_pts[0]=", z_vs_pts[0])
        z_i = [i-1 for i in range(1, len(z))
               if z[i] >= ref_depth]
        if(len(z_i) != 0):
            z_i = z_i[0]
            # slope of linear prior bound
            a = (vs[z_i+1]-vs[z_i])/(z[z_i+1]-z[z_i])
            # calc. intercept of linear (affine) prior bound
            b = vs[z_i] - a*z[z_i]
            out_vs = a*ref_depth+b
            out_vs *= 1000  # mineos uses m/s
            # vsv == vsh (no anisotropy needed, neemuds_mcmc manages it alone)
            out_fields[3] = out_fields[7] = out_vs
            # infer vp from vs and then rho from vp
            out_fields[2] = out_fields[6] = \
                out_fields[3] * vs2vp_mul_offset[0] + \
                vs2vp_mul_offset[1] * 1000
            out_fields[1] = out_fields[2] * vp2rho_mul_offset[0] + \
                vp2rho_mul_offset[1]
        return out_fields

    derivate_mod_from_prem(out_file, refmod_fields2linear_prior_fields,
                           prem_file)

def loc_create_linear_prior_bound(out_file, z_vs_pts, layer_thickness,
                                  vs2vp_mul_offset, vp2rho_mul_offset):
    out_vs = []
    out_vp = []
    out_rho = []
    out_lines = []
    # prior vs and z
    pvs = z_vs_pts[1]
    pz = z_vs_pts[0]
    # generate a regular list of depths, according to the layer_thickness
    if(layer_thickness):
        vs_prior_z = linspace(pz[0], pz[-1], int(abs(pz[-1]-pz[0])/layer_thickness))
    else:
        vs_prior_z = array(pz)
    # compute affine relationship of the vs prior
    p_a = []
    p_b = []
    for z_i in range(0, len(pz)-1):
        # compute the VS point for this depth
        # slope of linear prior bound
        a = (pvs[z_i+1]-pvs[z_i])/(pz[z_i+1]-pz[z_i])
        # calc. intercept of linear (affine) prior bound
        b = pvs[z_i] - a*pz[z_i]
        p_a += [a]
        p_b += [b]
    for z in vs_prior_z:
        # for the current depth (z) find the matching segment of the linear prior
        z_i = [i-1 for i in range(1, len(pz))
               if pz[i] >= z]
        if(len(z_i) != 0):
            z_i = z_i[0]
            a = p_a[z_i]
            b = p_b[z_i]
            out_vs += [a*z+b]
            # infer the VP and RHO points from the VS point
            out_vp += [ out_vs[-1] * vs2vp_mul_offset[0] + \
                       vs2vp_mul_offset[1]]
            out_rho += [ out_vp[-1] * vp2rho_mul_offset[0] + \
                        vp2rho_mul_offset[1] * 10**-3] # herrmann wants g/cm^3
        else:
            # shouldn't be here (logically impossible)
            raise Exception("The depth "+str(z)+" wasn't found into the prior"
                            " depth domain.")
        # write the prior boundary file
        out_lines += [ [z, out_vp[-1], out_vs[-1], out_rho[-1], 0] ]
    savetxt(out_file, array(out_lines), fmt=["%8.0f", "%9.2f", "%9.2f",
                                              "%9.2f", "%1.1f"])

def loc_create_bz_prior_bound(out_file, z_vs_grad_coords, layer_thickness,
                              vs2vp_mul_offset,
                              vp2rho_mul_offset):

    vs = z_vs_grad_coords[1]
    z = z_vs_grad_coords[0]
    grad = z_vs_grad_coords[2]
    bz3_composite_curve = []

    for i in range(0, len(z)-1):  # one curve per point except for the last one
        ctrl_pts = [(z[i], vs[i]),  # first ctrl point
                    (z[i]+grad[i][0], vs[i]+grad[i][1]),  # 2nd ctrl point
                    (z[i+1]-grad[i][0], vs[i+1]-grad[i][1]),  # 3rd ctrl point
                    (z[i+1], vs[i+1])]    # 4th ctrl point

        # print("ctrl pts for one bz3:", ctrl_pts)
        bz3_composite_curve += eval_bz3_curve(NPOINTS_PER_BCURVE, ctrl_pts)

    # print(bz3_composite_curve)

    loc_create_linear_prior_bound(out_file,
                                  [[z for z, vs in bz3_composite_curve],
                                   [vs for z, vs in bz3_composite_curve]],
                                  layer_thickness,
                                  vs2vp_mul_offset, vp2rho_mul_offset)


def check_opt(opt):
    global planet, prem_file, lo, hi, cwp_lo, cwp_hi, lin_lo,\
            lin_hi, plotting, vs2vp_coeffs, vp2rho_coeffs,\
            vp2rho_offsets, bz_lo, bz_hi, layer_thickness, \
            zmods_hi, zmods_lo
    if(opt in ["--from-planet-conf", "-c"]):
        check_file_exists(planet_conf_file)
        m = search("^.*(mars|earth).*.conf$", planet_conf_file)
        if(not m):
            raise Exception("The conf. filename used "+planet_conf_file+" is "
                            "not valid, it must contains "
                            "`mars' or `earth' and ends with the suffix "
                            ".conf.")
        else:
            planet = m[1]
    elif(opt in ["--prem-file", "-p"]):
        check_file_exists(prem_file)
        check_prem_thickness_mutex()
    elif(opt in ["--lo", "-l"]):
        if(match(cwp_regexp, lo)):
            # print("lo=",lo.replace("cwp:",""))
            cwp_lo = RefModRadiusCoeff(lo.replace("cwp:", ""))
        elif(match(lin_regexp, lo)):
            lin_lo = parse_lin_arg(lo)
        elif(match(bz_regexp, lo)):
            bz_lo = parse_bz_arg(lo)
        elif m_lo := match(zmod_regexp, lo):
            zmods_lo = m_lo.group(1).split(',')
        else:
            raise Exception("Invalid "+opt+" value format.")
    elif(opt in ["--hi", "-h"]):
        if(match(cwp_regexp, hi)):
            # print("hi=", hi.replace("cwp:",""))
            cwp_hi = RefModRadiusCoeff(hi.replace("cwp:", ""))
        elif(match(lin_regexp, hi)):
            lin_hi = parse_lin_arg(hi)
        elif(match(bz_regexp, hi)):
            bz_hi = parse_bz_arg(hi)
        elif m_hi := match(zmod_regexp, hi):
            zmods_hi = m_hi.group(1).split(',')
        else:
            raise Exception("Invalid "+opt+" value format.")
    elif(opt in ["--plot"]):
        plotting = True
    elif(opt == "--vs2vp"):
        # vs2vp_coeffs is a str of format float,float:float,float (each float
        # is optional)
        # after this block it returns to a list of floats as by default
        m = match(r"^\s*"+flt_regx+r"?(,|,"+flt_regx+")?(:" +
                  flt_regx+r"?(,|,"+flt_regx+r")?)?\s*$", vs2vp_coeffs)
        if(not m):
            raise Exception("Invalid value for "+opt+".")
        vs2vp_coeffs = DEFT_VS2VP_COEFFS
        vs2vp_offsets = DEFT_VS2VP_OFFSETS
        if(m[1] is not None):
            vs2vp_coeffs[0] = vs2vp_coeffs[1] = float(m[1])
        if(m[11] is not None):
            vs2vp_coeffs[1] = float(m[11])
        if(m[6] is not None):
            vs2vp_offsets[0] = vs2vp_offsets[1] = float(m[6])
        if(m[16] is not None):
            vs2vp_offsets[1] = float(m[16])
    elif(opt == "--vp2rho"):
        # vp2rho_coeffs is a str of format float,float:float,float (each float
        # is optional)
        # after this block it returns to a list of floats as by default
        m = match(r"^\s*"+flt_regx+r"?(,|,"+flt_regx+")?(:" +
                  flt_regx+r"?(,|,"+flt_regx+r")?)?\s*$", vp2rho_coeffs)
        if(not m):
            raise Exception("Invalid value for "+opt+".")
        vp2rho_coeffs = DEFT_VP2RHO_COEFFS
        vp2rho_offsets = DEFT_VP2RHO_OFFSETS
        if(m[1] is not None):
            vp2rho_coeffs[0] = vp2rho_coeffs[1] = float(m[1])
        if(m[11] is not None):
            vp2rho_coeffs[1] = float(m[11])
        if(m[6] is not None):
            vp2rho_offsets[0] = vp2rho_offsets[1] = float(m[6])
        if(m[16] is not None):
            vp2rho_offsets[1] = float(m[16])
    elif(opt in ["--layer-thickness", "-t"]):
        if(not (isinstance(eval(layer_thickness), float) or
                isinstance(eval(layer_thickness), int))):
            raise ValueError("The layer thickness must be a number")
#        print("check_opt() layer_thickness=", layer_thickness)
        layer_thickness = float(layer_thickness)
        check_prem_thickness_mutex()


def check_prem_thickness_mutex():
    if(layer_thickness and prem_file):
        raise ValueError("The two options --layer-thickness|-t and --prem-file|-p",
                         "are mutually exclusive.")


def prem2prior_filename(level, prem_file):
    lvlstr = "hi"
    if(level == LOW):
        lvlstr = "lo"
    return search(r'([^.]*)(\..*)?', basename(prem_file))[1]+"."+lvlstr


def get_planet_radius_from_prem(prem_file):
    last_line = open(prem_file).readlines()[-1].split(" ")
    last_line = [e for e in last_line if e != '']
    planet_radius = float(last_line[0])
    return planet_radius


def plot_priors(hi_mod, lo_mod, prem_file, plot_prem=True):
    hi = loadtxt(hi_mod, skiprows=3)
    lo = loadtxt(lo_mod, skiprows=3)
    prem = loadtxt(prem_file, skiprows=3)
    plt.rcParams['figure.figsize'] = [12.0, 8]

    def id2pos(idx):
        pos = [ 1, 2, 3 ]
        return pos[idx-1]

    def id2par(idx):
        pars = ['RHO', 'VP', 'VS']
        return pars[idx-1]

    def id2mul(idx):
        muls = [10**-3, 10**-3, 10**-3]
        return muls[idx-1]

    def id2unit(idx):
        units = [ "g/cm³", "km/s", "km/s"]
        return units[idx-1]
    for i in [1, 2, 3]:
        plt.subplot(1, 3, id2pos(i-1))
        if(cwp_lo or lin_lo or planet_conf_file):
            plt.plot((planet_radius-lo[::-1][:, 0])/1000, lo[::-1][:, i] *
                     id2mul(i), label=id2par(i)+"_lo")
        if(cwp_hi or lin_hi or planet_conf_file):
            plt.plot((planet_radius-hi[::-1][:, 0])/1000, hi[::-1][:, i] *
                     id2mul(i), label=id2par(i)+"_hi")
        if zmods_lo:
            plt.plot((planet_radius-lo[::-1][:, 0])/1000, lo[::-1][:, i] *
                     id2mul(i),
                     label=id2par(i)+"_lo")
        if zmods_hi:
            plt.plot((planet_radius-hi[::-1][:, 0])/1000, hi[::-1][:, i] *
                     id2mul(i),
                     label=id2par(i)+"_hi")
        if(plot_prem):
            plt.plot((planet_radius-prem[::-1][:, 0])/1000, prem[::-1][:, i] *
                     id2mul(i),
                     label=id2par(i)+"_ref")
        plt.xlabel("z (km)")
        plt.ylabel(id2unit(i))
        plt.legend()
        plt.grid(True)
        plt.suptitle("Ref.: "+prem_file+" and prior: "+lo_mod+" "+hi_mod)
    if(lin_lo and lin_hi):
        plt.title(
            "\n  VP_lo=VS_lo*"+str(vs2vp_coeffs[0])+"+"+str(vs2vp_offsets[0]) +
            " VP_hi=VS_hi*" + str(vs2vp_coeffs[1])+"+"+str(vs2vp_offsets[1]) +
            "\nRHO_lo=VP_lo*" + str(vp2rho_coeffs[0])+"+" +
            str(vp2rho_offsets[0]) +
            " RHO_hi=VP_hi*" +
            str(vp2rho_coeffs[1])+"+"+str(vp2rho_offsets[1]))
    plt.show()


def loc_plot_priors(hi_mod, lo_mod):
    hi = loadtxt(hi_mod, skiprows=0)
    lo = loadtxt(lo_mod, skiprows=0)
    # duplicate rows in order to show discontinuities
    # as interpreted by disp96
    def dup_for_discontinuities(mod):
        mod_dup = ndarray((2*mod.shape[0]-1, mod.shape[1]))
        for i in range(0, mod_dup.shape[0]-1, 2):
            mod_dup[i, :] = mod[int(i/2), :]
            mod_dup[i+1, 0] = mod[int(i/2)+1, 0]
            mod_dup[i+1, 1:] = mod[int(i/2), 1:]
        mod_dup[-1,:] = mod[-1,:]
        return mod_dup
    hi_dup = dup_for_discontinuities(hi)
    lo_dup = dup_for_discontinuities(lo)
    hi = hi_dup
    lo = lo_dup
    plt.rcParams['figure.figsize'] = [13.0, 8]

    def id2par(idx):
        pars = ['VP', 'VS', 'RHO']
        return pars[idx-1]

    def id2mul(idx):
        muls = [1, 1, 1]
        return muls[idx-1]

    def id2unit(idx):
        units = ["km/s", "km/s", "g/cm³"]
        return units[idx-1]
    for i in [2, 1, 3]:
        plt.subplot(1, 3, i)
        if(cwp_lo or lin_lo or planet_conf_file):
            plt.plot(lo[:][:, 0], lo[:][:, i] *
                     id2mul(i), label=id2par(i)+"_lo")
        if(cwp_hi or lin_hi or planet_conf_file):
            plt.plot(hi[:][:, 0], hi[:][:, i] *
                     id2mul(i), label=id2par(i)+"_hi")
        plt.xlabel("z (km)")
        plt.ylabel(id2unit(i))
        plt.grid(True)
        plt.legend()
    title = "Prior: "+lo_mod+" "+hi_mod
    if(lin_lo and lin_hi):
        title +=(
            "\n  VP_lo=VS_lo*"+str(vs2vp_coeffs[0])+"+"+str(vs2vp_offsets[0]) +
            " VP_hi=VS_hi*" + str(vs2vp_coeffs[1])+"+"+str(vs2vp_offsets[1]) +
            "\nRHO_lo=VP_lo*" + str(vp2rho_coeffs[0])+"+" +
            str(vp2rho_offsets[0]) +
            " RHO_hi=VP_hi*" +
            str(vp2rho_coeffs[1])+"+"+str(vp2rho_offsets[1]))
    plt.suptitle(title)
    plt.show()


def help():
    cwd_cmd = infer_path_rel_and_abs_cmds(argv)[0]
    print_frame("HELP", Color.RED)
    print(bold("1. Generating a Prior by Component-Wise Product on a "
               "Reference "
               "Model, the configuration file way (Global scale/Mineos only)"))
    print(col(Color.RED, bold(cwd_cmd+" -c|--from-planet-conf [--plot]")),
          col(Color.BLUE, "<filepath>"))
    print("\t\tGenerates a set of priors from a config."
          " file which contains the component-wise product coefficients and"
          " the reference model to derivate from (see for example "
          "neemuds_mars.conf or neemuds_earth.conf).")
    print(col(Color.GREEN, "\t\tExample:\n\t\t  "),
          col(Color.RED, bold(cwd_cmd)+" -c"),
          col(Color.BLUE, "neemuds_mars.conf"), col(Color.RED, "--plot\n"))
    print(bold("=====\n"), end='')
    print(bold("2. Generating a Prior by Component-Wise Product on a "
               "Reference "
               "Model, the command line way (Global scale/Mineos only)"))
    print(col(Color.RED, bold(cwd_cmd+" -p|--prem-file")),
          col(Color.BLUE, "<filepath>"), col(Color.RED, "--lo|-l "),
          col(Color.BLUE, 'cwp:<coeff_list>'), col(Color.RED, "--hi|-h "),
          col(Color.BLUE, 'cwp:<coeff_list>'), col(Color.RED, '[--plot]'))
    print("\t\tGenerates a prior low or high bounds by"
          " applying a component-wise product on each PREM row.",
          "\n\t\tThe coefficient vectors used for the products are set"
          " with --hi and --lo options.\n\t\tLook at the doc. in "
          "neemuds_earth.conf to comprehend the coefficient list format.")
    print(col(Color.GREEN, "\t\tExamples:\n\t\t  "),
          col(Color.RED, bold(cwd_cmd) + " --prem-file"),
          col(Color.BLUE, "~/.ndata/prior/prem_noocean.txt"),
          col(Color.RED, "--lo"),
          col(Color.BLUE, "'cwp:.95, .85, .85, 1, 1, 1, 1, 1, "
              "6371000;6271000, .90, .8, .8, 1, 1, 1, 1, 1'"),
          col(Color.RED, "--hi"),
          col(Color.BLUE, "'cwp:1.05, 1.15, 1.15, 1, 1, 1, 1, 1, "
              "6371000;6271000, 1.1, 1.2, 1.2, 1, 1, 1, 1, 1'"))
    print("\t\t  ", col(Color.RED, bold(cwd_cmd) + " --prem-file"),
          col(Color.BLUE, "~/.ndata/prior/prem_noocean.txt"),
          col(Color.RED, "--lo"),
          col(Color.BLUE, "'cwp:.95, .85, .85, 1, 1, 1, 1, 1, "
              "6371000;6271000, .90, .8, .8, 1, 1, 1, 1, 1'"))
    print("\t\t  ", col(Color.RED, bold(cwd_cmd) + " --prem-file"),
          col(Color.BLUE, "~/.ndata/prior/prem_noocean.txt"),
          col(Color.RED, "--hi"),
          col(Color.BLUE, "'cwp:1.05, 1.15, 1.15, 1, 1, 1, 1, 1, "
              "6371000;6271000, 1.1, 1.2, 1.2, 1, 1, 1, 1, 1'"),
          col(Color.RED, '--plot\n'))
    print(bold("=====\n"), end='')
    print(bold("3. Generating a Piecewise Affine VS Prior and Inferring VP and "
               "RHO Priors Affinely (Global scale/Mineos only)"))
    print(col(Color.RED, bold(cwd_cmd+" -p|--prem-file")),
          col(Color.BLUE, "<filepath>"), col(Color.RED, "--lo|-l "),
          col(Color.BLUE, 'lin:<z_coeff_list>:<vs_coeff_list>'),
          col(Color.RED, "--hi|-h "),
          col(Color.BLUE, 'lin:<z_coeff_list>:<vs_coeff_list>'),
          col(Color.RED, "[--plot]"),
          col(Color.RED, "[--vs2vp"),
          col(Color.BLUE, "<A1>[,<B1>][:<A2>[,<B2>]"),
          col(Color.RED, "]"),
          col(Color.RED, "[--vp2rho"),
          col(Color.BLUE, "<A3>[,<B3>][:<A4>[,<B4>]"),
          col(Color.RED, "]"))
    print("\t\tGenerates a VS prior low or/and high bounds by defining a list "
          "of segments for the lower bounds (`--lo' option) and likewise for "
          "the higher bounds (`--hi' option).")
    print("\t\tThe format for a boundary composed of N segments is "
          "lin:<z_1>,<z_2>,...,<z_N>:<vs_1>,<vs_2>,...,<vs_N>, with z_i being "
          "the depth of the i-th point (in km) and vs_i the corresponding "
          "VS value in km/s.")
    print("\t\tIf the z-list doesn't cover the whole planet radius then the",
          "prior bound will be a copy of the PREM for the outside depth",
          "domain (see fourth example below).")
    print("\t\tThe VP prior is deduced from the VS prior by this",
          "relationship: VP_lo = VS_lo*A1+B1 and VP_hi = VS_hi*A2+B2",
          "(in km/s).",
          ("By default, A1 = {0:1.3f}, A2 = {1:1.3f}, B1={2:1.3f}," +
           " B2={3:1.3f}.").format(*vs2vp_coeffs, *vs2vp_offsets))
    print("\t\tIf only A1, B1 are defined then A2 = A1, B2 = B1.")
    print("\t\tThe RHO prior is likewise deduced from the VP prior by the",
          "following relationship: RHO_lo = VP_lo*A3+B3, RHO_hi =",
          "VP_hi*A4+B4.\n\t\tBy default, A3 = {0:1.3f}, A4 = {1:1.3f}, B3 = "
          "{3:1.3f}, B4 = {2:1.3f}. B3 and B4 are in kg/m^3.".
          format(*vp2rho_coeffs, *vp2rho_offsets))
    print("\t\tIf only A3, B3 are defined then A4 = A3, B4 = B3.")
    print("\n\t\tUse optional switches --vs2vp and --vp2rho to override",
          "default values.")
    print(col(Color.GREEN, "\t\tExamples:\n\t\t  "),
          col(Color.RED, bold(cwd_cmd) + " --prem-file"),
          col(Color.BLUE, "~/.ndata/prior/prem_noocean.txt"),
          col(Color.RED, "--lo"),
          col(Color.BLUE, "'lin:0,2891,5150,6371:2,0,0,3'"),
          col(Color.RED, "--hi"),
          col(Color.BLUE, "'lin:0,700,6371:4,7,8'"), col(Color.RED,
                                                         "--plot\n\t\t  "),
          col(Color.RED, bold(cwd_cmd) + " --prem-file"),
          col(Color.BLUE, "~/.ndata/prior/mars/EH45TcoldCrust1.tvel"),
          col(Color.RED, "--lo"),
          col(Color.BLUE, "'lin:0,1500,3389.5:2,0,0'"),
          col(Color.RED, "--hi"),
          col(Color.BLUE, "'lin:0,700,3389.5:4.5,5,6'"),
          col(Color.RED, "--plot\n\t\t  "),
          col(Color.RED, bold(cwd_cmd) + " --prem-file"),
          col(Color.BLUE, "~/.ndata/prior/mars/EH45TcoldCrust1.tvel"),
          col(Color.RED, "--lo"),
          col(Color.BLUE, "'lin:0,1500,3389.5:2,0,0'"),
          col(Color.RED, "--hi"),
          col(Color.BLUE, "'lin:0,700,3389.5:4.5,5,6'"),
          col(Color.RED, "--plot"),
          col(Color.RED, "--vs2vp"), col(Color.BLUE, "1.7:1.95"),
          col(Color.RED, "--vp2rho"), col(Color.BLUE, ".39,1000:.4,3000" +
                                          "\n\t\t  "),
          col(Color.RED, bold(cwd_cmd) + " --prem-file"),
          col(Color.BLUE, "~/.ndata/prior/mars/EH45TcoldCrust1.tvel"),
          col(Color.RED, "--lo"),
          col(Color.BLUE, "'lin:0,1500,3389.5:2,0,0'"),
          col(Color.RED, "--hi"),
          col(Color.BLUE, "'lin:0,700,3389.5:4.5,5,6'"),
          col(Color.RED, "--plot"),
          col(Color.RED, "--vs2vp"), col(Color.BLUE, ",1:,1.1"),
          col(Color.RED, "--vp2rho"), col(Color.BLUE, ",1000:.4,3000\n\t\t  "),
          col(Color.RED, bold(cwd_cmd) + " --prem-file"),
          col(Color.BLUE, "~/.ndata/prior/prem_noocean.txt"),
          col(Color.RED, "--lo"),
          col(Color.BLUE, "'lin:0,1000,2000:0,2,2.5'"),
          col(Color.RED, "--hi"),
          col(Color.BLUE, "'lin:0,700,2000:5,7,8'"), col(Color.RED,
                                                         "--plot\n\t\t"))
    print(bold("=====\n"), end='')
    print(bold("4. Generating Composite Symmetric Cubic Bezier Prior and "
               "Inferring VP and "
               "RHO Priors Affinely (Global scale/Mineos only)"))
    print(col(Color.RED, bold(cwd_cmd+" -p|--prem-file")),
          col(Color.BLUE, "<filepath>"), col(Color.RED, "--lo|-l "),
          col(Color.BLUE,
              'bz:<z0>,<vs0>:<grad_z0>,<grad_vs0>;<z1>,<vs1>:' +
              '[<grad_z1>,<grad_vs1>][...<zN>,<vsN>[:<grad_zN>,<grad_vsN>]]'),
          col(Color.RED, "--hi|-h "),
          col(Color.BLUE,
              'bz:<z0>,<vs0>:<grad_z0>,<grad_vs0>;<z1>,<vs1>:' +
              '[<grad_z1>,<grad_vs1>][...<zN>,<vsN>[:<grad_zN>,<grad_vsN>]]'),
          col(Color.RED, "[--plot]"),
          col(Color.RED, "[--vs2vp"),
          col(Color.BLUE, "<A1>[,<B1>][:<A2>[,<B2>]"),
          col(Color.RED, "]"),
          col(Color.RED, "[--vp2rho"),
          col(Color.BLUE, "<A3>[,<B3>][:<A4>[,<B4>]"),
          col(Color.RED, "]"))
    print("\t\tGenerates a VS prior low or/and high bounds by defining a "
          "composite bezier cubic curve for the lower bounds (`--lo' option) "
          "and likewise for the higher bounds (`--hi' option).")
    print("\t\tThe `bz:' format defines a list of anchor points for a VS",
          "prior boundary.",
          "\n\t\tThe composite curve of the prior boundary passes through",
          "all its anchor points and contains (N-1) component bezier curves.",
          "\n\t\tA component bezier curve is defined by two anchor",
          "points and a gradient. These two anchor points are the first and",
          "the last of its four control points. Hence, N anchor points",
          "allows to define a prior boundary composed of (N-1) bezier curves.",
          "\n\t\tThe gradient is the way to deduce the two intermediary",
          "control points of a curve from its two extrem control points",
          "(which are anchor points). For example, the first curve is defined",
          "by the following control points: (z0, vs0),",
          "(z0+grad_z0, vs0+grad_z0), (z1-grad_z0, vs1-grad_vs0), (z1, vs1).",
          "The second curve which is connected to the first one through the",
          "point (z1, vs1) is defined by the four next control points:",
          "(z1, vs1), (z1+grad_z1, vs1+grad_vs1), (z2-grad_z1, vs2-grad_vs2),",
          "(z2, vs2). The gradient being optional except for the first curve,",
          "if it's not specified then grad_z1 == grad_z0,",
          "grad_vs1 == grad_vs0. More generally, grad_z_i == grad_z_(i-1),",
          "grad_vs_i == grad_vs_(i-1), if it's specified for anchor point of",
          "index (i-1) but not for the index i. In other words, the gradient",
          "stays the same along the component curves as long as you don't",
          "change it somewhere in the chain.\n\t\tFor an explanation about",
          "`--vp2rho' or `--vs2vp' options look at "+bold(".3"))
    print(col(Color.GREEN, "\t\tExamples:"))
    print("\t\t\t"+col(Color.RED, bold(cwd_cmd) + " --prem-file"),
          col(Color.BLUE, "~/.ndata/prior/prem_noocean.txt"),
          col(Color.RED, "--lo"),
          col(Color.BLUE, "'bz:0.1,0:15,3;3000,1;5000,4'"),
          col(Color.RED, "--hi"),
          col(Color.BLUE, "'bz:0.1,7:15,3;2800,9;5000,10'"),
          col(Color.RED, "--plot"))
    print("\t\t\tIn the example above, anchor points are:",
          "\n\t\t\t(z0 = 0.1, vs0 = 0.0), (z1 = 3000, vs1 = 1),",
          "(z2 = 5000, vs2 = 4) for the lower boundary.",
          "\n\t\t\t(z0 = 0.1, vs0 = 7.0), (z1 = 2800, vs1 = 9.0),",
          "(z2 = 5000, vs2 = 10.0) for the upper boundary.",
          "\n\t\t\tThe gradient of both lower and higher boundary curves",
          "is always (15.0, 3.0)")
    print("\t\t\t"+col(Color.RED, bold(cwd_cmd) + " --prem-file"),
          col(Color.BLUE, "~/.ndata/prior/prem_noocean.txt"),
          col(Color.RED, "--lo"),
          col(Color.BLUE, "'bz:0.1,0:15,3;3000,1:50,1;5000,4'"),
          col(Color.RED, "--hi"),
          col(Color.BLUE, "'bz:0.1,7:15,3;2800,10;5000,10'"),
          col(Color.RED, "--plot"))
    print("\t\t\tIn the last example, the gradient changes along the",
          "curves of the lower boundary. It's (15.0, 3.0) for the first curve",
          "and (50.0, 1.0) for the second.")
    print(bold("=====\n"), end='')
    print(bold("5. Generating Priors by any of the Methods 3. or 4. for the "
               "Local scale/Herrmann case (only)"))
    print("\t\t\tThis use case is exactly the same as for Mineos in 3.",
          "and 4. except that the `--prem-file' option is replaced by the",
          "`--layer-thickness' option which allows to define the regular space",
          "between each successive pair of points of the priors boundaries",
          "along the depth (contrary",
          "to the 3. and 4. options that deduce a non-regular depth space",
          "following the prem depths-radii).")
    print("\t\t\tThe layer thickness is defined in km.")
    print("\t\t\tThe `--layer-thickness' option is mandatory for Bezier",
          "priors but",
          "facultative for linear priors (but take note that the use or non-use",
          "of this option and its value may generate really",
          "different priors as the `--plot' option shows it).")
    print(col(Color.GREEN, "\t\tExamples (Linear Priors):\n\t\t  "),
          col(Color.RED, bold(cwd_cmd) + " --layer-thickness"),
          col(Color.BLUE, "2"),
          col(Color.RED, "--lo"),
          col(Color.BLUE, "'lin:0,2891,5150,6371:2,0,0,3'"),
          col(Color.RED, "--hi"),
          col(Color.BLUE, "'lin:0,700,6371:4,7,8'"), col(Color.RED,
                                                         "--plot"))
    print(col(Color.RED, "\t\t   "+bold(cwd_cmd)),
          col(Color.RED, "--lo"),
          col(Color.BLUE, "'lin:0,2891,5150,6371:2,0,0,3'"),
          col(Color.RED, "--hi"),
          col(Color.BLUE, "'lin:0,700,6371:4,7,8'"), col(Color.RED,
                                                         "--plot\n\t\t  "),
          col(Color.RED, bold(cwd_cmd) + " --layer-thickness"),
          col(Color.BLUE, "2"),
          col(Color.RED, "--lo"),
          col(Color.BLUE, "'lin:0,1500,3389.5:2,0,0'"),
          col(Color.RED, "--hi"),
          col(Color.BLUE, "'lin:0,700,3389.5:4.5,5,6'"),
          col(Color.RED, "--plot\n\t\t  "),
          col(Color.RED, bold(cwd_cmd) + " --layer-thickness"),
          col(Color.BLUE, "2"),
          col(Color.RED, "--lo"),
          col(Color.BLUE, "'lin:0,1500,3389.5:2,0,0,3'"),
          col(Color.RED, "--hi"),
          col(Color.BLUE, "'lin:0,700,3389.5:4.5,5,6'"),
          col(Color.RED, "--plot"),
          col(Color.RED, "--vs2vp"), col(Color.BLUE, "1.7:1.95"),
          col(Color.RED, "--vp2rho"), col(Color.BLUE, ".39,1000:.4,3000" +
                                          "\n\t\t  "),
          col(Color.RED, bold(cwd_cmd) + " --layer-thickness"),
          col(Color.BLUE, "2"),
          col(Color.RED, "--lo"),
          col(Color.BLUE, "'lin:0,1500,3389.5:2,0,0'"),
          col(Color.RED, "--hi"),
          col(Color.BLUE, "'lin:0,700,3389.5:4.5,5,6'"),
          col(Color.RED, "--plot"),
          col(Color.RED, "--vs2vp"), col(Color.BLUE, ",1:,1.1"),
          col(Color.RED, "--vp2rho"), col(Color.BLUE, ",1000:.4,3000\n\t\t  "),
          col(Color.RED, bold(cwd_cmd) + " --layer-thickness"),
          col(Color.BLUE, "2"),
          col(Color.RED, "--lo"),
          col(Color.BLUE, "'lin:0,1000,2000:0,2,2.5'"),
          col(Color.RED, "--hi"),
          col(Color.BLUE, "'lin:0,700,2000:5,7,8'"), col(Color.RED,
                                                         "--plot\n\t\t"))
    print(col(Color.GREEN, "\t\tExamples (Bezier Priors):"))
    print("\t\t\t"+col(Color.RED, bold(cwd_cmd) + " --layer-thickness"),
          col(Color.BLUE, "2"),
          col(Color.RED, "--lo"),
          col(Color.BLUE, "'bz:0.1,0:15,3;3000,1;5000,4'"),
          col(Color.RED, "--hi"),
          col(Color.BLUE, "'bz:0.1,7:15,3;2800,9;5000,10'"),
          col(Color.RED, "--plot"))
    print("\t\t\t"+col(Color.RED, bold(cwd_cmd) + " --layer-thickness"),
          col(Color.BLUE, "200"),
          col(Color.RED, "--lo"),
          col(Color.BLUE, "'bz:0.1,0:15,3;3000,1;5000,4'"),
          col(Color.RED, "--hi"),
          col(Color.BLUE, "'bz:0.1,7:15,3;2800,9;5000,10'"),
          col(Color.RED, "--plot"))
    print("\t\t\t"+col(Color.RED, bold(cwd_cmd) + " --layer-thickness"),
          col(Color.BLUE, "2"),
          col(Color.RED, "--lo"),
          col(Color.BLUE, "'bz:0.1,0:15,3;3000,1:50,1;5000,4'"),
          col(Color.RED, "--hi"),
          col(Color.BLUE, "'bz:0.1,7:15,3;2800,10;5000,10'"),
          col(Color.RED, "--plot"))
    print(bold("=====\n"), end='')
    print(bold("6. Generating a Mineos model by joining models: depth models"
               " in surface and reference model for deeper layers"
               ))
    print(col(Color.RED, bold(cwd_cmd+" -p|--prem-file")),
          col(Color.BLUE, "<filepath>"), col(Color.RED, "--lo|-l "),
          col(Color.BLUE,
              'zmod_files:<rho_file.txt>,<vp()v_file.txt>,<vs(v)_file.txt>,' +
              '[<vph_file.txt>,<vsh_file.txt>,<eta_file.txt>]'),
          col(Color.RED, "--hi|-h "),
          col(Color.BLUE,
              'zmod_files:<rho_file.txt>,<vp()v_file.txt>,<vs(v)_file.txt>,' +
              '[<vph_file.txt>,<vsh_file.txt>,<eta_file.txt>]'),
          col(Color.RED, "[--plot]"))
    print("\t\tGenerates a prior for low or/and high bounds by joining a"
          " reference model (-p|--prem-file) used for the deeper part of the"
          " output prior and depth models (rho, vpv, vsv, etc.) for the"
          " surface part of the prior.\n"
          "\t\tThe depth models are joined to the reference model to form the"
          " prior.\n"
          "\t\tThe depth models must be formatted with two fields: the depth "
          "in m, the parameter in m/s for vp, vs, kg/m^3 for rho and no unit "
          "for eta.\n"
          "\t\tThey all must use the same depth layers (same number and same"
          " z's). The maximum z of depth models must be lower or equal to the"
          "planet radius. The minimum z must be zero.\n")
    print(col(Color.GREEN, "\t\tExamples:"))
    print("\t\t\t"+col(Color.RED, bold(cwd_cmd) + " --prem-file"),
          col(Color.BLUE, "~/.ndata/prior/prem_noocean.txt"),
          col(Color.RED, "--lo"),
          col(Color.BLUE, "'zmod_files:rho.lo,vp.lo,vs.lo'"),
          col(Color.RED, "--hi"),
          col(Color.BLUE, "'zmod_files:rho.hi,vp.hi,vs.hi'"),
          col(Color.RED, "--plot"))
    print("\t\t\tIn the example above, rho.lo, vp.lo, and vp.hi are:",
          """\n\t\t\t--- rho.lo:
          \t\t0 2480
          \t\t2000 2500

          \t\t--- vp.lo:
          \t\t0 4800
          \t\t2000 4810

          \t\t--- vs.lo:
          \t\t0 3090
          \t\t2000 3100

          \t\t--- rho.hi:
          \t\t0 3000
          \t\t0 3100

          \t\t--- vp.hi:
          \t\t0 6000
          \t\t2000 6100

          \t\t--- vs.hi:
          \t\t0 4000
          \t\t2000 4100

          \t\t--- prem_noocean.txt end is:
          \t\t6368000.  2600.00  5800.00  3200.00  57823.0    600.0  5800.00 3200.00  1.00000
          \t\t6368000.  2600.00  5800.00  3200.00  57823.0    600.0  5800.00 3200.00  1.00000
          \t\t6369000.  2600.00  5800.00  3200.00  57823.0    600.0  5800.00 3200.00  1.00000
          \t\t6370000.  2600.00  5800.00  3200.00  57823.0    600.0  5800.00 3200.00  1.00000
          \t\t6371000.  2600.00  5800.00  3200.00  57823.0    600.0  5800.00 3200.00  1.00000

          \t\tThe program outputs the following prior models (low and high limits of prior;
          \t\tonly the file ends are shown):
            \t\t==> prem_noocean.hi <==
            \t\t6367000.  2600.00  5800.00  3200.00  57823.0    600.0  5800.00  3200.00  1.00000
            \t\t6368000.  2600.00  5800.00  3200.00  57823.0    600.0  5800.00  3200.00  1.00000
            \t\t6368000.  2600.00  5800.00  3200.00  57823.0    600.0  5800.00  3200.00  1.00000
            \t\t6369000.  3100.00  6100.00  4100.00  57823.0    600.0  6100.00  4100.00  1.00000
            \t\t6371000.  3000.00  6000.00  4000.00  57823.0    600.0  6000.00  4000.00  1.00000

            \t\t==> prem_noocean.lo <==
            \t\t6367000.  2600.00  5800.00  3200.00  57823.0    600.0  5800.00  3200.00  1.00000
            \t\t6368000.  2600.00  5800.00  3200.00  57823.0    600.0  5800.00  3200.00  1.00000
            \t\t6368000.  2600.00  5800.00  3200.00  57823.0    600.0  5800.00  3200.00  1.00000
            \t\t6369000.  2500.00  4810.00  3100.00  57823.0    600.0  4810.00  3100.00  1.00000
            \t\t6371000.  2480.00  4800.00  3090.00  57823.0    600.0  4800.00  3090.00  1.00000
          """)
    print(bold("=====\n"), end='')

def build_joint_ref_mod_and_surface_zmods(ref_mod_file, zmod_files, out_mod_file):
    """
    Forms a mineos model (such as the PREM) by merging the depth models zmod_files
    for the surface side and the reference model ref_mod_file for the deeper
    part.

    Args:
        zmod_files: a list of depth model files, two possibilities:
            - [rho, vp, vs]: in this case vpv == vph, and vsv == vsh, eta == [1,
              ..., 1]
            - [rho, vpv, vsv, vph, vsh, eta]
        ref_mod: a reference model in Mineos format (e.g. prem_noocean.txt).
        out_mod_file: the output file for the resulting Mineos model.

    Returns: None.
    """

    # check files exist
    for f in [ref_mod_file]+zmod_files:

        if not exists(f):
            raise ValueError(f+' doesn\'t exist')

    n = len(zmod_files)
    # check mandatory arguments
    if n < 3:
        raise Exception('At least 3 model files must be passed')

    # check that optional arguments are consistent
    vph_vsh_eta = False  # models not provided by default
    if n > 3:
        vph_vsh_eta = True
        if n != 6:
            raise Exception('Optional models vph, vsh and eta must all be'
                            ' provided or none')

    # open provided depth models
    rho, vpv, vsv = [loadtxt(zmod_files[i]) for i in range(3)]
    if vph_vsh_eta:
        vph, vsh, eta = [loadtxt(zmod_files[i]) for i in range(3, 6)]

    # verify models are depth consistent
    for dmod in [vpv, vsv] + [vph, vsh, eta] if vph_vsh_eta else []:
        if not allclose(dmod[:, 0], rho[:, 0]):
            raise Exception('All depth models must have the same depth layers')

    # load mineos ref model skipping header
    ref_mod = loadtxt(ref_mod_file, skiprows=3)

    if ref_mod.ndim != 2 or ref_mod.shape[1] != 9:
        raise Exception("The input reference model "+ref_mod+" is not valid"
                        "(it must have 9 columns/fields; see Mineos"
                        "documentation)")

    # depth models are in m as in mineos format
    dm_z = rho[:, 0]
    dm_max_z = dm_z[-1]

    # verify the maximum depth of depth models
    # is lower/equal to the planet radius (pr) in ref_mod
    # NOTE: depth model are in m, mineos is in m too
    pr = ref_mod[-1, 0]
    if pr < dm_max_z:
        raise Exception("Depth models are exceeding the planet whole"
                        " radius")

    # get the ref_mod part below to depth models
    dm_r = pr - dm_z
    dm_max_r = pr - dm_max_z  # converted to radius
    bref_mod = ref_mod[ref_mod[:, 0] < dm_max_r]

    # build qkappa, qshear from ref_mod
    # (computed by lerp if not exact depth found)
    qkappa = zeros((dm_r.size, 1))
    qshear = zeros((dm_r.size, 1))
    for i, r in enumerate(dm_r):
        # for each radius r of the depth model
        # find two layers in ref model to interpolate
        l1 = ref_mod[ref_mod[:, 0] <= r][-1]  # deeper/as deep layer
        if l1[0] == r:
            # exact radius found
            rqkappa, rqshear = l1[4:6]
        else:
            l2 = ref_mod[ref_mod[:, 0] > r][0]  # shallower layer
            # lerp between l1, l2
            rqkappa = l1[4] + (r - l1[0]) * (l2[4] - l1[4]) / (l2[0] - l1[0])
            rqshear = l1[5] + (r - l1[0]) * (l2[5] - l1[5]) / (l2[0] - l1[0])
        qkappa[i] = rqkappa
        qshear[i] = rqshear

    # copy vpv, vsv for vph, vsh if the latter are not provided
    # build eta (only ones) if not provided
    if not vph_vsh_eta:
        vph = vpv.copy()
        vsh = vsv.copy()
        eta = hstack((vpv[:, 0].reshape(-1, 1), ones(vpv.shape[0]).reshape(-1, 1)))

    # gather all in a mineos model
    # it needs reverting the layer order (because of the depth to radius
    # conversion)
    mineos_mod = hstack((dm_r[::-1].reshape(-1, 1),
                            rho[::-1, 1].reshape(-1, 1),
                            vpv[::-1, 1].reshape(-1, 1),
                            vsv[::-1, 1].reshape(-1, 1),
                            qkappa[::-1].reshape(-1, 1),
                            qshear[::-1].reshape(-1, 1),
                            vph[::-1, 1].reshape(-1, 1),
                            vsh[::-1, 1].reshape(-1, 1),
                            eta[::-1, 1].reshape(-1, 1)
                            ))
    # add ref mod deeper part
    mineos_mod = vstack((bref_mod, mineos_mod))

    fmt = ('%7.0f.','%8.2f','%8.2f','%8.2f',
           '%8.1f','%8.1f','%8.2f','%8.2f','%8.5f')
    # build header
    # layer index of the solid side of the inner-core boundary
    # (vs > 0)
    nic = 0
    while ref_mod[nic, 3] > 0:
        nic += 1
    # layer index of the liquid side of the mantle-core boundary
    # (vs == 0)
    noc = nic + 1
    while ref_mod[noc, 3] == 0:
        noc += 1
    title = "Generated model"
    ifanis = int(not all(eta[:, 1] == 1))
    tref = 1 # physical dispersion correction
    ifdeck = 1 # tabular format
    N = len(mineos_mod)
    header = "\n".join([title,
                        str(ifanis) + " " + str(tref) + " " + str(ifdeck),
                        str(N) + " " + str(nic) + " " + str(noc)])

    savetxt(out_mod_file, mineos_mod, fmt=fmt, header=header, comments='')


if __name__ == "__main__":
    opts, remaining = getopt(argv[1:], short_opts, long_opts)
    # whatever the scale (mars or earth) we want to generate a prior from
    # planet_conf_file
    parse_opts(opts)
    if(planet_conf_file):
        p = parse_params_conf_file(planet, PlanetParams,
                                   filepath=planet_conf_file)
        for wavetype in ["rayl", "love"]:
            for level in HIGH, LOW:
                gen_neg_perturbation_mod(wavetype, level, planet,
                                         planet_params=p)
        planet_radius = get_planet_radius_from_prem(p.refmod)
        if(plotting):
            for lo_mod, hi_mod in [(p.lo_mod_rayl, p.hi_mod_rayl),
                                   (p.lo_mod_love, p.hi_mod_love)]:
                print("lo_mod=", lo_mod, "hi_mod=", hi_mod)
                plot_priors(hi_mod, lo_mod, p.refmod, plot_prem=True)
    elif(prem_file):
        planet_radius = get_planet_radius_from_prem(prem_file)
        hi_mod = prem2prior_filename(HIGH, prem_file)
        lo_mod = prem2prior_filename(LOW, prem_file)
        if(cwp_hi):
            print(col(Color.GREEN, "INFO:"), "generates hi. model in:", hi_mod)
            gen_neg_perturb_mod_with_coeffs(hi_mod, cwp_hi, prem_file)
        elif(lin_hi):
            print(col(Color.GREEN, "INFO:"), "generates hi. model in:", hi_mod)
            create_linear_prior_bound(hi_mod, lin_hi, prem_file,
                                      [vs2vp_coeffs[1], vs2vp_offsets[1]],
                                      [vp2rho_coeffs[1], vp2rho_offsets[1]])
        elif(bz_hi):
            print(col(Color.GREEN, "INFO:"), "generates hi. model in:", hi_mod)
            create_bz_prior_bound(hi_mod, bz_hi, prem_file,
                                  [vs2vp_coeffs[1], vs2vp_offsets[1]],
                                  [vp2rho_coeffs[1], vp2rho_offsets[1]])
            lin_hi = bz_hi
        elif zmods_hi:
            print(col(Color.GREEN, "INFO:"), "generates lo. model in:", hi_mod)
            build_joint_ref_mod_and_surface_zmods(prem_file, zmods_hi, hi_mod)

        if(cwp_lo):
            print(col(Color.GREEN, "INFO:"), "generates lo. model in:", lo_mod)
            gen_neg_perturb_mod_with_coeffs(lo_mod, cwp_lo, prem_file)
        elif(lin_lo):
            print(col(Color.GREEN, "INFO:"), "generates lo. model in:", lo_mod)
            create_linear_prior_bound(lo_mod, lin_lo, prem_file,
                                      [vs2vp_coeffs[0], vs2vp_offsets[0]],
                                      [vp2rho_coeffs[0], vp2rho_offsets[0]])
        elif(bz_lo):
            print(col(Color.GREEN, "INFO:"), "generates lo. model in:", lo_mod)
            create_bz_prior_bound(lo_mod, bz_lo, prem_file,
                                  [vs2vp_coeffs[1], vs2vp_offsets[1]],
                                  [vp2rho_coeffs[1], vp2rho_offsets[1]])
            lin_lo = bz_lo
        elif zmods_lo:
            print(col(Color.GREEN, "INFO:"), "generates lo. model in:", lo_mod)
            build_joint_ref_mod_and_surface_zmods(prem_file, zmods_lo, lo_mod)
        if(plotting):
            # plot_prem = cwp_hi or cwp_lo
            plot_priors(hi_mod, lo_mod, prem_file, plot_prem=True)
    elif(layer_thickness or lin_hi or lin_lo):
        hi_mod = "loc_mod.hi"
        lo_mod = "loc_mod.lo"
        if(lin_hi):
            print(col(Color.GREEN, "INFO:"), "generates hi. model in:", hi_mod)
            loc_create_linear_prior_bound(hi_mod, lin_hi, layer_thickness,
                                      [vs2vp_coeffs[1], vs2vp_offsets[1]],
                                      [vp2rho_coeffs[1], vp2rho_offsets[1]])
        elif(bz_hi):
            print(col(Color.GREEN, "INFO:"), "generates hi. model in:", hi_mod)
            loc_create_bz_prior_bound(hi_mod, bz_hi, layer_thickness,
                                  [vs2vp_coeffs[1], vs2vp_offsets[1]],
                                  [vp2rho_coeffs[1], vp2rho_offsets[1]])
            lin_hi = bz_hi
        if(lin_lo):
            print(col(Color.GREEN, "INFO:"), "generates lo. model in:", lo_mod)
            loc_create_linear_prior_bound(lo_mod, lin_lo, layer_thickness,
                                      [vs2vp_coeffs[0], vs2vp_offsets[0]],
                                      [vp2rho_coeffs[0], vp2rho_offsets[0]])
        elif(bz_lo):
            print(col(Color.GREEN, "INFO:"), "generates lo. model in:", lo_mod)
            loc_create_bz_prior_bound(lo_mod, bz_lo, layer_thickness,
                                  [vs2vp_coeffs[1], vs2vp_offsets[1]],
                                  [vp2rho_coeffs[1], vp2rho_offsets[1]])
            lin_lo = bz_lo
        if(plotting):
            # plot_prem = cwp_hi or cwp_lo
            loc_plot_priors(hi_mod, lo_mod)
    else:
        help()
