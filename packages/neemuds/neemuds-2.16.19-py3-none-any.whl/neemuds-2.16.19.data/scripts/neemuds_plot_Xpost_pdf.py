#!python

from getopt import getopt
from re import match
from sys import argv
from py3toolset.nmath import str_isint, str_isfloat
from glob import glob
from os import environ
environ['DONT_NEED_SAC'] = '1'
from neemuds_postmcmc import ok_print
from py3toolset.txt_color import warn, r, b, g, y, bold
from py3toolset.fs import infer_path_rel_and_abs_cmds
import numpy as np
from os.path import join, sep, basename, exists, expanduser
import matplotlib.pyplot as plt
import matplotlib

# TODO: replace use of /tmp by generic tempfile or something

class PlotXPostPDFOpts:

    opt_words = ['param', 'nminmax', 'xminmax', 'zminmax', 'binwidth',
                 'verbose', 'multiproc', 'fmax', 'modlist', 'save-only',
                 'width-height', 'envelope']
    short_opts = 'p:n:x:z:b:vmf:l:sw:e'
    long_opts = ["param=", "nminmax=", "xminmax=", "zminmax=", "binwidth=",
                 "verbose", "multiproc", "fmax=", "modlist=", "save-only",
                 "width-height=", "envelope"]

    valid_params = ['VPv', 'VSv', 'VPh', 'VSh', 'RHO', 'XI', 'ETA', 'K', 'MU']

    def __init__(self):
        # mandatory parameters
        self.param = None
        self.nminmax = None
        self.nmin = None
        self.nmax = None
        self.nfiles = None # derived parameter
        # optional parameters
        self.xminmax = None
        self.xmin = None # derived parameter
        self.xmax = None # derived parameter
        self.zminmax = None
        self.zmin = None # derived parameter
        self.zmax = None # derived parameter
        self.binwidth = None
        self.verbose = False
        self.save_only = False
        self.multiproc = False
        self.fmax = 100
        self.modlist = None
        self.width_height = None
        self.width = 640
        self.height = 480
        self.envelope = False

    def check_opt(self, opt_word):
        if opt_word == 'param':
            self.check_is_not_none(opt_word, self.param)
            self.check_type_str(opt_word, self.param)
            if not self.param in PlotXPostPDFOpts.valid_params:
                raise ValueError("The parameter "+self.param+" is unknown, "
                " valid ones are "+str(PlotXPostPDFOpts.valid_params)+". The value is case"
                " sensitive.")
        elif opt_word == 'nminmax':
            self.check_is_not_none(opt_word, self.nminmax)
            self.check_type_str(opt_word, self.nminmax)
            nminmax_err = ValueError('nminmax option value must be in the format'
                                     ' nmin:nmax where nmin and nmax are integers.')
            if m := match(r'(\d+):(\d+)', self.nminmax):
                self.check_type_int('nmin', m.group(1))
                self.check_type_int('nmax', m.group(2))
                self.nmin = int(m.group(1))
                self.nmax = int(m.group(2))
            else:
                raise nminmax_err
            self.nfiles = self.nmax - self.nmin + 1
            if self.nmin > self.nmax:
                raise ValueError('nmin must be less or equal to nmax.')
        elif opt_word == 'xminmax' and self.xminmax is not None:
            self.check_is_not_none(opt_word, self.xminmax)
            self.check_type_str(opt_word, self.xminmax)
            xminmax_err = ValueError('xminmax option value must be in the format'
                                     ' xmin:nmax where xmin and nmax are floats.')
            if m := match('([0-9.]+):([0-9.]+)', self.xminmax):
                self.check_type_float('xmin', m.group(1))
                self.check_type_float('xmax', m.group(2))
                self.xmin = float(m.group(1))
                self.xmax = float(m.group(2))
            else:
                raise xminmax_err
        elif opt_word == 'zminmax' and self.zminmax is not None:
            self.check_is_not_none(opt_word, self.zminmax)
            self.check_type_str(opt_word, self.zminmax)
            zminmax_err = ValueError('zminmax option value must be in the format'
                                     ' zmin:nmax where zmin and nmax are floats.')
            if m := match('([0-9.]+):([0-9.]+)', self.zminmax):
                self.check_type_float('zmin', m.group(1))
                self.check_type_float('zmax', m.group(2))
                self.zmin = float(m.group(1)) * 1000 # convert to meters
                self.zmax = float(m.group(2)) * 1000
                if self.zmin > self.zmax:
                    raise ValueError('zminmax option error: zmin must be lower'
                                     ' to zmax')
            else:
                raise zminmax_err
        elif opt_word == 'width-height':
            self.check_is_not_none(opt_word, self.width_height)
            self.check_type_str(opt_word, self.width_height)
            figsize_err = ValueError('width-height option value must be in the format'
                                     ' width:height where width and height are floats.')
            if m := match('([0-9.]+):([0-9.]+)', self.width_height):
                self.check_type_float('width', m.group(1))
                self.check_type_float('height', m.group(2))
                self.width = float(m.group(1))
                self.height = float(m.group(2))
            else:
                raise figsize_err
        elif opt_word == 'verbose':
            self.verbose = True
        elif opt_word == 'save-only':
            self.save_only = True
        elif opt_word == 'multiproc':
            self.multiproc = True
        elif opt_word == 'fmax' and self.fmax != 100:
                self.check_type_float(opt_word, self.fmax)
                self.fmax = float(self.fmax)
        elif opt_word == 'modlist' and self.modlist is not None:
            if not exists(self.modlist):
                raise ValueError('No readable file: '+self.modlist)
        elif opt_word == 'envelope':
            self.envelope = True
        else:
            raise ValueError('Unknown option '+opt_word)


    def check_all_opts(self):
        for opt_word in PlotXPostPDFOpts.opt_words:
            self.check_opt(opt_word)

    def check_type_str(self, name, var):
        if not isinstance(var, str):
            raise TypeError(name+' must be a str')

    def check_type_int(self, name, var):
        if not isinstance(var, int) and not str_isint(var):
            raise TypeError(name+' must be an integer but the value is:'
                    +str(var))

    def check_type_float(self, name, var):
        if not isinstance(var, float) and not str_isfloat(var, abs=False):
            raise TypeError(name+' must be a float but the value is: '+str(var))

    def check_is_not_none(self, name, var):
        if var is None:
            usage()
            raise TypeError(name+" option is mandatory (can't be None)")

    def print(self):
        print(g(bold('=== program option values:')))
        for opt_word in PlotXPostPDFOpts.opt_words:
            print(opt_word+":", getattr(self, opt_word.replace('-', '_')))
        print(g(bold('=== end')))


def parse_opts(getopt_str, opts: PlotXPostPDFOpts):
    opt_letters = PlotXPostPDFOpts.short_opts.replace(':', '')
    opt_words = [opt.replace('=', '') for opt in PlotXPostPDFOpts.long_opts]
    for opt, val in getopt_str:
        for i in range(len(opt_letters)):
            if opt in ["-"+opt_letters[i], "--"+opt_words[i]]:
                setattr(opts, opt_words[i].replace('-', '_'), val)
                opts.check_opt(opt_words[i])

def usage():
    cwd_cmd = infer_path_rel_and_abs_cmds(argv)[0]
    print(bold(r("USAGE:")), end=' ')
    print(bold(r(cwd_cmd)), r('-p|--param'), b('VPv|VSv|RHO|ETA|XI'),
          r('-n|--nminmax'), b('<nmin_int>:<nmax_int>'),
          '['+r('-x|--xminmax'), b('<xmin_float>:<xmax_float>')+']',
          '['+r('-z|--zminmax'), b('<zmin_float>:<zmax_float>')+']',
          '['+r('-f|--fmax'), b('<float>')+']',
          '['+r('-b|--binwidth'), b('<float>')+']',
          '['+r('-v|--verbose')+']',
          '['+r('-m|--multiproc')+']',
          '['+r('-l|--modlist'), b('<filepath>')+']',
          '['+r('-s|--save-only')+']',
          '['+r('-w|--width-height'), b('<float>:<float>')+']',
          '['+r('-e|--envelope')+']',
          '['+r('-h|--help')+']',
          )
    print()
    print(bold(r("OPTIONS:")))
    print(r('-h|--help') + ':', 'prints this help.')
    print(r('-p|--param'), b('VPv|VSv|RHO|ETA|XI') + ':', 'parameter to be'
          ' plotted.')
    print(r('-n|--nminmax'), b('<nmin_int>:<nmax_int>') + ':', 'min and max'
          ' indices of parameter input files taken into account in the PDF.\r\n'
          ' The indices are the ranks of the files taken in lexicographic order.')
    print(r('-x|--xminmax'), b('<xmin_float>:<xmax_float>') + ':', '(optional)'
          ' parameter value range considered in PDF and plot.\r\n If not used '
          'the range is automatically set according to values found in input files.')
    print(r('-z|--zminmax'), b('<zmin_float>:<zmax_float>') + ':', '(optional)'
          ' depth range considered in PDF and plot (in km).\r\n If not used the'
          ' range is automatically set according to values found in input files.')
    print(r('-b|--binwidth'), b('<float>') + ':', '(optional) PDF bin width'
          ' value (default is (xmax - xmin) / 50)')
    print(r('-f|--fmax'), b('<float>') + ':', '(optional) clipping value (%)'
          ' for histogram plotting (0 < fmax < 100). Default is 100%.')
    print(r('-v|--verbose') + ':', '(optional) verbose mode flag.')
    print(r('-m|--multiproc') + ':', '(optional) enables the'
          ' multiprocessing to build the histogram in parallel (useful if huge number of'
          ' files). It is not enabled by default. When enabled it uses as many'
          ' process as available (multiprocessing.cpu_count()).')
    print(r('-e|--envelope') + ':', '(optional) outputs inferior and superior '
          'envelopes of the nonzero posterior probability zone of the parameter.'
          ' The file in current working directory are: '
          '<parameter>-envelope_[sup|inf].txt (e.g. VPv-envelope.txt).'
          ' The envelope is also plotted on the figure.')
    print(r('-s|--save-only') + ':', '(optional) saves only the figure without'
          ' plotting (defaultly the figure is saved then plotted).')
    print(r('-w|--width-height'), b('<float>') + ':', '(optional) figure'
          ' width:height values in pixels (default is 640:480)')
    print(r('-l|--modlist'), b('<filepath>') + ':', '(optional)', 'list of'
          ' single model curves to be added to the pdf plot')
    print('Each line of the file at <filepath> must contain 3 fields:'
       ' model_filename | color (R, G, B, [A]) | pen_width')
    print('The model must be S.I. compliant.')
    print('../prior4mcmc/mod_earth_lo.zRHO          (0, 0, 0)     1')
    print('../prior4mcmc/mod_earth_hi.zRHO          (0, 0, 0)     1')
    print('../rand-mdl/0243_neemuds-out_03-0682.txt.zRHO    (.47, .75, 1)     3')
    print()
    print(bold(g('Additional information:')))
    print(g('This script is supposed to be used after neemuds_postmcmc.py'))
    print(g('Hint: 1st dry run without -x/-z to see how the PDF looks like'
            ' then define parameter and depth ranges in a second run.'))

def select_param_models(opts: PlotXPostPDFOpts):
    """
    Selects the parameter files in CWD according to opts.nmin/nmax indices.
    """
    pfiles = glob('*.z'+opts.param)
    if opts.verbose:
        ok_print("parameter files found:", pfiles)
    if len(pfiles) == 0:
        raise Exception('No parameter '+opts.param+' files found in cwd. Are'
                        ' you sure this is the good directory?')
    if len(pfiles) < opts.nfiles:
        raise Exception('Not enough parameter files found regarding the nmin,'
                        ' nmax values.')
    # opts.nmin <= opts.nmax, so it can't be any further trouble
    spfiles = pfiles[opts.nmin:opts.nmax+1] # selected files
    return spfiles

def make_zhist(li, lz, spfiles, bw, nbins, pmin, pmax, z_hists, output='array'):
    """
    Computes a part of histogram, for depths in lz for one parameter.

    Args:
        li: the indices of depths to process.
        lz: the depths to process.
        spfiles: the parameter files of the model to include in the histogram.
        bw: the bin width.
        nbins: the number of bins.
        pmin: the minimum parameter value of the considered range.
        pmax: the maximum parameter value of the considered range.
        z_hists: the output of the histogram, z_hists[i] receives the histogram
        part for the depth lz[i] (row format: bin pval, z, density).
        output: 'array' or 'file', z_hists is a list of array in the first case
        and a list of filepaths in the 2nd case.
    """
    # make the part of the full histogram for these z (at indices i)
    assert isinstance(li, (list, np.ndarray))
    assert isinstance(lz, (list, np.ndarray))
    for i, z in zip(li, lz):
        z_pvals = [] # all model parameter values at depth z
        for spfile in spfiles:
            # reopen the file for each z to avoid memory consumption
            # which might happen if all files are opened simultaneously
            pmod = np.loadtxt(spfile)
            if pmod[pmod[:, 0] == z, 1].size == 1:
                pz = pmod[pmod[:, 0] == z, 1].item() # param val at depth z
                z_pvals.append(pz)
            else:
                warn("No point or multiple points found in "+spfile+" for"
                     " z="+str(z))
            del pmod
        hist, bin_edges = np.histogram(z_pvals, bins=nbins, range=(pmin,
                                                                   pmax))
        hist = hist / len(z_pvals) * 100 # percentage
        # center the bins, bin_edges being on the left of the bins
        bin_centers = bin_edges[:-1] + bw / 2
        # make post pdf as z, param, density 2d array
        z_hist = np.hstack((bin_centers.reshape(-1, 1),
                            np.full((hist.size, 1), z),
                            hist.reshape(-1, 1)))
        if output == 'array':
            z_hists[i] = z_hist
        elif output == 'file':
            fp = '/tmp/z_hist'+'{i:04d}'.format(i=i)
            np.savetxt(fp, z_hist, fmt="%.6g")
            z_hists[i] = fp
        else:
            raise ValueError('output must be \'file\' or \'array\'')


def make_full_hist(opts: PlotXPostPDFOpts, spfiles: list[str]):
    """
    Returns the full histogram for the parameter selected with opts.param for the regularized model files spfiles.

    It proceeds depth layer per depth layer to construct partial histograms
    and then packs them all into a full histogram.
    The minimal and maximal bins are defined by opts.xmin, opts.xmax or
    defaulty by taking the min and max of the parameter values.
    """
    parallel = opts.multiproc
    # get z step (which is the same for all regularized models)
    pmod0 = np.loadtxt(spfiles[0])
    # the model has at least two layers
    z_step = pmod0[1,0] - pmod0[0, 0]
    # if opts.zmin is not in the models take the next point
    ezmin = pmod0[pmod0[:, 0] >= opts.zmin][0, 0]
    if ezmin != opts.zmin:
        warn('zmin adjusted to closest available depth in models: '+str(ezmin)+' m')
    # if opts.zmax is not in the models take the previous point
    ezmax = pmod0[pmod0[:, 0] <= opts.zmax][-1, 0]
    if ezmax != opts.zmax:
        warn('zmax adjusted to closest available depth in models: '+str(ezmax)+' m')
    if not ezmin < ezmax:
        raise ValueError('Invalid model '+spfiles[0]+' or invalid option'
                         ' zminmax')
    del pmod0
    full_hist = None # will receive full histogram (all z's)
    if opts.xmin is None or opts.xmax is None:
        pmin = min([min(np.loadtxt(spfile)[:, 1]) for spfile in spfiles])
        pmax = max([max(np.loadtxt(spfile)[:, 1]) for spfile in spfiles])
    else:
        pmin = opts.xmin
        pmax = opts.xmax
        if pmin > pmax:
            raise ValueError('xmin must be smaller than xmax.')
    nbins = 49
    bw = opts.binwidth if opts.binwidth is not None else (pmax - pmin) / (nbins
                                                                          + 1)
    if opts.verbose:
        ok_print("pmin=", pmin, "pmax=", pmax)
    if bw == 0:
        nbins = 1

    # set all z of the histogram
    # it's guaranteed that opts.zmin < opts.zmax (cf. PlotXPostPDFOpts.check_opt)
    depths = np.arange(ezmin, ezmax+1, z_step)
    nz = len(depths)
    z_hists = [0 for i in range(len(depths))]

    if parallel:
        from threading import Thread
        from multiprocessing import cpu_count
        nprocs = cpu_count()
        if opts.verbose:
            print(g(3*'=' + ' ' + str(nprocs) + ' cores will be used to build the histogram'))
        nz_per_thread = nz // nprocs
        # workload for each threads
        ths_work = np.empty(nprocs, dtype='int')
        r = nz - nz_per_thread * nprocs
        if r > 0:
            # the number of z is not evenly distributed to threads
            ths_work[0:r] = nz_per_thread + 1
            ths_work[r:] = nz_per_thread
        else:
            # the depths are evenly distributed to cores
            ths_work[0:] = nz_per_thread
        assert np.sum(ths_work) == nz
        # depth indices for all threads
        th_inds = []
        # depths for all threads
        th_zs = []
        for i in range(nprocs):
            if i == 0:
                th_inds.append(list(range(ths_work[i])))
            else:
                pl_id = th_inds[i-1][-1] # previous thread last z id
                th_inds.append(list(range(pl_id + 1, ths_work[i] +
                                     pl_id + 1)))
            th_zs.append(depths[th_inds[-1][0]:th_inds[-1][-1] + 1])
        # launch threads
        pmeth = 'process'
        if pmeth == 'multithread':
            # this method has shown to be a far slower than multiprocess meth
            threads = []
            for th_ind, th_z, tid in zip(th_inds, th_zs, np.arange(nprocs)):
                if opts.verbose:
                    print("thread:", tid, "will process depths:", th_z, " of"
                          " indices:", th_ind)
                t = Thread(target=make_zhist, args=(th_ind, th_z, spfiles,
                                                    bw, nbins, pmin, pmax, z_hists))
                t.start()
                threads.append(t)

            # wait all finished
            for t in threads:
                t.join()

            if opts.verbose:
                ok_print("All threads finished their work")
        else: # pmeth is 'process'
            from multiprocessing import Process
            processes = []
            for th_ind, th_z, tid in zip(th_inds, th_zs, np.arange(nprocs)):
                if opts.verbose:
                    print("process:", tid, "will treat depths:", th_z, " of"
                          " indices:", th_ind)
                p = Process(target=make_zhist, args=(th_ind, th_z, spfiles,
                                                    bw, nbins, pmin, pmax,
                                                     z_hists, 'file'))
                p.start()
                processes.append(p)

            # wait all finished
            for p in processes:
                p.join()

            # reconstruct the sequence of z_hists from files
            for (i, z), z_hist in zip(enumerate(depths), z_hists):
                fp = '/tmp/z_hist'+'{i:04d}'.format(i=i)
                z_hist = np.loadtxt(fp)
                z_hists[i] = z_hist

            if opts.verbose:
                ok_print("All processes finished their work")
    else:
        make_zhist(np.arange(nz), depths, spfiles, bw, nbins, pmin, pmax, z_hists)

    # all z_hists should be set

    # pack all z_hists in one histogram full_hist
    for (i, z), z_hist in zip(enumerate(depths), z_hists):
        if opts.verbose:
            fp = '/tmp/z_hist'+'{i:04d}'.format(i=i)
            ok_print("Outputting the histogram for z="+str(z)+" in:", fp)
            np.savetxt(fp, z_hist, fmt="%.6g")

        # complete the whole histogram
        if full_hist is None:
            full_hist = z_hist.copy()
        else:
            full_hist = np.vstack((full_hist, z_hist))

    param_unit = get_param_unit_from_spfile(spfiles[0])

    if opts.envelope:
        # TODO: should be refactored in a separate function
        envelope_inf = np.zeros((len(z_hists), 2))
        envelope_sup = np.zeros((len(z_hists), 2))
        for (i, z), z_hist in zip(enumerate(depths), z_hists):
            I = np.argsort(z_hist[:, -1])
            z_hist_sorted = np.copy(z_hist)
            z_hist_sorted = z_hist_sorted[I[::-1]]
            nzp_hist_sorted = z_hist_sorted[z_hist_sorted[:,2] > 0]
            pmin = np.min(nzp_hist_sorted[:,0])
            pmax = np.max(nzp_hist_sorted[:,0])
            envelope_inf[i, :] = (z, pmin)
            envelope_sup[i, :] = (z, pmax)

        np.savetxt(opts.param+'-envelope_inf.txt', envelope_inf,
                   header="z (m), "+param_unit.strip(),
                   fmt='%.6g')
        np.savetxt(opts.param+'-envelope_sup.txt', envelope_sup,
                   header="z (m), "+param_unit.strip(),
                   fmt='%.6g')

    fp = opts.param + "_full_hist.txt"
    ok_print("Output of the full histogram in:", fp)
    np.savetxt(fp, full_hist, fmt="%.6g", header=param_unit.strip()+", z (m),"
               " density prob (%)")
    return full_hist


def check_zminmax(opts: PlotXPostPDFOpts, spfiles: list[str]):
    """
    Verifies and sets opts.zmin, zmax values after parsing.
    """
    if opts.zmin is None or opts.zmax is None:
        # all models have the same working zone
        pmod0 = np.loadtxt(spfiles[0])
        opts.zmin = pmod0[0,0]
        opts.zmax = pmod0[-1,0]

def get_param_unit_from_spfile(spfile):
    with open(spfile) as f:
        l = f.readline()
        param_unit = l.split(',')[-1]
    return param_unit


def _extract_mineos_mod_param(opts: PlotXPostPDFOpts, file, param=None):
    """
     Extracts param column and converts radius to depth.

    """
    zcolid = 0
    if param is None:
        param = opts.param
    pstr = param.lower()
    if pstr == 'rho':
        # rho is in kg/m³ in the PREM, no need to convert
        pcolid = 1
    elif pstr == 'vpv':
        pcolid = 2
    elif pstr == 'vsv':
        pcolid = 3
    elif pstr == 'vph':
        pcolid = 6
    elif pstr == 'vsh':
        pcolid = 7
    elif pstr == 'eta':
        pcolid = 8
    elif pstr == 'k' or pstr == 'mu':
        VPv = _extract_mineos_mod_param(opts, file, 'VPv')
        VSv = _extract_mineos_mod_param(opts, file, 'VSv')
        RHO = _extract_mineos_mod_param(opts, file, 'RHO')
        if pstr == 'k':
            K = np.empty(VPv.shape, dtype=VPv.dtype)
            K[:, 0] = VPv[:, 0]
            K[:, 1] = (VPv[:,1]**2 - 4/3 * VSv[:,1]**2) * RHO[:,1]
            return K
        else: # pstr == 'mu'
            MU = np.empty(VPv.shape, dtype=VPv.dtype)
            MU[:, 0] = VPv[:, 0]
            MU[:, 1] = VSv[:,1]**2 * RHO[:,1]
            return MU
    elif pstr == 'xi':
        VSv = _extract_mineos_mod_param(opts, file, 'VSv')
        VSh = _extract_mineos_mod_param(opts, file, 'VSh')
        XI = np.empty(VSv.shape, dtype=VSv.dtype)
        XI[:, 0] = VSv[:, 0]
        XI[:, 1] = VSh[:, 1]**2 / VSv[:, 1]**2 # possible NaN if VSv == 0
        # (no worry, these parts won't be plotted by matplotlib)
        return XI
    else:
        raise ValueError("param "+str(opts.param)+" can't be extracted from a"
                         " mineos model file")
    mod = np.loadtxt(file, skiprows=3)[::-1, [zcolid, pcolid]]
    mod[:,0] = mod[0, 0] - mod[:, 0]
    return mod


def get_conv_pz_coeffs(f):
    # if the file contains a header, use the given units
    # for conversion
    # otherwise assume it's in S.I.
    depth_div = 1000 # assume model in meter, we plot km
    param_div = 1
    with open(f) as fmod:
        fline = fmod.readline()
        if m2 := match(r"\s*#.*\(([^)]+)\).*\(([^)]+)\)", fline):
            if m2.group(1).strip() in ['m', 'metre']:
                depth_div = 1000
            elif m2.group(1).strip() in ['km']:
                depth_div = 1
            if opts.param.lower() in ['vpv', 'vsv', 'vph',
                                     'vsh']:
                if m2.group(2).strip() in ['km/s', 'km.s-1', 'km.s^-1']:
                    param_div = 1/1000 # conv to meter in plot
            elif opts.param.lower() in ['rho']:
                if m2.group(2).strip() in ['g/cm^3', 'g/cm3', 'g.cm^-3', 'g.cm-3']:
                    param_div = 1/1000 # conv to kg/m^3
    return depth_div, param_div


def plot_pdf(opts: PlotXPostPDFOpts, full_hist, spfiles):
    """
    Plots the grid (PDF) from the histogram full_hist.

    Args:
        opts: the script options.
        full_hist: the PDF/histogram to plot.
        spfiles: the parameter model files (from which the function extracts
        header line to know the parameter unit).

    """
    f = plt.figure(num=1, figsize=(opts.width/100, opts.height/100))
    #plt.rcParams['figure.figsize'] = (opts.width, opts.height)
    pvals = full_hist[full_hist[:,1] == full_hist[0, 1]][:,0]
    zvals = np.unique(full_hist[:, 1])
    dvals = np.ndarray((len(zvals), len(pvals)))
    zi = 0
    for i in range(0, full_hist.shape[0], len(pvals)):
        dvals[zi, :] = full_hist[i:i+len(pvals), 2]
        zi += 1
    plt.title(opts.param+" MCMC post-PDF", fontweight='bold')
    # zvals is in meters (cf. neemuds_postmcmc)
    # plot it in km
    my_cmap = matplotlib.cm.get_cmap('jet')
    my_cmap.set_under('w') # zero to white color (works with vmin set below)
    pc = plt.pcolormesh(pvals, zvals / 1000, dvals,
                        cmap=my_cmap, vmin=1e-16,
                        vmax=min(opts.fmax, np.max(dvals)), norm="linear")
    plt.gca().invert_yaxis()
    plt.ylabel('depth (km)')
    plt.colorbar(pc)
    # TODO: maybe convert m/s into km/s ?
    param_unit = get_param_unit_from_spfile(spfiles[0])
    plt.xlabel(param_unit)
    plt.tight_layout()
    if opts.modlist is not None:
        with open(opts.modlist) as f:
            modlist = f.readlines()
            for mline in modlist:
                if m := \
                        match(r'^([^\s#]+)\s+\((([0-9.]+,\s*){2}[0-9.]+)\)\s+(\d+)\s*(format=([^\s]+))?.*$',
                              mline.strip()):
                    for f in glob(expanduser(m.group(1))):
                        if  m.lastindex >= 5:
                            format=m.group(6)
                            if opts.verbose:
                                print("file=", f)
                                print("format=", format)
                            if format == 'mineos':
                                mod = _extract_mineos_mod_param(opts, f)
                            else:
                                raise ValueError('Unknown file format: '
                                                 +format)
                        else:
                            mod = np.loadtxt(f)
                        c = [float(s) for s in m.group(2).split(',')]
                        pw = int(m.group(4)) # pen width
                        depth_div, param_div = get_conv_pz_coeffs(f)
                        if len(mod) <= 2:
                            # in case of two points model, interpolate points
                            # in between according to the layer thickness of
                            # explored models
                            nli = int(((mod[1,0] - mod[0,0])/depth_div)/((zvals[1] -
                                                             zvals[0]) / 1000))
                            mod_li = np.empty((nli, 2), dtype=mod.dtype)
                            mod_li[:,0] = np.linspace(mod[0, 0], mod[1, 0],
                                                      nli)
                            mod_li[:,1] = np.linspace(mod[0, 1], mod[1, 1],
                                                      nli)
                            mod = mod_li
                        mod = mod[mod[:, 0] / depth_div >= zvals[0] / 1000]
                        mod = mod[mod[:, 0] / depth_div <= zvals[-1] / 1000]
                        plt.plot(mod[:, 1] / param_div, mod[:, 0] / depth_div,
                                 c=c, linewidth=pw, linestyle='--',
                                 label=basename(m.group(1)))
    if opts.envelope:
        for side in ['inf', 'sup']:
            f = opts.param+'-envelope_'+side+'.txt'
            e_side = np.loadtxt(f)
            depth_div, param_div = get_conv_pz_coeffs(f)
            e_side = e_side[e_side[:, 0] / depth_div >= zvals[0] / 1000]
            e_side = e_side[e_side[:, 0] / depth_div <= zvals[-1] / 1000]
            plt.plot(e_side[:, 1] / param_div, e_side[:, 0] / depth_div,
                     linestyle="dotted", marker='^',
                     label="envelope "+side, linewidth=3, c='gray')
    plt.legend()
    plt.savefig(opts.param+'.png')
    if not opts.save_only:
        plt.show()

if __name__ == '__main__':
    if len(argv) == 1 or '-h' in argv or '--help' in argv:
        usage()
        exit(0)
    opts = PlotXPostPDFOpts()
    opts_str, remaining = getopt(argv[1:], PlotXPostPDFOpts.short_opts,
                                 PlotXPostPDFOpts.long_opts)
    parse_opts(opts_str, opts)
    if opts.verbose:
        opts.print()
    spfiles = select_param_models(opts)
    ok_print("Selected files:", spfiles)
    check_zminmax(opts, spfiles)
    full_hist = make_full_hist(opts, spfiles)
    plot_pdf(opts, full_hist, spfiles)
