#!python

import sys
from os import sep
from os.path import exists, dirname, isabs, join
import traceback
import re
from glob import glob
import matplotlib.pyplot as plt
import matplotlib
from getopt import getopt
import matplotlib.path as mpath
import matplotlib.patches as mpatches
from random import randint, random
import numpy as np
from py3toolset.nmath import zeropad
from neemuds.mcmc_deprecated_conf_parser import (
    # get_section_lines_from_conf,
    get_resdir_from_conf,
    get_num_markov_chains_from_conf,
    get_scale_from_conf_file,
    get_max_depth_from_conf_file,
    get_num_bz_curves_from_conf,
    get_runtype_num_of_iterations)
from neemuds.mcmc_config_parser import MCMCConfig

from neemuds.mcmc_deprecated_conf_parser import (GLOBAL, LOCAL, HOT_RUN,
                                                 COLD_RUN)
from py3toolset.fs import infer_path_rel_and_abs_cmds
import seaborn as sns
cmap = sns.cubehelix_palette(dark=0, light=1, as_cmap=True)
plt.rc("text", usetex=True)
plt.rc("font", family="serif")


def usage():
    cwd_cmd = infer_path_rel_and_abs_cmds(sys.argv)[0]
    print_frame("USAGE")
    print(bold(cwd_cmd)+""" <mcmc_conf_file>

     At the end of line, you must specify the Neemuds MCMC configuration file
     you want to plot some results.
     This file should be a .ini (new configuration format),
     .conf format is deprecated but still accepted temporarily (it is not
     maintained anymore).

     NOTE: it's expected that neemuds_mcmc.py has terminated successfully
     before launching this command to proceed with plotting.


    Main operation options:
        1/ --apoints|-a
        2/ --sep-apoints|-s
        3/ --best-mod|-b
        4/ --pdf|-d
        5/ --rand-mods|-n <number>
        6/ --gof-apoints|-g

    Assistance options:
        --help|-h
        --examples|-e

    Background plots: 1/ 2/ 4/ 6
    Foreground plots: 3/ 5/

    Compatibility:
        Background plots are not compatible with each other,
        Foreground plots are compatible with each other and also with
        background plots.

    Options for 3/ and 5/:
        --bz-samples|--neem-samples|--both-samples (default is bz-samples)
        (--neem-samples samples output, enabled with section #34 to 1 in conf.
          file)

    Options for all:
        --markov-chain|-m <id> (all chains by default, plotted in a row)

    Mandatory options (in all cases):
        -r|--run-type <cold|hot>
        -p|param VP|VS|RHO|XI|ETA
""")


def examples():
    cwd_cmd = infer_path_rel_and_abs_cmds(sys.argv)[0]
    prog = bold(cwd_cmd)
    # prog=sys.argv[0]
    print_frame("Examples")
    cmds = ["--apoints --run-type hot --params VS --markov-chains 0"
            " ./neemuds_mcmc_earth.ini",
            "-a -r hot -p VS,VP -m 0,1 ./neemuds_mcmc_earth.ini",
            "--sep-apoints --run-type hot -p VS --markov-chains 0"
            " ./neemuds_mcmc_earth.ini",
            "--best-mod -r hot -p VS -m 0 ./neemuds_mcmc_earth.ini",
            "--best-mod --neem-samples -r hot -p VS -m 0"
            " ./neemuds_mcmc_earth.ini",
            "--best-mod --both-samples -r hot -p VS -m 0"
            " ./neemuds_mcmc_earth.ini",
            "-a --best-mod --both-samples -r hot -p VS -m 0"
            " ./neemuds_mcmc_earth.ini",
            "--pdf -r hot -p VS -m 0 ./neemuds_mcmc_earth.ini",
            "--gof-apoints -r hot -p VS -m 0 ./neemuds_mcmc_earth.ini",
            "-b --rand-mods 5 --neem-samples -r hot -p VS -m 0"
            " ./neemuds_mcmc_earth.ini"
            ]
    for cmd in cmds:
        print(prog+" "+cmd)


def list_prior_files_in_profdir(prof_dir):
    # prof_dir existence must be verified by the caller
    gp = prof_dir+sep+'cold_run'+sep+'0'+sep+'prior_*'
    return glob(gp)


def get_prior_segs(prior_path):
    # prior_path existence must be verified by the caller
    z_coords = []
    p_min_coords = []
    p_max_coords = []
    f = open(prior_path)
    for line in f.readlines():
        if re.match(r"^\s*#.*", line):
            continue
        lfields = line.split()
        z_coords += [float(lfields[0])]
        p_min_coords += [float(lfields[1])]
        p_max_coords += [float(lfields[2])]
    # print(z_coords, p_min_coords, p_max_coords)
    return z_coords, p_min_coords, p_max_coords


def plot_prior(prior_path, plt=plt):
    z_coords, p_min_coords, p_max_coords = get_prior_segs(prior_path)
    for i in range(0, len(z_coords)-1):
        if z_coords[i] != z_coords[i+1]:
            # print(z_coords[i:i+2], p_min_coords[i:i+2])
            if i == 0:
                plt.plot(p_min_coords[i:i+2],  - np.array(z_coords[i:i+2]),
                         c='k', lw=1, label="prior min.")
                plt.plot(p_max_coords[i:i+2],  - np.array(z_coords[i:i+2]),
                         c='k', lw=2, label="prior max.")
            else:
                plt.plot(p_min_coords[i:i+2],  - np.array(z_coords[i:i+2]),
                         c='k', lw=1)
                plt.plot(p_max_coords[i:i+2],  - np.array(z_coords[i:i+2]),
                         c='k', lw=2)
        else:
            plt.plot(p_min_coords[i:i+2],  - np.array(z_coords[i:i+2]),
                     ls='--', c='k', lw=1)
            plt.plot(p_max_coords[i:i+2],  - np.array(z_coords[i:i+2]),
                     ls='--', c='k', lw=2)


def plot_param_prior(prof_dir, param_name, sp_ax):
    prior = get_prior_file_path_and_check(prof_dir, param_name)
    plot_prior(prior, sp_ax)


def get_param_file_path(prof_dir, mc_id, param_name, runtype):
    runtype_folder = runtype2folder(runtype)
    str_mc_id = zeropad(sc.nmchains, mc_id)
    return glob(join(prof_dir, runtype_folder, "*"+str_mc_id, param_name))[0]


def get_prior_file_path(prof_dir, param_name):
    # prior files are only in cold_run directory
    return glob(prof_dir+sep+"cold_run"+sep+"*"+sep+"prior_"+param_name)[0]


def get_prior_file_path_and_check(prof_dir, param_name):
    prior = get_prior_file_path(prof, param_name)
    check_file(prior, "\nPlease check the prior parameter "+param_name+" has"
               " been really calculated in the Neemuds MCMC execution and"
               " this execution terminated successfully. Finally, you could"
               " just try not to use this parameter in plotting...")
    return prior


def parse_bz_anchor_points(param_file_path, num_bcurves, tangents=False):
    z_coords = [[] for i in range(0, num_bcurves+1)]
    p_coords = [[] for i in range(0, num_bcurves+1)]
    with open(param_file_path) as f:
        i = 0
        for line in f.readlines():
            fields = line.split()
            z_coords[i] += [float(fields[1])]
            p_coords[i] += [float(fields[2])]
            i += 1
            i %= num_bcurves+1
    return z_coords, p_coords


def parse_bz_points_and_tangents(param_file_path, num_bcurves, mod_ids=None):
    z_coords = []
    p_coords = []
    tan_zpcoords = []
    with open(param_file_path) as f:
        for line in f.readlines():
            fields = line.split()
            if not mod_ids or int(fields[0]) in mod_ids:
                print("parse_bz_points_and_tangents() mod_id=", fields[0])
                z_coords += [float(fields[1])]
                p_coords += [float(fields[2])]
                if len(fields) > 3:  # first line of bezier curves group
                    tan_zpcoords += [[float(fields[3]), float(fields[4])]]
    return z_coords, p_coords, tan_zpcoords


def get_goodness_of_fit_filepath(prof_dir, mc_id, runtype):
    runtype_folder = runtype2folder(runtype)
    str_mc_id = zeropad(sc.nmchains, mc_id)
    filepath = join(prof_dir, runtype_folder, str_mc_id, "GOODNESS_OF_FIT")
    return filepath


def get_best_param_file_path(prof_dir, mc_id, param_name, runtype):
    runtype_folder = runtype2folder(runtype)
    str_mc_id = zeropad(sc.nmchains, mc_id)
    filepath = glob(join(prof_dir, runtype_folder, "*"+str_mc_id,
                         "BEST_"+param_name))[0]
    if not exists(filepath) and runtype == HOT_RUN:
        runtype_folder = runtype2folder(COLD_RUN)
        filepath = glob(join(prof_dir, runtype_folder, "*"+str(mc_id),
                             "BEST_"+param_name))[0]
    return filepath


def get_best_herrmann_file_path(prof_dir, mc_id, runtype, sc):
    get_best_full_model_file_path(prof_dir, mc_id, runtype, LOCAL, sc)


def get_best_mineos_file_path(prof_dir, mc_id, runtype, sc):
    get_best_full_model_file_path(prof_dir, mc_id, runtype, GLOBAL, sc)


def get_best_full_model_file_path(prof_dir, mc_id, runtype, scale, sc):
    """
    Gets the best full/bz-sampled model filepath.

    Args:
        prof_dir: dirpath of the McMC profile (result dir.).
        mc_id: Markov chain number.
        runtype: COLD_RUN or HOT_RUN.
        scale: GLOBAL or LOCAL (mineos/herrman prefix for the filepath).
        sc: VisuScriptConfig instance.

    Return:
        The filepath for the best model of Markov chain mc_id.
        If none found in HOT_RUN directory, the COLD_RUN one is returned.
    """
    # if file doesn't exist for hot run, get the cold run's one of same chain
    # (because it means there was no better mod found in hot run)
    if scale % 2 == GLOBAL:
        scale = "mineos"
    elif scale % 2 == LOCAL:
        scale = "herrmann"
    else:
        raise ValueError("Invalid scale.")
    runtype_folder = runtype2folder(runtype)
    # mc_id should be small (about thousands at worst)
    # zero-padding according to the total number of chains
    str_mc_id = zeropad(sc.nmchains, mc_id)
    filepath = join(prof_dir, runtype_folder, str_mc_id,
                    scale+"-"+runtype_folder+"-best-"+str_mc_id+".txt")
    if not exists(filepath) and runtype == HOT_RUN:
        runtype_folder = runtype2folder(COLD_RUN)
        filepath = join(prof_dir, runtype_folder, str_mc_id,
                        scale+"-"+runtype_folder+"-best-"+str_mc_id+".txt")
    print("get_best_"+scale+"_file_path()=", filepath)
    return filepath


def get_full_mod_file_paths2(sc, prof_dir, mc_id, runtype, rand_ids, scale):
    return get_full_mod_file_paths(sc.nites[runtype], prof_dir, mc_id, runtype,
                                   rand_ids, scale, sc)


def get_full_mod_file_paths(num_ites, prof_dir, mc_id, runtype, mod_ids,
                            scale, sc):
    """
    Gets the full/bz-sampled model filepaths of chain mc_id and iterations
    mod_ids.

    Args:
        num_ites: total number of iterations for the runtype.
        prof_dir: dirpath of the McMC profile (result dir.).
        mc_id: Markov chain number.
        runtype: COLD_RUN or HOT_RUN.
        mod_ids: the ids of the models to return (chain iterations).
        scale: GLOBAL or LOCAL (mineos/herrman prefix for the filepath).
        sc: VisuScriptConfig instance.

    Return:
        The filepaths for the model of Markov chain mc_id matching iterations
        in mod_ids.
        If none found in HOT_RUN directory, the COLD_RUN one is returned.
    """
    runtype_folder = runtype2folder(runtype)
    # mc_id should be small (about thousands at worst)
    # zero-padding according to the total number of chains
    str_mc_id = zeropad(sc.nmchains, mc_id)
    # more efficient (than glob()) to get number of iterations for this runtype
    # and forge the random filepaths
    if scale % 2 == GLOBAL:
        scale = "mineos"
    elif scale % 2 == LOCAL:
        scale = "herrmann"
    else:
        raise ValueError("Invalid scale.")
    rpaths = []
    # while(len(rpaths) < nrand):
    #    r = randint(1, num_ites)
    for i in mod_ids:
        str_i = zeropad(num_ites, i)
        rpath = join(prof_dir, runtype_folder, str_mc_id,
                     scale+"-"+runtype_folder+"-"+str_i+".txt")
        # print("get_full_mod_file_paths() rpath=", rpath)
        rpaths.append(rpath)
    return rpaths


def get_rand_mineos_file_path(prof_dir, mc_id, runtype, nrand):
    pass


def plot_param_points_at_rank_i(z_coords, p_coords, i, sp_ax=plt):
    if i == 0:
        istr = "1st"
    elif i == 1:
        istr = "2nd"
    elif i == 2:
        istr = "3rd"
    else:
        istr = str(i+1)+"th"
    istr += " Anchor Points"
    num_cols = len(matplotlib.rcParams['axes.prop_cycle'].by_key()['color'])
    # we cycle on the first color if i >= num_cols
    pt_col = \
        matplotlib.rcParams['axes.prop_cycle'].by_key()['color'][i % num_cols]
    sp_ax.scatter(p_coords[i],  - np.array(z_coords[i]), label=istr, c=pt_col)


def plot_param_points(z_coords, p_coords, sp_ax=plt):
    for i in range(0, len(z_coords)):
        plot_param_points_at_rank_i(z_coords, p_coords, i)


def plot_cubic_bz(ctrl_points, sp_ax, legend=False, color="b", lw=1,
                  ls='solid', label=''):
    Path = mpath.Path
    kwargs = {'fc': "none", 'color': color, 'lw': lw, 'ls': ls}
    if legend:
        kwargs['label'] = label
    pp1 = mpatches.PathPatch(
        Path(ctrl_points,
             [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]),
        **kwargs)
    sp_ax.legend()
    sp_ax.add_patch(pp1)


def plot_all_cubic_bz(z_coords, p_coords, tan_zpcoords, num_bcurves, sp_ax,
                      color="b", lw=1, ls='solid', label=''):
    j = 0  # current tangent index in tan_zpcoords
    i = 0
    cur_tanzp = None
    legend = True
    while i < len(z_coords)-1:
        if i % (num_bcurves+1) == 0 or i == 0:
            # new curve, get tangent
            cur_tanzp = tan_zpcoords[j]
            # print("cur_tanzp=", cur_tanzp, "z_coords[i]=", z_coords[i])
            print("plot_all_cubic_bz(), new model, i=", i, "j=", j)
            j += 1
        if i % (num_bcurves+1) != num_bcurves:
            ctrl_pts = [(p_coords[i], - z_coords[i]),  # first ctrl point
                        (p_coords[i]+cur_tanzp[1],
                         - z_coords[i]+cur_tanzp[0]),  # 2nd ctrl point
                        (p_coords[i+1]-cur_tanzp[1],
                         - z_coords[i+1]-cur_tanzp[0]),  # 3rd ctrl point
                        (p_coords[i+1], - z_coords[i+1])]  # 4th ctrl point
            if i > 0:
                legend = False  # legend one time for all bezier mods
            print("plot_cubic_bz(ctrl_pts=", ctrl_pts, ")")
            plot_cubic_bz(ctrl_pts, sp_ax, legend, color, lw, ls, label=label)
        i += 1


def plot_all_cubic_bz_in_file(path, num_bcurves, sp_ax, color="b", lw=1, ls='solid', label=''):
    z_coords, p_coords, tan_zpcoords = parse_bz_points_and_tangents(path, num_bcurves)
    plot_all_cubic_bz(z_coords, p_coords, tan_zpcoords, num_bcurves, sp_ax, color, lw, ls, label=label)


def plot_rand_cubic_bz_in_file(path, num_bcurves, sp_ax, rand_ids, color="b", lw=1, ls='solid', label=''):
    z_coords, p_coords, tan_zpcoords = parse_bz_points_and_tangents(path, num_bcurves, rand_ids)
    # all_ids = list(range(0, len(tan_zpcoords))) # num mods == num tangents
    # rand_ids = []
    rz_coords, rp_coords, rtan_zpcoords = [], [], []
#    while(len(rand_ids) < nrand):
#        r = all_ids[randint(0, len(all_ids)-1)]
#        all_ids.remove(r)
#        rand_ids.append(r)
#    for r in rand_ids:
#        rb = r*(num_bcurves+1)
#        rz_coords += z_coords[rb:rb+num_bcurves+1]
#        rp_coords += p_coords[rb:rb+num_bcurves+1]
#        rtan_zpcoords.append(tan_zpcoords[r])
    print("rand_ids=", rand_ids)
    plot_all_cubic_bz(z_coords, p_coords, tan_zpcoords, num_bcurves, sp_ax, color, lw, ls, label=label)


def get_random_mods_indices(prof_dir, mc_id, param_name, runtype, scale,
                            num_ites, nrand,
                            sc,
                            only_existing_sampled_models=False):
    path = get_param_file_path(prof_dir, mc_id, param_name, runtype)
    rand_ids = []
    all_ids = []
    with open(path) as pfile:
        all_ids += [int(line.split()[0]) for line in pfile.readlines()]
    if only_existing_sampled_models:
        for i in all_ids:
            mpath = get_full_mod_file_paths(num_ites, prof_dir, mc_id,
                                            runtype, [i], scale, sc)
            if not exists(mpath[0]):
                while all_ids.__contains__(i):
                    all_ids.remove(i)
    # delete duplicates
    all_ids = list(set(all_ids))
    # all_ids.sort()
    if nrand > len(all_ids):
        warn("The number of random models asked is greater than the number of"
             " models vailable. Diminishing this number to: "+str(len(all_ids)))
        nrand = len(all_ids)
    while(len(rand_ids) < nrand):
        r = all_ids[randint(0, len(all_ids)-1)]
        all_ids.remove(r)
        rand_ids.append(r)
    return rand_ids


def parse_mod_file(scale, path, param_name, max_depth):
    if scale == GLOBAL:
        return parse_mineos_mod_file(path, param_name, max_depth)
    elif scale == LOCAL:
        return parse_herr_mod_file(path, param_name)  #max_depth useless for herrman models (there is no prem linking)
    else:
        raise ValueError("Invalid scale.")


def parse_herr_mod_file(path, param_name):
    param_name = param_name.upper()
    if param_name not in ["VP", "VS", "RHO"]:
        raise Exception ("Invalid parameter name (must be VP, VS or RHO.")
    par_field_ids = {"VP": 1, "VS": 2, "RHO": 3}
    depths, par_vals = [], []
    with open(path) as f:
        for line in f.readlines():
            #print("line=", line)
            if not re.match(r"^\s*#.*", line):
                fields = line.split()
                depths.append(float(fields[0]))
                par_vals.append(float(fields[par_field_ids[param_name]]))
    return depths, par_vals


def parse_mineos_mod_file(path, param_name, max_depth):
    # TODO: test this function
    param_name = param_name.upper()
    if param_name not in ["VP", "VS", "RHO", "ETA"]: # TODO: check it's really ETA
        raise Exception ("Invalid parameter name (must be VP, VS, RHO or ETA.")
    par_field_ids = {"VP": 2, "VS": 3, "RHO": 1, "ETA": 8}
    radii, par_vals = [], []
    fields_per_line = 9
    with open(path) as f:
        f.readline() # skip at least first line of header
        for line in f.readlines():
            #print("line=", line)
            if not re.match(r"^\s*#.*", line):
                fields = line.split()
                if len(fields) < fields_per_line:
                    # still in header, skip the line
                    continue
                radii.append(float(fields[0]))
                par_vals.append(float(fields[par_field_ids[param_name]]))
    radii = np.array(radii)
    # convert to depths
    depths = (radii[-1]-radii[:])/1000 # mineos uses meters, we use km
    depths = depths[::-1]
    depths = list(depths[depths<=max_depth])
    par_vals = par_vals[::-1]
    par_vals = par_vals[:len(depths)]
    return depths, par_vals


def plot_mods_in_files(max_depth, scale, paths, param_name, sp_ax, color="b", continuous=True, ls='solid'):
    if scale % 2 == GLOBAL:
        plot_mineos_mods_in_files(max_depth, paths, param_name, sp_ax, color, continuous, ls)
    elif scale % 2 == LOCAL:
        plot_herr_mods_in_files(paths, param_name, sp_ax, color, continuous, ls)
    else:
        raise ValueError("Invalid scale.")


def plot_herr_mods_in_files(paths, param_name, sp_ax, color="b", continuous=True, ls='solid'):
    for path in paths:
        depths, par_vals = parse_herr_mod_file(path, param_name)
        sp_ax.plot(par_vals,  - np.array(depths), c=color, ls=ls)


def plot_mineos_mods_in_files(max_depth, paths, param_name, sp_ax, color='b', continuous=True, ls='solid'):
    for path in paths:
        depths, par_vals = parse_mineos_mod_file(path, param_name, max_depth)
        sp_ax.plot(par_vals,  - np.array(depths), c=color, ls=ls)


def runtype2str(runtype):
    if runtype == COLD_RUN:
        return "Cold Run"
    elif runtype == HOT_RUN:
        return "Hot Run"
    else:
        raise Exception("runtype value's not valid.")


def runtype_opt2int(opt):
    opt = opt.lower()
    if opt == "cold":
        return COLD_RUN
    elif opt == "hot":
        return HOT_RUN
    return None


def runtype2folder(runtype):
    if runtype == COLD_RUN:
        runtype_folder = "cold_run"
    elif runtype == HOT_RUN:
        runtype_folder = "hot_run"
    else:
        raise Exception("Unvalid runtype value: "+str(runtype))
    return runtype_folder


class VisuScriptConfig:

    long_opts = ["apoints", "sep-apoints", "run-type=", "params=", "markov-chains=", "best-mods", "bz-samples", "neem-samples", "both-samples", "rand-mods=", "pdf", "gof-apoints", "examples"]
    short_opts = "asr:p:m:bn:dge"

    def __init__(self, argv):
        self.parse_opts(argv)
        self.check_mandatory_opts()
        self.check_not_mandatory_opts()

    def parse_conf(self):
        if self.cfg_file.endswith('.conf'):
            self.prof_name = get_resdir_from_conf(self.cfg_file)
            self.scale = get_scale_from_conf_file(self.cfg_file) % 2
            self.nmchains = get_num_markov_chains_from_conf(self.cfg_file)
            self.max_depth = get_max_depth_from_conf_file(self.cfg_file)
            self.ncurves = get_num_bz_curves_from_conf(self.cfg_file)
            self.nites = {COLD_RUN: get_runtype_num_of_iterations(self.cfg_file,
                                                                  COLD_RUN),
                          HOT_RUN:
                          get_runtype_num_of_iterations(self.cfg_file, HOT_RUN)}
        elif self.cfg_file.endswith('.ini'):
            self.mcmc_conf = MCMCConfig(self.cfg_file)
            self.prof_name = self.mcmc_conf.profile_name
            self.scale = self.mcmc_conf.scale_type % 2
            self.nmchains = self.mcmc_conf.chain_number
            self.max_depth = self.mcmc_conf.max_depth
            self.ncurves = self.mcmc_conf.chain_bz3_numbers
            self.nites = {COLD_RUN:  self.mcmc_conf.cold_n_iters,
                          HOT_RUN: self.mcmc_conf.hot_n_iters}

    def parse_opts(self, argv):
        # default values
        self.runtype = None
        self.cfg_file = None
        self.cfg_dir = None
        self.params = None
        self.plotting_anchor_points = False
        self.plotting_sep_anchor_points = False
        self.plotting_best_mods = False
        self.plotting_bz_samples = False
        self.plotting_neem_samples = False
        self.plotting_both_samples = False
        self.num_rand_mods = 0
        self.plotting_pdf = False
        self.plotting_gof_apoints = False
        self.mchain_ids = None
        self.printing_examples = False
        if len(sys.argv) < 2 or contains_help_switch(argv[1:]):
            usage()
            exit(1)
            #raise Exception("Not any operation-option was specified.")
        else:
            opts, remaining = getopt(argv[1:], self.short_opts, self.long_opts)
            r_len = len(remaining)
            if r_len > 0:
                self.cfg_file = remaining[-1]
                self.parse_conf()
                check_file(self.cfg_file)
                self.cfg_dir = dirname(self.cfg_file)
                if r_len > 1:
                    warn("Remaining command line arguments ignored: " + repr(remaining[1:r_len]))
            for opt, val in opts:
                if opt in ("-r", "--run-type"):
                    self.runtype = runtype_opt2int(val)
                    self.check_opt("runtype")
                elif opt in ("-a", "--apoints"):
                    self.plotting_anchor_points = True
                elif opt in ("-s", "--sep-apoints"):
                    self.plotting_sep_anchor_points = True
                elif opt in ("-p", "--params"):
                    self.params = val.split(',')
                    self.check_opt("params")
                elif opt in ("-m", "--markov-chains"):
                    self.mchain_ids = val.split(',')
                    self.check_opt("markov-chains")
                elif opt in ("-b", "--best-mods"):
                    self.plotting_best_mods = True
                elif opt in ("--bz-samples"):
                    self.plotting_bz_samples = True
                elif opt == "--neem-samples": #not "in" to avoid confusion with -n
                    self.plotting_neem_samples = True
                elif opt in ("--both-samples"):
                    self.plotting_both_samples = True
                elif opt in ("--rand-mods", "-n"):
                    self.num_rand_mods = val
                elif opt in ("--pdf", "-d"):
                    self.plotting_pdf = True
                elif opt in ("--gof-apoints", "-g"):
                    self.plotting_gof_apoints = True
                elif opt in ("--examples", "-e"):
                    self.printing_examples = True
                    examples()
                    exit(0) # TODO: a way less dirty

    def check_mandatory_opts(self):
        gen_msg = "mandatory parameter not set: "
        if self.runtype == None:
            raise Exception(gen_msg + "option --run-type or -r")
        if self.params == None:
            raise Exception(gen_msg + "option --params or -p")

    def check_not_mandatory_opts(self):
        if not self.mchain_ids: #defaulty, empty --markov-chains option will
            # put the script to plot params for every single markov chain
            # cfg_file has normally already been retrieved at this point
            self.mchain_ids = list(range(0, self.nmchains))
        self.check_opt("rand-mods")
        self.check_bgplot_excl()

    def check_bgplot_excl(self):
        # check background plot exclusivity
        background_plots = [self.plotting_anchor_points, self.plotting_sep_anchor_points,
                            self.plotting_pdf, self.plotting_gof_apoints]
        num_enabled_opts = 0
        for opt in background_plots:
            if opt:
                num_enabled_opts+=1
                if num_enabled_opts>1: raise Exception("Background plots are not compatible with each other. That is, you can't use two options among: "+repr(["--"+self.long_opts[i] for i in self.get_bg_plot_longopt_ids()])+", or their short equivalent options: "+repr(["-"+self.short_opts[i] for i in self.get_bg_plot_shortopt_ids()]))

    def check_opt(self, opt):
        if opt == "runtype":
            if self.runtype not in [COLD_RUN, HOT_RUN]: raise Exception("run type option must be `cold' or `hot'.")
        elif opt == "params":
            for p in self.params:
                if p not in ["VP", "VS", "RHO", "XI", "ETA"]:
                    raise Exception("invalid parameter to plot: "+p)
        elif opt == "markov-chains":
            for i in range(0, len(self.mchain_ids)):
                if not str_isint(self.mchain_ids[i]):
                    raise Exception("--markov-chains option must receive integers. The value: "+self.mchain_ids[i]+" isn't an integer")
                self.mchain_ids[i] = int(self.mchain_ids[i])
                nmc = self.nmchains
                if self.mchain_ids[i] not in list(range(0, nmc)):
                    raise Exception("Unvalid markov chain index passed to option --markov-chains. Must be between 0 to "+(nmc-1)+" for the profile configuration: "+self.cfg_file)
        elif opt == "rand-mods":
            if not str_isint(str(self.num_rand_mods)):
                raise Exception("--rand-mods option must receive a integer. The value:"+self.num_rand_mods+" is not.")
            self.num_rand_mods = int(self.num_rand_mods)

    def get_bg_plot_longopt_ids(self):
        return [i for i in range(0, len(self.long_opts)) if self.long_opts[i] in ["apoints", "sep-apoints", "pdf", "gof-apoints"]]

    def get_bg_plot_shortopt_ids(self):
        return [i for i in range(0, len(self.short_opts)) if self.short_opts[i] in ["a", "s", "d", "g"]]

    def get_short_long_opt_pairs(self, long_ids, short_ids):
        return [(self.long_opts[i], self.short_opts[j]) for i, j in zip(long_ids, short_ids)]


    def __str__(self):
        _str = "VisuScriptConfig:\n"
        _str += "MCMC config. file: "+ self.cfg_file+"\n"
        _str += "Parameters to plot: "+str(self.params)+"\n"
        _str += "Run-type to plot: "+str(runtype2str(self.runtype))+"\n"
        _str += "Plotting apoints: "+str(self.plotting_anchor_points)+"\n"
        _str += "Plotting separated apoints: "+str(self.plotting_sep_anchor_points)+"\n"
        _str += "Plotting neemuds samples: "+str(self.plotting_neem_samples)+"\n"
        return _str

def choose_profile(profs):
    warn("There are several sub-profiles available for this profile. Please select the profile you want to plot:")
    choice = -1
    while (choice < 0 or choice >= len(profs)):
        for i, prof in enumerate(profs):
            print(bold("Type "+str(i)+ " to select: "+prof))
        print("Type enter to validate your selection (after entering the number).")
        print("Type the relevant number among "+str(list(range(0, len(profs))))+": ", end='')
        choice = input()
        if not str_isint(choice):
            choice = -1
            err("invalid input, please choose a valid number between 0 and "+len(profs)-1)
        else:
            choice = int(choice)
    return profs[choice]


def plot_param_anchor_points_and_prior(prof, param_name, mc_id, ncurves, runtype):
    print("Parameter Name:", param_name)
    main_sp = plt#.subplot(1,  - np.array(ncurves[mc_id]+2), 1)#ncurves[mc_id]+2) # this code is for the case we don't use plt.subplots() like below
    plot_param_prior(prof, param_name, main_sp)
    param_file_path = get_param_file_path(prof, mc_id, param_name, runtype)
    print("param_file_path=", param_file_path)
    z_coords, p_coords = parse_bz_anchor_points(param_file_path, ncurves)
    plot_param_points(z_coords, p_coords, main_sp)
    main_sp.legend()
    plt.title(param_name+" points ("+runtype2str(runtype)+", Markov Chain "+str(mc_id)+")")
    plt.ylabel("Depth (km)")
    plt.xlabel(param_name)
    return [main_sp.gca()]

def plot_param_separated_anchor_points_and_prior(prof, param_name, mc_id, ncurves, runtype, plot_best_mod=False):
    param_file_path = get_param_file_path(prof, mc_id, param_name, runtype)
    z_coords, p_coords = parse_bz_anchor_points(param_file_path, ncurves)
    #j = 1
    fig, subplots = plt.subplots(int((ncurves+2)/2), 2, sharex=False, sharey=False)
    fig.suptitle(param_name+" separated points ("+runtype2str(runtype)+", Markov Chain "+str(mc_id)+")")
    #for i in range(0, ncurves[mc_id]+1):
    subplots1d = []
    for i in range(0, ncurves+1):
        #i_sp = plt.subplot(2,  - np.array((ncurves[mc_id]+2)/2), j)
        y_sp = int(i / 2)
        x_sp = int(i % 2)
        i_sp = subplots[y_sp, x_sp]
        subplots1d.append(i_sp)
        if x_sp == 0:
            i_sp.set_xlabel(param_name)
        if y_sp+1 == int((ncurves+2)/2):
            # last subplot vertically
            i_sp.set_ylabel("Depth (km)")
        #j+=1
        prior = get_prior_file_path_and_check(prof, param_name)
        plot_prior(prior, i_sp)
        plot_param_points_at_rank_i(z_coords, p_coords, i, i_sp)
        #  if plot_best_mod:
        #     plot_all_cubic_bz_in_file(get_best_param_file_path(prof, 0, param_name, runtype), ncurves, i_sp)
        i_sp.legend()
    for x in [0, 1]:
        subplots[len(subplots)-1, x].set_ylabel("Depth (km)")
    if ncurves+1 < int((ncurves+2)/2)*2:
        subplots[len(subplots)-1, 1].set_visible(False)
        subplots[len(subplots)-2, 1].set_ylabel("Depth (km)")
    return subplots1d

def gen_rand_density_grid(size_z, size_p):
    grid = []
    for i in range(0, size_p):
        depth_line = []
        for j in range(0, size_z):
            depth_line += [random()]
#            if i < size_p/2:
#                depth_line += [1]
#            else:
#                depth_line += [0]
        grid += [depth_line]

    return grid

def list_goodnesses_of_fit(prof_dir, runtype, mc_id):
    filepath = get_goodness_of_fit_filepath(prof_dir, mc_id, runtype)
    mod_ids = []
    goodnesses_of_fit = []
    with open(filepath) as f:
        for line in f.readlines():
            f = line.split()
            mod_ids.append(int(f[0]))
            goodnesses_of_fit.append(float(f[1]))
    return mod_ids, goodnesses_of_fit

def build_pdf_grid(sc, prof_dir, runtype, mc_id, param_name,
                    grid_z_size, grid_p_size, scale, max_depth):
    """
    Args:
        sc: VisuScriptConfig
    """
    mod_ids, goodnesses_of_fit = list_goodnesses_of_fit(prof_dir, runtype, mc_id)
    min_gof = min(goodnesses_of_fit)
    grid = [[0 for i in range(0, grid_z_size)] for j in range(0, grid_p_size)]
    count_grid = [[0 for i in range(0, grid_z_size)] for j in range(0, grid_p_size)]
    # TODO: mineos !
    full_mod_files = get_full_mod_file_paths2(sc, prof_dir, mc_id, runtype,
                                              mod_ids, scale)
    prior_file = get_prior_file_path_and_check(prof, param_name)
    min_z, max_z, min_p, max_p = get_prior_zp_min_max(prior_file)
    dz = (max_z-min_z)/len(grid[0])
    dp = (max_p-min_p)/len(grid)
    for i, hfile in enumerate(full_mod_files):
        # if sample model doesn't exist it means the
        # option for outputting sampled model was disabled in mcmc*.conf/ini
        # TODO: check the option in mcmc*.conf/.ini and fails with error if not
        # enabled
        if not exists(hfile):
            continue
        depths, par_vals = parse_mod_file(scale, hfile, param_name, max_depth)
        dgof = abs(goodnesses_of_fit[i]-min_gof)
        #dgof = abs(goodnesses_of_fit[i])
        print("dgof=", dgof)
        for z, p in zip(depths, par_vals):
            gz, gp = min(int((z-min_z)/dz), grid_z_size-1), min(int((p-min_p)/dp), grid_p_size-1)
            print("z=", z, "p=", p, "gp=", gp, "gz=", gz)
            grid[gp][gz] += dgof
            count_grid[gp][gz] += 1
    sums = []
    for zi in range(0, len(grid[0])):
        s = 0
        for pi in range(0, len(grid)):
            s += grid[pi][zi]
        sums += [s]
#    print(sums)
    # normalize depth lines
    for zi in range(0, len(grid[0])):
        if sums[zi] <= 0: continue
        for pi in range(0, len(grid)):
            grid[pi][zi] /= sums[zi]
            print("grid[pi][zi]=", grid[pi][zi])
    return grid


def get_prior_zp_min_max(prior_file):
    z_coords, p_min_coords, p_max_coords = get_prior_segs(prior_file)
    min_z = min(z_coords)
    max_z = max(z_coords)
    min_p = min(p_min_coords)
    max_p = max(p_max_coords)
    return min_z, max_z, min_p, max_p


def plot_density_grid(grid, prior, sp_ax, n_meshes):
    min_z, max_z, min_p, max_p = get_prior_zp_min_max(prior)
    dz = (max_z-min_z)/len(grid[0])
    dp = (max_p-min_p)/len(grid)
    z_coords = [min_z]
    while(z_coords[-1] < max_z and len(z_coords) < len(grid[0])):
        z_coords += [z_coords[-1]+dz]
    z_coords[-1] = max_z
    p_coords = [min_p]
    while(p_coords[-1] < max_p and len(p_coords) < len(grid)):
        p_coords += [p_coords[-1]+dp]
    p_coords[-1] = max_p
    # we could plot simply with one pcolormesh like this:
    # sp_ax.pcolormesh(np.array(z_coords), np.array(p_coords), np.array(grid))
    # but to enhance visibilty we plot per depth layers, each one in a different pcolormesh
    pdz = int(len(z_coords)/n_meshes)
    for i in range(0, len(z_coords), pdz):
        z_vals = np.array([z_coords[min(k, len(z_coords)-1)] for k in
                           range(i, i+pdz+1)])
#        sp_ax.pcolormesh(z_vals,
#                         np.array(p_coords),
#                         np.array([[grid[j][min(k, len(z_coords)-1)] for k in range(i, i+pdz+1)] for j in range(0, len(grid))]))#, cmap="Greys")
        sp_ax.pcolormesh(np.array(p_coords),
                         - z_vals,
                         np.array([[grid[j][min(k, len(z_coords)-1)] for j in range(0, len(grid))] for k in range(i, i+pdz+1)]))#, cmap="Greys")
        print([[grid[j][i]] for j in range(0, len(grid))])
    sp_ax.colorbar()

def plot_gof_points(prof_dir, runtype, mc_id, ncurves, param_name, sp_ax, plotting_prior=False):
    # get all accepted models gofs and points
    mod_ids, goodnesses_of_fit = list_goodnesses_of_fit(prof_dir, runtype, mc_id)
    # we don't necessarily display all models (for the plot readability)
    max_num_mods = len(mod_ids)#5000 #TODO: max_num_mods should be an option
    param_file_path = get_param_file_path(prof, mc_id, param_name, runtype)
    z_coords, p_coords = parse_bz_anchor_points(param_file_path, ncurves)
    # gather displayed model infos (one model every step_sz ones)
    num_mods = len(mod_ids)
    step_sz = max(num_mods//(max_num_mods-1), 1)
    mod_ids = mod_ids[:num_mods:step_sz]
    goodnesses_of_fit = goodnesses_of_fit[:num_mods:step_sz]
    mod_ids = mod_ids[:max_num_mods]
    goodnesses_of_fit = goodnesses_of_fit[:max_num_mods]
    for i in range(0, len(z_coords)):
        z_coords[i] = z_coords[i][:num_mods:step_sz]
        p_coords[i] = p_coords[i][:num_mods:step_sz]
        z_coords[i] = z_coords[i][:max_num_mods]
        p_coords[i] = p_coords[i][:max_num_mods]
    min_gof = min(goodnesses_of_fit)
    max_gof = max(goodnesses_of_fit)
    # cmap = matplotlib.cm.get_cmap('viridis') #TODO: option for cmap type
    cmap = matplotlib.cm.ScalarMappable(cmap='viridis')
    norm = matplotlib.colors.Normalize(vmin=min_gof, vmax=max_gof)
    # norm(min_gof) == 0, norm(max_gof) == 1
    print([norm(gof) for gof in goodnesses_of_fit])
    colors = []
    # vars to group point per model id and not per anchor point level (like it was above)
    mi_z_coords = []
    mi_p_coords = []
    cmap.set_norm(norm)
    fig, ax = plt.subplots(1, 2, gridspec_kw={'width_ratios': [95, 5]})
    plot_param_prior(prof_dir, param_name, ax[0])
    for mi in range(0, len(mod_ids)):
        #col_arr = cmap.to_rgba(norm(goodnesses_of_fit[mi]), norm=False, bytes=True)
        col_arr = cmap.to_rgba(goodnesses_of_fit[mi], norm=True, bytes=True)
        #convert array to hex number and then to html color notation
        n = col_arr[3]+col_arr[2]*256+col_arr[1]*256**2+col_arr[0]*256**3
        for i in range(0, len(z_coords)):
            colors.append("#"+str(hex(n).split('x')[1]))
            #print(colors[-1])
            mi_z_coords.append(z_coords[i][mi])
            mi_p_coords.append(p_coords[i][mi])
    #now we can plot points per model with their gof color
    deft_marker_sz = matplotlib.rcParams['lines.markersize']
    matplotlib.rcParams['lines.markersize']= 3
    #for mi in range(0, len(mod_ids)):
    ax[0].scatter(mi_p_coords,  - np.array(mi_z_coords), c=colors, marker='.')
    #    print("mi=", mi, "/len(mod_ids)=", len(mod_ids), "col=", colors[mi])
    # plt.colorbar(np.linspace(min_gof, max_gof, 10))
    cb1 = matplotlib.colorbar.ColorbarBase(ax[1], cmap=matplotlib.cm.viridis, norm=norm, orientation='vertical')
    cb1.set_label('Goodness of Fit (log)')
    matplotlib.rcParams['lines.markersize'] = deft_marker_sz
    return ax[0]


if __name__ == '__main__':
    # add to pythonpath the script directory (needed if script launched through symlink in neemuds)
    # add to pythonpath the script parent directory (needed if the script is launched directly with its path)
    sys.path.append(dirname(sys.argv[0]))
    sys.path.append(join(dirname(sys.argv[0]), ".."))
    from py3toolset.txt_color import bold, print_frame, err, warn  # col, Color
    from py3toolset.fs import check_file
    from py3toolset.cmd_interact import contains_help_switch
    from py3toolset.nmath import str_isint
    try:
        sc = VisuScriptConfig(sys.argv)
        print(sc)
        scale = sc.scale
        prof_name = sc.prof_name
        # two possible prof_paths
        prof_path1 = prof_name  # absolute path or cwd
        prof_path2 = join(sc.cfg_dir, prof_name)  # in same dir as config file
        # Probe the effective path
        if isabs(prof_name) or sc.cfg_dir == '':
            prof_path = prof_path1
        else:
            prof_path = prof_path2
            if not glob(prof_path+"-*"):
                warn("no "+prof_path2+"* folder found, fall back to: "+prof_path1)
                prof_path = prof_path1
        max_depth = sc.max_depth
        profs = glob(prof_path+"-*")
        # if there are several profiles, ask user which one the script will have to analyze
        if len(profs) > 1:
            prof = choose_profile(profs)
            print("Selected profile:", prof)
        else:
            prof = profs[0]
        # TODO: if no profile dir found, notice user with error
        # print("profiles=", profs)
        for param_name in sc.params:
            nmc = sc.nmchains
            print("Number of Markov chains: ", nmc)
            ncurves = sc.ncurves
            if len(ncurves) < nmc:
                ncurves = ncurves[0:] + [ncurves[-1] for i in range(len(ncurves), nmc)]
            print("Numbers of Bezier curves for the chains:", ncurves)
            subplots1d = []

            for chain_idx in sc.mchain_ids:
                if sc.plotting_anchor_points:
                    subplots1d = plot_param_anchor_points_and_prior(prof, param_name, chain_idx, ncurves[chain_idx], sc.runtype)
                elif sc.plotting_sep_anchor_points:
                    subplots1d = plot_param_separated_anchor_points_and_prior(prof, param_name, chain_idx, ncurves[chain_idx], sc.runtype)
                elif sc.plotting_pdf:
                    plot_param_prior(prof, param_name, plt)
                    grid = build_pdf_grid(sc, prof, sc.runtype,
                                          chain_idx, param_name, 96, 50, scale, max_depth)
#                    print(grid)
                    plot_density_grid(grid, get_prior_file_path_and_check(prof, param_name), plt, 50)
                    subplots1d = [plt.gca()]
                elif sc.plotting_gof_apoints:
                    sp_ax = plot_gof_points(prof, sc.runtype, chain_idx, ncurves[chain_idx], param_name, plt, plotting_prior=True)
                    subplots1d = [sp_ax]
                else:
                    # no background plot then plot a minimal legend for
                    # possible foreground plots
                    plt.legend()
                    plt.xlabel(param_name)
                    plt.ylabel("depth (km)")
                if sc.plotting_best_mods:
                    if len(subplots1d) == 0:
                        plot_param_prior(prof, param_name, plt)
                        subplots1d = [plt.gca()]
                    for i_sp in subplots1d:
                        if sc.plotting_bz_samples or not sc.plotting_neem_samples:
                            plot_all_cubic_bz_in_file(get_best_param_file_path(prof, chain_idx, param_name, sc.runtype), ncurves[chain_idx], i_sp, color="r", lw=3, label='Best mod.')
                        if sc.plotting_neem_samples or sc.plotting_both_samples:
                            plot_mods_in_files(max_depth, scale,
                                               [get_best_full_model_file_path(prof,
                                                                              chain_idx,
                                                                              sc.runtype,
                                                                              scale,
                                                                              sc)], param_name, i_sp, color="r")
                if sc.num_rand_mods > 0:
                    num_ites = sc.nites[sc.runtype]
                    if len(subplots1d) == 0:
                        plot_param_prior(prof, param_name, plt)
                        subplots1d = [plt.gca()]
                    only_existing_sampled_models = (sc.plotting_neem_samples or
                                                    sc.plotting_both_samples)
                    rand_ids = get_random_mods_indices(prof, chain_idx,
                                                       param_name, sc.runtype,
                                                       scale, num_ites, sc.num_rand_mods,
                                                       sc,
                                                       only_existing_sampled_models)
                    print("rand_ids=", rand_ids)
                    for i_sp in subplots1d:
                        if sc.plotting_bz_samples or not sc.plotting_neem_samples:
                            plot_rand_cubic_bz_in_file(get_param_file_path(prof, chain_idx, param_name, sc.runtype), ncurves[chain_idx], i_sp, rand_ids, ls=":", label="Random mods")
                        if sc.plotting_neem_samples or sc.plotting_both_samples:
                            plot_mods_in_files(max_depth, scale,
                                               get_full_mod_file_paths2(sc, prof, chain_idx, sc.runtype, rand_ids, scale), param_name, i_sp, ls=":")
                plt.show()
        # print(get_section_lines_from_conf(sc.cfg_file, 26))
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        msg = str(e)
        err(msg)
