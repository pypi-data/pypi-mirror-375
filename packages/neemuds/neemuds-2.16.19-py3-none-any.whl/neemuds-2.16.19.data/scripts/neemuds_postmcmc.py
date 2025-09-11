#!python
from getopt import getopt
from os.path import exists, join, isfile, basename, sep
from os import environ, symlink, remove, system, mkdir
from glob import glob
from sys import argv, stderr
from py3toolset.nmath import str_isint, str_isfloat
from py3toolset.txt_color import warn, r, b, g, bold
from py3toolset.nmath import zeropad
from py3toolset.fs import (check_file, count_file_lines,
                        infer_path_rel_and_abs_cmds,
                        copy_file_with_rpath)
from re import match
import numpy as np
from shutil import copyfile
from multiprocessing import Process, cpu_count

environ['DONT_NEED_SAC'] = '1'
from neemuds.mcmc_config_parser import MCMCConfig  # noqa: E402

MAX_RSYNC_TRIALS = 10

"""
 Script to post process all models inferred during neemuds_mcmc.
"""


class PostMCMCOpts:

    opt_words = ['mcmc_conf_file', 'mcmc_directory', 'decimation_factor',
                 'n_models', 'rsync_src', 'n_csv_models', 'theoretical_max']
    short_opts = 'f:d:e:n:r:c:t:'
    long_opts = ["mcmc_conf_file=", "mcmc_directory=", "decimation_factor=",
                 "n_models=", "rsync_src=", "n_csv_models=",
                 "theoretical_max="]

    def __init__(self):
        # mandatory parameters
        self.mcmc_conf_file = None
        self.mcmc_directory = None
        self.decimation_factor = None
        self.n_models = None
        # optional parameters
        self.rsync_src = '.'
        self.n_csv_models = None
        self.theoretical_max = None

    def check_opt(self, opt_word):
        if opt_word == 'mcmc_conf_file':
            self.check_is_not_none(opt_word, self.mcmc_conf_file)
            self.check_type_str(opt_word, self.mcmc_conf_file)
            if not exists(self.mcmc_conf_file):
                raise Exception('The filepath ' +
                                self.mcmc_conf_file+' doesn\'t '
                                ' exist')
            if not self.mcmc_conf_file.endswith('.ini'):
                raise ValueError('mcmc_conf_file must ends with .ini and'
                                 ' respect the proper format (.conf format is'
                                 ' not supported.')
        elif opt_word == 'mcmc_directory':
            self.check_is_not_none(opt_word, self.mcmc_directory)
            self.check_type_str(opt_word, self.mcmc_directory)
            # delay directory existence checking to try_pre_download_mcmc_dir
        elif opt_word == 'decimation_factor':
            self.check_is_not_none(opt_word, self.decimation_factor)
            self.check_type_int(opt_word, self.decimation_factor)
            self.decimation_factor = int(self.decimation_factor)
        elif opt_word == 'n_models':
            self.check_is_not_none(opt_word, self.n_models)
            self.check_type_int(opt_word, self.n_models)
            self.n_models = int(self.n_models)
        # not mandatory options
        elif opt_word == 'rsync_src':
            if self.rsync_src is not None:
                self.check_type_str(opt_word, self.rsync_src)
                if (match(r'[^\s]+@[^\s]+:[^\s]+', self.rsync_src) is None
                        and not exists(self.rsync_src)):
                    raise ValueError('rsync_src error: the expected format is '
                                     'user@host:path but the value is: '
                                     + str(self.rsync_src) + ' which doesn\'t '
                                     'exist locally either.')

        elif opt_word == 'n_csv_models':
            if self.n_csv_models is not None:
                self.check_type_int(opt_word, self.n_csv_models)
                self.n_csv_models = int(self.n_csv_models)
        elif opt_word == 'theoretical_max':
            if self.theoretical_max is not None:
                self.check_type_float(opt_word, self.theoretical_max)
                self.theoretical_max = float(self.theoretical_max)

    def check_all_opts(self):
        for opt_word in PostMCMCOpts.opt_words:
            self.check_opt(opt_word)

    def check_type_str(self, name, var):
        if not isinstance(var, str):
            raise TypeError(name+' must be a str')

    def check_type_int(self, name, var):
        if not isinstance(var, int) and not str_isint(var):
            raise TypeError(name+' must be an integer but the value is:'
                            + str(var))

    def check_type_float(self, name, var):
        if not isinstance(var, float) and not str_isfloat(var, abs=False):
            raise TypeError(name +
                            ' must be a float but the value is: '
                            + str(var))

    def check_is_not_none(self, name, var):
        if var is None:
            usage()
            raise TypeError(name+" option is mandatory (can't be None)")

    def print(self):
        print(g(bold('=== program option values:')))
        for opt_word in PostMCMCOpts.opt_words:
            print(opt_word+"=", getattr(self, opt_word))
        print(g(bold('=== end')))


def examples():
    cwd_cmd = infer_path_rel_and_abs_cmds(argv)[0]
    print(bold(r("EXAMPLES:")))
    print('\t'+bold(r(cwd_cmd)),
          r('-d'), b('mcmc_local-R/hot_run'),
          r('-f'), b('neemuds_mcmc_local.ini'),
          r('-r'),
          b('my_name@machine.ccipl.univ-nantes.fr:/scratch/LPGN/my_name'),
          r('--decimation_factor'), b('3'),
          r('-n'), b('10000'))
    print('\t'+bold(r(cwd_cmd)),
          r('-d'), b('mcmc_mars_global-RL/hot_run'),
          r('-f'), b('neemuds_mcmc_mars_n10_20181128.ini'),
          r('-e'), b('2'),
          r('-n'), b('10000'),
          r('-t'), b('-5.0'),
          r('--n_csv_models'), b('10000'))
    print('\t'+bold(r(cwd_cmd)),
          r('-d'), b('mcmc_earth_global-R/hot_run'),
          r('-f'), b('neemuds_mcmc_earth.ini'),
          r('-r'),
          b('my_name@machine.ccipl.univ-nantes.fr:/scratch/LPGN/my_name/'
            '2006319BFOBHZ-r1/mcmc_earth_global-R/hot_run'),
          r('--decimation_factor'), b('2'),
          r('-n'), b('10000'))


def usage():
    cwd_cmd = infer_path_rel_and_abs_cmds(argv)[0]
    print(bold(r("USAGE:")), end=' ')
    print(bold(r(cwd_cmd)), r('-f|--mcmc_conf_file'), b('<filepath>'),
          r('-d|--mcmc_directory'),
          b('<directory path>'), r('-e|--decimation_factor'), b('<integer>'),
          r('-n|--n_models'), b('<integer>'),
          b('[') + r('-r|--rsync_src'),
          b('<user@host:filepath>]'),
          b('[') + r('-c|--n_csv_models'),
          b('<integer>') +
          b(']') +
          b('[') + r('-t|--theoretical_max'),
          b('<float>') +
          b(']'),
          b('[')+r('-h|--help')+b(']'))
    print()
    print(bold(r("OPTIONS:")))
    print(r('-h|--help') + ':', 'prints this help.')
    print(r('-f|--mcmc_conf_file'), b('<filepath>') + ':', 'neemuds_mcmc'
          ' configuration file (neemuds_mcmc_local.ini,'
          ' neemuds_mcmc_earth.ini, ...).')
    print(r('-d|--mcmc_directory'),
          b('<directory path>') + ':', 'path of the MCMC result directory'
          ' containing all process sub-directories (00, 01, 02...).')
    print(r('-e|--decimation_factor'), b('<integer>') +
          ':', 'for decimation in'
          ' order to avoid model covariances'
          ' (1 model every X models, X=2, 3, 4).')
    print(r('-n|--n_models'), b('<integer>') + ':', 'amount of retained'
          ' models to compute the posterior pdfs')
    print(b('[') + r('-r|--rsync_src'),
          b('<user@host:filepath>]') + ':',
          '(optional) ssh address used by rsync to download model files. If no'
          ' address is given then the directory is read locally. The filepath'
          ' must points the parent directory of the mcmc_* directory passed to'
          ' option -d.')
    print(b('[') + r('-c|--n_csv_models'),
          b('<integer>') +
          b(']') + ':', '(optional) amount of selected models only for csv'
          ' plots (sGoF.csv) which can'
          ' differ from n_models. By default this is the same value that'
          ' n_models.')
    print(b('[') + r('-t|--theoretical_max'),
          b('<float>') +
          b(']') + ':', '(optional) theoretical maximum GoF value'
          ' (threshold to ensure'
          ' consistent models). By default, the value is -10.')
    print()
    examples()


def parse_opts(getopt_str, opts: PostMCMCOpts):
    opt_letters = PostMCMCOpts.short_opts.replace(':', '')
    opt_words = [opt.replace('=', '') for opt in PostMCMCOpts.long_opts]
    for opt, val in getopt_str:
        for i in range(len(opt_letters)):
            if opt in ["-"+opt_letters[i], "--"+opt_words[i]]:
                setattr(opts, opt_words[i], val)
                opts.check_opt(opt_words[i])


def ok_print(*args):
    print(g(bold('[OK]')), *args)


def check_mcmc_dirs(opts, conf):
    """
    Makes an integrity checking up of MCMC output directories.

    It creates symbolic links VPv -> VP, VSv -> VS.
    According to conf and opts, it verifies that:
    - no junk file is located in opts.mcmc_directory,
    - no markov chain/proc directory is missing,
    - no unexpected markov chain is found.


    Args
        opts: the parsed options of this script.
        conf: the parsed configuration of the MCMC (option
        -f|--mcmc_conf_file).

    """
    for vfile in (glob(opts.mcmc_directory+'/*/VP') +
                  glob(opts.mcmc_directory+'/*/VS')):
        if not exists(vfile+'v'):
            symlink(basename(vfile), vfile+'v')
    # test if there are files that shouldn't be in opts.mcmc_directory
    # they should be deleted
    extra_files = [f for f in glob(opts.mcmc_directory+'/*') if isfile(f)]
    # verify that the markov chain directories match the number of markov
    # chains defined in configuration
    expected_chain_dirs = zeropad(conf.chain_number,
                                  list(range(0, conf.chain_number)))
    found_chain_dirs = [basename(p) for p in glob(opts.mcmc_directory+'/*')]
    found_chain_dirs.sort()
    # sort because glob might return
    # chain dirs in order 0 3 2 1
    missing_chain_dirs = [join(opts.mcmc_directory, ed)
                          for ed in expected_chain_dirs if
                          found_chain_dirs.count(ed) == 0]
    extra_chain_dirs = [join(opts.mcmc_directory, ed)
                        for ed in found_chain_dirs if
                        expected_chain_dirs.count(ed) == 0]

    if len(extra_files) > 0:
        raise Exception("Extra files (to be removed)"
                        " in " + opts.mcmc_directory + ": " +str(extra_files))
    if len(missing_chain_dirs) > 0:
        raise Exception("Missing directories (to be added?) in " +
        opts.mcmc_directory + " (maybe by copying "
        "them from cold-run directories if you're working on hot-runs): ",
        str(missing_chain_dirs))
    if len(extra_chain_dirs) > 0:
        raise Exception("Extra directories (to be removed) in "+
                opts.mcmc_directory+ ": "+str(extra_chain_dirs))

    check_mchain_dirs(opts, conf)


def check_mchain_dirs(opts, conf):
    """
    Checks there is no missing chain markov directory according to the number
    defined in configuration.


    Args
        opts: the parsed options of this script.
        conf: the parsed configuration of the MCMC (option
        -f|--mcmc_conf_file).

    """
    chain_indices = [int(basename(d)) for d in glob(opts.mcmc_directory+'/*')]
    # chain_indices could be in any order
    if (np.sort(np.array(chain_indices)) != np.arange(conf.chain_number)).any():
        raise Exception('Mismatch between the number of chains of Markov '+
                str(conf.chain_number)+' and'
                ' directories found in '+opts.mcmc_directory+'. It\'s most'+
                ' likely that a directory is missing.')

def chain_id2name(conf: MCMCConfig, cid):
    """
    Converts a chain directory index to its name (basically zeropad str(id))

    Args:
        conf: (MCMCConfig) parse configuration (-f|--mcmc_conf_file option).
        cid: chain id (integer).

    Return:
        the zero-padded chain directory name.
    """
    nprocs = conf.chain_number
    sid = str(cid)
    nz = len(str(nprocs)) - len(sid)
    return "0"*nz + sid

def lock():
    """
    This function create a lock to prevent parallel calls of neemuds_postmcmc.py


    Args
        opts: the parsed options of this script.
        conf: the parsed configuration of the MCMC (option
        -f|--mcmc_conf_file).

    """
    #TODO: it could be limited to one MCMC directory
    # avoid parallel execution of this script using a lockfile
    lockfile = '/tmp/'+basename(argv[0]).replace('.py', '')+'.lock'
    if exists(lockfile):
        raise Exception('Another instance of this script is/was running. '
                'Please wait the termination of that instance or if it has failed'
                ' to terminate correctly remove the lock file: '+lockfile)
    else:
        lfd = open(lockfile, 'w')
        lfd.close()

def release_lock():
    """
    Releases the lock put but the lock() function.
    """
    lockfile = '/tmp/'+basename(argv[0]).replace('.py', '')+'.lock'
    if exists(lockfile):
        remove(lockfile)

def get_chain_bz_npts(conf, chain_id):
    """
    Returns the number of Bezier points for a given Markov chain.

    Args
        conf: the parsed configuration of the MCMC (option
        -f|--mcmc_conf_file).
        chain_id: the index of the Markov chain of interest.
    """
    a = np.array(conf.chain_bz3_numbers)
    return a[chain_id] + 1 # the number of curves + 1


def check_vsv_zmax(opts, conf):
    """
    Verifies for each Markov chains that the zmax found in VSv parameter file is equal to conf.max_depth

    It is verified only for local scale because for glocal case it is
    a join point obtained from the reference model

    Args
        opts: the parsed options of this script.
        conf: the parsed configuration of the MCMC (option
        -f|--mcmc_conf_file).

    """
    chain_dirs = [d for d in glob(opts.mcmc_directory+'/*')]
    chain_dirs.sort() # because glob can returns chain dirs in order 0 3 2 1

    if conf.scale_type % 2 == 0:
        for i, chain_dir in enumerate(chain_dirs):
            vsv_file = join(chain_dir, 'VSv')
            vsv_data = np.loadtxt(vsv_file, usecols=1)
            vsv_max_depth = vsv_data[:get_chain_bz_npts(conf, i)][-1]
            #vsv_max_depth = vsv_data[-1]
            #print("chain:", i, "vsv_file zmax:", vsv_max_depth)
            if conf.max_depth != vsv_max_depth:
                raise Exception('Mismatch max depth between configuration '
                        +str(conf.max_depth)+' and the one found in VSv file:'
                        +vsv_file+' which is: '+str(vsv_max_depth))

def truncate_chains(inds, chain_dirs, opts, conf):
    """See truncate. This function makes the work sequentially for a subset of chains.

    Args:
        inds: the indices of chains processed.
        chain_dirs: the directory paths of chains processed.

    """
    for mc_ind, chain_dir in zip(inds, chain_dirs):
        chain_bz_npts = get_chain_bz_npts(conf, mc_ind)
        gof_file = join(chain_dir, 'GOODNESS_OF_FIT')
        check_file(gof_file)
        # check ACCEPTANCE, that must exist too
        check_file(join(chain_dir, 'ACCEPTANCE'))
        # initialize the minimum number of lines
        # with GOODNESS_OF_FIT
        nfloor = count_file_lines(gof_file)
        truncating = False # need to truncate (True) or not
        files = ['ACCEPTANCE', 'VSv', 'VPv', 'RHO', 'ETA', 'XI', 'K', 'MU',
                 'RAYL-GVELS', 'LOVE-GVELS', 'GOODNESS_OF_FIT']
        all_files = glob(join(chain_dir, '*'))
        files = [basename(f) for f in all_files if basename(f) in files]
        its = {} # iterations found for all models
        runtype = opts.mcmc_directory.split('/')[-1]
        if runtype == '': # the directory path ends with /
            runtype = opts.mcmc_directory.split('/')[-2]
        itermax = conf.cold_n_iters if \
              runtype == 'cold_run' else conf.hot_n_iters
        # iterations starts at 1 before (we are before it 0 insertion)
        # (if it0 was already inserted in a previous run, it is ignored)
        conf_its = np.arange(1, itermax + 1, dtype='int') # iterations in all
                                                          # models according to conf
        common_its = conf_its # iterations in all models (modified later)
        # no need to copy, it is not overridden later
        files_to_truncate = []
        for file in files:
            filepath = join(chain_dir, file)
            if file in ['RAYL-GVELS', 'LOVE-GVELS']:
                its[file] = np.unique(np.loadtxt(filepath, skiprows=1,
                                                 usecols=0)).astype('int')
            else:
                its[file] = np.unique(np.loadtxt(filepath,
                                                 usecols=0)).astype('int')
            f_its = its[file]
            f_its = f_its[f_its != 0] # ignored possible it 0
            if (len(f_its) < len(conf_its) or not
            np.allclose(np.sort(f_its), conf_its)):
                missing_ites = [i for i in conf_its
                                if i not in f_its]
                # missing iteration intervals
                mii = _ites_to_intervals(missing_ites, itermax)
                warn(' '.join(["Markov chain "+str(mc_ind), "file "+filepath+" has missing iterations"
                               " (only", str(len(f_its)), "versus", str(itermax),
                               "in conf)", "missing iterations: " +
                               str([str(s.start) + "-" + str(s.stop) for s in
                                    mii]), "\n\tAll the chain files will be"
                               " truncated accordingly."]))
            cits_ = np.copy(common_its)
            common_its = [i for i in f_its if i in cits_]
        # list files to truncate
        for file in files:
            f_its = its[file]
            f_its = f_its[f_its != 0] # ignored possible it 0
            if len(f_its) > len(common_its):
                files_to_truncate += [file]
        if len(common_its) == 0:
            raise Exception("It can't be no iteration at all")
        if len(files_to_truncate) > 0:
            print("files to truncate", "(chain:", str(mc_ind) + "):", files_to_truncate)
        else:
            continue
        for file in files_to_truncate:
            filepath = join(chain_dir, file)
            with open(filepath) as f:
                lines = f.readlines()
            lines_to_write = []
            for i, line in enumerate(lines):
                if file in ['RAYL-GVELS', 'LOVE-GVELS'] and i == 0:
                    lines_to_write += [line]
                elif int(line.split()[0]) in common_its:
                    lines_to_write += [line]
            with open(filepath, 'w') as f:
                f.writelines(lines_to_write)

def _ites_to_intervals(ites, itermax=None):
    """
    Converts a list of iterations (ites) to slices.

    The contiguous iterations are removed and replaced by a slice.
    """
    ints = [slice(ites[0], None)] # intervals
    if itermax is None:
        itermax = ints[-1]
    for i in range(1, len(ites)):
        if ites[i-1] < ites[i] - 1:
            ints[-1] = \
            slice(ints[-1].start, ites[i-1]) # end of interval
            # start of next interval
            ints += [slice(ites[i])]
    if ints[-1].stop is None:
        ints[-1] = \
        slice(ints[-1].start, itermax)
    return ints


def truncate(opts, conf):
    """
    Truncates MCMC output files to the minimum number of models found according
    to all output files of the chain.

    It could happen that when the model is too complicated mineos failed and
    the proc stuck. Then the amounts of lines in parameter files (VSv, VPv,
    RHO...) do not necessarily correspond with GOODNESS_OF_FIT and/or
    ACCEPTANCE- the choice is to truncate possible extra lines to the minimum
    number of lines in order for all files to agree.

    NOTE: this function is parallelized to the number of cores available
    locally.

    Args:
        opts: the parsed options of this script.
        conf: the parsed configuration of the MCMC (option
        -f|--mcmc_conf_file).

    """
    print(b("=== Truncating output files... to the minimum number of"
            " models found in all markov chains."))
    chain_dirs = [d for d in glob(opts.mcmc_directory+'/*')]
    chain_dirs.sort() # because glob can returns chain dirs in order 0 3 2 1
    processes = []
    nprocs = cpu_count()
    if ('TRUNCATE_NPROCS' in environ and str_isint(environ['TRUNCATE_NPROCS'])
        and int(environ['TRUNCATE_NPROCS']) > 0):
        nprocs = int(environ['TRUNCATE_NPROCS'])
        ok_print("TRUNCATE_NPROCS=", nprocs, '(set from environment)')
    cpp = len(chain_dirs) // nprocs # chain per proc
    r = len(chain_dirs) - cpp * nprocs
    proc_nchains = np.array([cpp for i in range(cpu_count())]).astype('int')
    if r > 0:
        proc_nchains[:r] += 1
    alloc_nchains = 0

    for pi in range(nprocs):
        inds = np.arange(alloc_nchains, alloc_nchains +
                         proc_nchains[pi]).astype('int')
        proc_chain_dirs = chain_dirs[alloc_nchains:alloc_nchains + proc_nchains[pi]]
        alloc_nchains += proc_nchains[pi]
        p = Process(target=truncate_chains, args=(inds, proc_chain_dirs, opts, conf))
        p.start()
        processes.append(p)
    # wait all finished
    for p in processes:
        p.join()

def main(opts: PostMCMCOpts):
    # TODO: 20 and .01 should be constant global variables
    # nrand is 1% of opts.n_models, the minimum is 20 models
    nrand = int(max(20, opts.n_models*.01))
    ok_print(nrand, 'random models')
    conf = MCMCConfig(opts.mcmc_conf_file)
    swcptype = 'herrmann' if conf.scale_type % 2 == 0 else 'mineos'
    ok_print('local scale' if conf.scale_type % 2 ==  0 else 'global scale',
             'st=', conf.scale_type, 'swcptype=', swcptype)
    runtype = opts.mcmc_directory.split('/')[-1]
    if runtype == '': # the directory path ends with /
        runtype = opts.mcmc_directory.split('/')[-2]
    ok_print('runtype:', runtype)
    itermax = conf.cold_n_iters if \
              runtype == 'cold_run' else conf.hot_n_iters
    ok_print(conf.chain_number, 'Markov chains (nproc)')
    ok_print(itermax, 'iterations (itermax)')
    ok_print('zmidmax=', conf.last_bz3_min_depth, 'km')
    ok_print('zmin=', conf.min_depth, 'zmax=', conf.max_depth)
    ok_print('Number of bz curves for each chain:', conf.chain_bz3_numbers)


    lock()
    try_pre_download_mcmc_dir(opts, conf, swcptype)
    check_mcmc_dirs(opts, conf)


    check_vsv_zmax(opts, conf)

    truncate(opts, conf)

    # check again, just in case
    check_mchain_dirs(opts, conf)

    ok_print('check ACCEPTANCE and GOODNESS_OF_FIT')
    eprms = get_explored_parameters(opts, conf)
    ok_print('check eprms=', eprms)
    egvls = get_grp_velocities(opts, conf)
    ok_print('check egvls=', egvls)

    chain_dirs = glob(opts.mcmc_directory+'/*')
    chain_dirs.sort() # because glob can returns chain dirs in order 0 3 2 1

    save_all_best_grp_vels(conf, chain_dirs, runtype)

    add_iteration0(conf, chain_dirs, runtype)
    decimate(conf, chain_dirs, conf.chain_bz3_numbers, runtype, opts, itermax)

    merge_chains(opts, conf, runtype, itermax, nrand)

    # main course is complete
    # remove the lockfile
    release_lock()

def get_explored_parameters(opts, conf):
    """
    Returns a list of files that represents the output models of all parameters explored by the MCMC.

    Args:
        opts: the parsed options of this script.
        conf: the parsed configuration of the MCMC (option
        -f|--mcmc_conf_file).

    Returns: a list of paramter files.

    """
    chain_dirs = [d for d in glob(opts.mcmc_directory+'/*')]
    chain_dirs.sort() # because glob can returns chain dirs in order 0 3 2 1
    files = ['VSv', 'VPv', 'RHO', 'ETA', 'XI', 'K', 'MU']
    # get the parameters on the first markov chain
    chain_dir = chain_dirs[0]
    all_files = glob(join(chain_dir, '*'))
    mfiles = [basename(f) for f in all_files if basename(f) in files]
    # verify that other chains use the parameters too
    for i, chain_dir in enumerate(chain_dirs[1:]):
        for mfile in mfiles:
            if not exists(join(chain_dir, mfile)):
                raise Exception("Parameter inconsistency between markov "
                                "chains: "+mfile+" is explored for the markov "
                                "chain #0 but not for the chain #"+str(i+2)+".")
    return mfiles

def get_grp_velocities(opts, conf, check_consistency=True):
    """
    Returns the group velocities (list of files) used during the MCMC runs.

    It could be only ['RAYL-GVELS'] or ['RAYL-GVELS', 'LOVE-GVELS'] depending
    of the MCMC configuration.

    Args:
        opts: the parsed options of this script.
        conf: the parsed configuration of the MCMC (option
        -f|--mcmc_conf_file).


    Returns: a list of paramter files.
    """
    chain_dirs = [d for d in glob(opts.mcmc_directory+'/*')]
    chain_dirs.sort() # because glob can returns chain dirs in order 0 3 2 1
    files = ['RAYL-GVELS', 'LOVE-GVELS']
    # get the parameters on the first markov chain
    chain_dir = chain_dirs[0]
    all_files = glob(join(chain_dir, '*'))
    mfiles = [basename(f) for f in all_files if basename(f) in files]
    if check_consistency:
        # verify that other chains use the parameters too
        for i, chain_dir in enumerate(chain_dirs[1:]):
            for mfile in mfiles:
                if not exists(join(chain_dir, mfile)):
                    raise Exception("Group velocities inconsistency between markov "
                                    "chains: "+mfile+" is present for the markov "
                                    "chain #0 but not for the chain #"+str(i+2)+".")
    return mfiles

def get_best_grp_vel(gvel_file, best_gof_file):
    """
    Gets the best model/iteration from gvel_file and best_gof_file.

    Args:
        gvel_file: file of group velocities with frequencies in first line
        (RAYL-GVELS or LOVE-GVELS).
        best_gof_file: best model file, one line with the model number in the
        first field and the goodness of fit in second field.

    Returns:
        A numpy array of 2 columns: the first column is T (the periods found in
        gvel_file) and the second column is the corresponding group velocities
        of the best model found in gvel_file according to best_gof_file.
    """
    check_file(best_gof_file)
    # get the best model/iteration
    with open(best_gof_file) as f:
        best_id = int(f.readline().strip().split(' ')[0])
#        print("best_id:", best_id)
    # get the corresponding group velocities
    return get_mod_grp_vel(gvel_file, best_id)

def get_mod_grp_vel(gvel_file, mod_id):
    """
    Gets model/iteration from gvel_file.

    Args:
        gvel_file: file of group velocities with frequencies in first line
        (RAYL-GVELS or LOVE-GVELS).

    Returns:
        A numpy array of 2 columns: the first column is T (the periods found in
        gvel_file) and the second column is the corresponding group velocities
        of the model which iteration is mod_id.
    """
    check_file(gvel_file)
    with open(gvel_file) as f:
        # get frequencies in 1st line of gvel_file
        line = f.readline().strip()
#        print("line:", line)
        freqs = [float(s) for s in line.split(' ') if s != '']
#        print("freqs:", freqs)
    # convert to periods
    T = np.array([1/f for f in freqs])
#    print("T:", T)
    # get model's group velocities
    all_models_gvels = np.loadtxt(gvel_file, skiprows=1)
    U = all_models_gvels[all_models_gvels[:, 0] == mod_id][:, 1:]
#    print("best_model gvels:", U)
    return np.vstack((T, U)).T

def save_all_best_grp_vels(conf, chain_dirs, runtype):
    """
    Gets the best model group velocities for each M. chain and saves it in a
    file named "best-<r|l>_<chain_id>.TU" (r for RAYL and l for LOVE).


    Args:
        conf: the parsed configuration of the MCMC (option
        -f|--mcmc_conf_file).
        chain_dirs: the list of Markov chain directories.
        runtype: 'cold_run' or 'hot_run'.

    """
    for i, chain_dir in enumerate(chain_dirs):
        print("Markov chain:", chain_dir)
        for wavetype in ['RAYL', 'LOVE']:
            gvel_file = join(chain_dir, wavetype+'-GVELS')
            best_gof_file = join(chain_dir,
                                 'BEST_GOODNESS_OF_FIT')
            zi = zeropad(conf.chain_number, i)
            if exists(gvel_file):
                TU = None
                if exists(best_gof_file):
                    TU = get_best_grp_vel(gvel_file, best_gof_file)
                    #print("TU:", TU)
                elif runtype == 'hot_run':
                    # it is possible that BEST_GOODNESS_OF_FIT exists
                    # only for the cold-runs
                    best_gof_file = join(chain_dir,
                                         '..', '..', 'cold_run', zi, 'BEST_GOODNESS_OF_FIT')
                    gvel_file = join(chain_dir, '..', '..', 'cold_run', zi, wavetype+'-GVELS')
                    if exists(gvel_file) and exists(best_gof_file):
                        TU = get_best_grp_vel(gvel_file, best_gof_file)
                        warn("BEST_GOODNESS_OF_FIT doesn't exist, took cold-runs' one"
                             " instead: "+best_gof_file)
                        #print("TU:", TU)
                    else:
                        raise Exception(gvel_file+' or '+best_gof_file+' not found')
                else:
                    raise Exception(best_gof_file+' not found')
                if TU is not None:
                    out_file = 'best-'+wavetype[0].lower()+'_'+zi+".TU"
                    print("Writing best model group velocities in:", out_file)
                    np.savetxt(out_file, TU, fmt='%.6g')

def _insert_it0(file, ins_lines):
    # utility function of add_iteration0
    # insert iteration 0, represented by ins_lines, in file
    f = open(file)
    plines = f.readlines()
    if m := match(r'(\s+)(\d+)(.*)', plines[0]):
        if m.group(2) != '0':
            f.close()
            with open(file, 'w') as f:
                # write best cold model (it 0)
                f.writelines(ins_lines)
                # re-write hot-run iterations
                f.writelines(plines)
    else:
        raise Exception('Format error in '
                        + file)

def _add_it0_gvels(chain_dir, cold_dir, bcrGoF_it):
    # utility function of add_iteration0
    # add iteration 0 in files of group velocities
    for v in ['RAYL-GVELS', 'LOVE-GVELS']:
        hot_vfile = join(chain_dir, v)
        if exists(hot_vfile):
            # backup
            copyfile(hot_vfile, hot_vfile+'.hotrun')
            # read best cold-run gvels
            cold_best_gvels = join(cold_dir, v)
            cold_file = open(cold_best_gvels)
            best_cold_line = cold_file.readlines()[bcrGoF_it]
            cold_file.close()
            m = match(r'(\s+)(\d+)(.*)', best_cold_line)
            if m is None or m.group(2) != str(bcrGoF_it):
                raise Exception('Failed to retrieve the best iteration'
                                ' in ' + cold_best_gof_file)
            best_cold_line = m.group(1)+'0'+m.group(3)+'\n'
            orig_file = open(hot_vfile)
            orig_lines = orig_file.readlines()
            orig_file.close()
            # check if it0 line already added, add it if not
            if not (m := match(r'\s+0\s+.*', orig_lines[1])):
                new_file = open(hot_vfile, 'w')
                # always write first line (freqs)
                new_lines = orig_lines[:1] + [best_cold_line] + orig_lines[1:]
                new_file.writelines(new_lines)
                new_file.close()
            ok_print("Added iteration 0 in "+hot_vfile)

def _add_it0_params_and_best_params(chain_dir, cold_dir, bcr_is_best):
    # utility function of add_iteration0
    # add it0 in parameter files and replace BEST_* files if the best cold-run
    # is better (in term of GoF) than the best hot-run
    # bcr_is_best: best cold-run is the overall best run
    for p in ['VS', 'VP', 'VPv', 'VSv', 'RHO', 'ETA', 'XI', 'K', 'MU']:
        file = join(chain_dir, p)
        bfile = 'BEST_'+p
        hot_bfile = join(chain_dir, bfile)
        backup = hot_bfile+'.hotrun'
        cold_bfile = join(cold_dir, bfile)
        if not exists(cold_bfile):
            continue
            # TODO: this is needed because BEST_VP/BEST_VS not renamed as BEST_VPv/VSv
        if exists(hot_bfile) and not exists(backup):
            # backup best hot-run bfile
            copyfile(hot_bfile, backup)
        # then replace it with cold-run one,
        # changing the it num to 0
        best_lines = []
        with open(cold_bfile) as f:
            lines = f.readlines()
            for line in lines:
                if m := match(r'(\s+)(\d+)(.*)', line):
                    new_line = m.group(1)+ '0' + m.group(3)
                    best_lines.append(new_line+'\n')
                else:
                    raise Exception('Format error in '
                                    + cold_bfile)
        if bcr_is_best: # it is best also if best files don't exist
            # the best cold-run is the overall best run
            # write best_lines as param. hot_bfile replacement
            if m.group(2) != '0':
                with open(hot_bfile, 'w') as f:
                    f.writelines(best_lines)
            ok_print("(best cold-run GoF > best hot-run GoF) Replaced"
                    " "+hot_bfile+" by "+cold_bfile)
            #else: the best cold run has already been taken into
            #account
        # now insert this best cold-run model as iteration 0 in parameter file
        if p in ['VS', 'VP']: # replacing deprecated names
            file = file+'v'
        _insert_it0(file, best_lines)
        ok_print("Inserted best cold-run "+p+" as iteration 0 of"
                 " hot-runs")

def _add_it0_samplefile(conf, chain_dir, proc, cold_dir, bcr_is_best):
    # utility function of add_iteration0
    # handle mineos-*txt or herrmann-*.txt from best cold-run to produce
    # herrmann/mineos-hot_run-*0.txt file, update best hot run .txt and
    # backup in .hotrun before
    if conf.scale_type % 2 == conf.SCALE_LOCAL_HERRMANN:
        sample_prefix = "herrmann"
    else:
        assert(conf.scale_type % 2 == conf.SCALE_GLOBAL_MINEOS)
        sample_prefix = "mineos"
    # copy the cold run best model sample file as iteration 0 sample file
    best_cold_sample_file = cold_best_gof_file = join(cold_dir,
                                                      sample_prefix+'-cold_run-best-'+chain_id2name(conf, proc)+'.txt')
    # the sample file might not exist, might not have been downloaded
    if not exists(best_cold_sample_file):
        raise Exception(best_cold_sample_file+' doesn\'t exist. It might not have been'
                        ' downloaded (no copy to hot_run as iteration 0 is'
                        ' possible). Please copy it from the remote dir'
                        ' if it applies.')
    nzeros = len(str(conf.hot_n_iters)) # for zero padding
    it0_hotrun_sample_file = join(chain_dir,
                                  sample_prefix+'-hot_run-'+('0'*nzeros)+'.txt')
    copyfile(best_cold_sample_file, it0_hotrun_sample_file)
    ok_print("Copied "+best_cold_sample_file+" as "+it0_hotrun_sample_file)
    if bcr_is_best:
        best_hot_sample_file = cold_best_gof_file = join(chain_dir,
                                                          sample_prefix+'-hot_run-best-'+chain_id2name(conf, proc)+'.txt')

        # the best cold-run is also better than the best hot-run
        # backup
        if exists(best_hot_sample_file):
            copyfile(best_hot_sample_file, best_hot_sample_file+'.hotrun')
        # replace the file
        copyfile(best_cold_sample_file, best_hot_sample_file)
        ok_print("(best cold-run GoF > best hot-run GoF) Replaced "+best_hot_sample_file+" by "
                 +best_cold_sample_file)

def add_iteration0(conf, chain_dirs, runtype):
    """
    This function adds an iteration 0 to all hot-runs markov chains. This
    iteration is the best cold-run from which the corresponding hot-run chain
    started.

    Files GOODNESS_OF_FIT, ACCEPTANCE, parameter files (VPv, etc.) are
    edited to add this iteration 0.

    BEST_* files are replaced if the best cold-run GoF is greater than the
    best GoF of hot-runs.
    """
    print(bold(r('='*5 + ' Build hot-run iteration 0 from best cold-run'
           ' iteration '+'='*5)))
    for proc, chain_dir in enumerate(chain_dirs):
        print(b('='*2 + ' Chain '+str(proc)))
        # restore all backup .hotrun files from a possible previous run
        # (we need this to start from a clean situation)
        for f in glob(join(chain_dir, "*.hotrun")):
            copyfile(f, f.replace('.hotrun', ''))
        cold_dir = join(chain_dir,
                             '..', '..', 'cold_run', chain_id2name(conf, proc))
        cold_best_gof_file = join(cold_dir, 'BEST_GOODNESS_OF_FIT')

        hot_best_gof_file = join(chain_dir, 'BEST_GOODNESS_OF_FIT')
        # verify runtype is hotrun, otherwise raise an error
        if runtype == 'hot_run' and exists(cold_best_gof_file):
            # get the best cold-run iteration from BEST_GOODNESS_OF_FIT
            best_cold_gof = np.loadtxt(cold_best_gof_file)
            bcrGoF = best_cold_gof[-1] # best cold-run gof
            bcrGoF_it = int(best_cold_gof[0]) # best cold-run gof
            bhrGoF_exists = exists(hot_best_gof_file)
            if bhrGoF_exists:
                bhrGoF = np.loadtxt(hot_best_gof_file)[-1] # best hot-run gof
            bcr_is_best = not bhrGoF_exists or bcrGoF > bhrGoF
            if bcr_is_best:
                # backup
                if bhrGoF_exists:
                    copyfile(hot_best_gof_file, hot_best_gof_file+'.hotrun')
                # replace hot-run best gof by cold-run one (it becomes iteration 0)
                f = open(hot_best_gof_file, 'w')
                f.writelines('\t'+str(0)+' '+str(bcrGoF)+'\n')
                f.close()
            # insert iteration 0 acceptance line
            _insert_it0(join(chain_dir, 'ACCEPTANCE'), '\t0\t0\t\t0\n')
            ok_print("Added iteration 0 in ACCEPTANCE (chain "+str(proc)+")")
            # insert iteration 0 gof line
            _insert_it0(join(chain_dir, 'GOODNESS_OF_FIT'), '\t'+str(0)+' '+str(bcrGoF)+'\n')
            ok_print("Added iteration 0 in GOODNESS_OF_FIT (chain "+str(proc)+")")
            _add_it0_params_and_best_params(chain_dir, cold_dir, bcr_is_best)
            _add_it0_gvels(chain_dir, cold_dir, bcrGoF_it)
            _add_it0_samplefile(conf, chain_dir, proc, cold_dir, bcr_is_best)
        else:
            raise Exception('This script is made to work for hot-runs with'
            ' previous cold-runs.')


def decimate(conf, chain_dirs, chain_bz3_nums, runtype, opts, itermax):
    """
    Decimates GOODNESS_OF_FIT and parameters (VPv, VSv, etc.) according to
    opts.decimation_factor for each chain directories (chain_dirs).

    Decimation means one model/iteration is kept over a number of
    opts.decimation_factor.

    Output files in each chain directory: GoF.GoF (decimated GoF), VPv.GoF,
    VSv.GoF, etc. (decimated parameters) and phi-rad.GoF (not decimated).

    Args:
        conf: the parsed configuration of the MCMC (option
        -f|--mcmc_conf_file).
        chain_dirs: directories of markov chains results to process.
        chain_bz3_nums: the number of bezier curves for all markov chains.
        runtype: should always be 'hot_run'.
        itermax: the maximum number of iterations on each markov chain.
    """
    # the number of bz points is equal to the number of curves + 1
    chain_bz_npts = np.array(chain_bz3_nums) + 1
    for proc, (chain_dir, nbzc, nbzp) in enumerate(zip(chain_dirs,
                                                  chain_bz3_nums,
                                                  chain_bz_npts)):
        cold_best_gof_file = join(chain_dir,
                             '..', '..', 'cold_run', chain_id2name(conf, proc), 'BEST_GOODNESS_OF_FIT')

        if runtype == 'hot_run' and exists(cold_best_gof_file):
            bcrGoF = np.loadtxt(cold_best_gof_file)[-1]
        else:
            raise Exception('This script is made to work for hot-runs with'
            ' previous cold-runs.')
        gof_file = join(chain_dir, 'GOODNESS_OF_FIT')
        GoF = np.loadtxt(gof_file)
        if GoF[0,1] == - np.inf:
            # the first ite/model has a GoF == -Inf, replace it by bcrGoF
            GoF[0,1] = bcrGoF
        elif GoF[0, 1] == np.nan:
            raise Exception('The case GoF = NaN is not handled yet')
        # remove all NaNs / - Inf GoFs
        GoF = GoF[GoF[:,1] != - np.inf]
        GoF = GoF[GoF[:,1] != np.nan]
        # fill the gaps of inf/nan (rejected) models using the previous accepted model GoF
        lastit = int(GoF[-1, 0])
        i = 0
        while i < lastit:
            if i+1 >= GoF.shape[0] or GoF[i+1, 0] - GoF[i, 0] > 1:
                GoF = np.vstack((GoF[:i+1], [GoF[i, 0] + 1, GoF[i,1]], GoF[i+1:]))
            i += 1
        # decimate
#        print("decimation_factor:", opts.decimation_factor)
#        print("shape GoF:", GoF.shape)
        dGoF = GoF[::opts.decimation_factor]
#        print("shape dGoF:", dGoF.shape)
        # reverse order of columns and add a third one with proc (to differentiate Mc
        # later)
        dGoF = np.hstack((dGoF[:,::-1], np.array([proc for i in
                                              range(dGoF.shape[0])]).reshape(dGoF.shape[0],
                                                                            1)))
        # write in GoF.GoF with zero padding on iteration number
        np.savetxt(join(chain_dir, 'GoF.GoF'), dGoF, fmt=['%.6g', "%0d", "%d"])

        # now decimate on parameter files
        # the decimation is multiplied by the number of bz points - 1 (because
        # the last point at zmax is ignored)
        skipX = opts.decimation_factor * nbzc

        # expand GoF to get the same number of rows as parameter models
        eGoF = np.array([GoF[i] for i in range(GoF.shape[0]) for j in range(nbzp)])
#        print("eGoF:", eGoF)
#        print("GoF, dGoF, eGoF shapes:", GoF.shape, dGoF.shape, eGoF.shape)

        for p in ['VSv', 'VPv', 'RHO', 'ETA', 'XI', 'K', 'MU']:
            file = join(chain_dir, p)
            if exists(file):
                # parameter array (only 3 first cols: it, z and parameter)
                pa = np.loadtxt(file, usecols=np.arange(3), skiprows=0)
#                print("pa shape:", pa.shape)
                # the number of rows of eGoF and pa must be the same
                if pa.shape[0] % nbzp >= 1:
                    raise Exception(file+" number of lines is not a multiple"
                                    " of "+str(nbzp)+" as it must be. Verify"
                                    " file / rsync again.")
                if eGoF.shape[0] != pa.shape[0]:
                    _check_expanded_gof_and_pa_ites(eGoF, pa, gof_file,
                                                    file)

                paeGoF = np.hstack((eGoF, pa))
#                print("paeGoF shape:", paeGoF.shape)
                # remove all zmax point rows
                paeGoF = ([paeGoF[i:i+nbzp-1] for i in
                                   range(0, pa.shape[0], nbzp)])
                paeGoF = np.vstack(paeGoF)
#                print("paeGoF shape:", paeGoF.shape)
                # check that the iteration present in two columns (from pa and
                # eGoF) are consistent
#                print("paeGoF shape:", paeGoF.shape)
#                print(paeGoF)
                #print(paeGoF[:,0], '\n', paeGoF[:,2])
                assert((paeGoF[:,0] == paeGoF[:,2]).all())
                # add the markov chain/proc in a last column
                paeGoF = np.hstack((paeGoF, np.array([proc for i in range(paeGoF.shape[0])]).reshape(paeGoF.shape[0], 1)))
#                print("paeGoF:", '\n', paeGoF)
                # change the order of columns and remove duplicated it col
                paeGoF_out = np.zeros((paeGoF.shape[0], 5))
                paeGoF_out[:,0] = paeGoF[:,1] # GoF
                paeGoF_out[:,1] = paeGoF[:,3] # z
                paeGoF_out[:,2] = paeGoF[:,4] # param
                paeGoF_out[:,3] = paeGoF[:,0] # it
                paeGoF_out[:,4] = paeGoF[:,5] # proc
                # decimate
                dpaeGoF_out = np.vstack(tuple(paeGoF_out[i:nbzc+i] for i in range(0,
                                                                             paeGoF.shape[0],
                                                                             skipX)))
                np.savetxt(join(chain_dir, p+'.GoF'), dpaeGoF_out, fmt=["%.6g",
                "%.6g", "%.6g", "%d", "%d"], header="GoF, z, param, it, proc")
        # get radius-phi with corresponding GoF
        rows = [line.split() for line in
                         open(chain_dir+sep+'VPv').readlines()]
        rows = [row for row in rows if len(row) > 3]
        phi_radius = np.array([row for row in rows if len(row) >
                                        3])[:,-2:].astype('double')
        # convert phi from radians to degrees
        phi_radius[:, 0] = phi_radius[:, 0] * 180/np.pi

        # add corresponding GoF and proc
        phi_rad_it_gof = np.hstack((phi_radius, GoF))
        phi_rad_it_gof_proc = np.hstack((phi_rad_it_gof, np.array([proc for i in
                                                  range(phi_rad_it_gof.shape[0])]).reshape(phi_rad_it_gof.shape[0],
                                                                                 1)))
        # swap it and gof columns
        phi_rad_gof_it_proc = phi_rad_it_gof_proc.copy()
        phi_rad_gof_it_proc[:,-3] = phi_rad_it_gof_proc[:,-2]
        phi_rad_gof_it_proc[:,-2] = phi_rad_it_gof_proc[:,-3]
        np.savetxt(join(chain_dir, 'phi-rad.GoF'), phi_rad_gof_it_proc, fmt=['%.6g',
        '%.6g', '%.6g', '%d', '%d'])

def _check_expanded_gof_and_pa_ites(eGoF, pa, gof_file, pa_file):
    """
    Sanity function.
    See decimate.

    Args:
        eGoF: extended/expanded GoF array (duplicate iterations to match number
        of lines per model of parameter in pa/pa_file).
        pa : parameter model array (VPv, etc.)
        gof_file: file of original GoF used to produce eGoF.
        pa_file: file of pa.

    """
    if eGoF.shape[0] == pa.shape[0]:
        return
    eGoF_ites = np.unique(eGoF[:, 0]).astype('int')
    pa_ites = np.unique(pa[:, 0]).astype('int')
    last_ite = max(eGoF_ites[-1], pa_ites[-1])
    if eGoF.shape[0] > pa.shape[0]:
        missing_ites = [i for i in np.arange(last_ite + 1)
                        if i not in pa_ites]
        mfile = pa_file
    else: # eGoF.shape[0] < pa.shape[0]:
        missing_ites = [i for i in np.arange(last_ite + 1)
                        if i not in eGoF_ites]
        mfile = gof_file
    raise Exception("The iteration(s) "+str(missing_ites)+" is/are"
                    " missing in file: "+mfile+". Please verify "
                    "if the original file has also this error. If"
                    " not then rsync the whole McMC directory"
                    " and retry "+argv[0]+" otherwise please "
                    "report a bug.")

def merge_validate_sort_gofs(opts):
    """
    Proceeds to a merge of all GoFs (from all chains) using GoF.GoF files.

    The GoFs are sorted, validated according to the theoretical maximum option (those
    who are greater are ignored and recorded into /tmp/models_to_rm).
    Only n_csv_models (see options) are registered in the output file sGoF.csv.

    Returns: all GoFs (and associated iter, proc) sorted ascendingly and lower or equal to theoretical max.
    """
    # gather all GoF.GoF files
    gof_files = glob(opts.mcmc_directory+'/*/GoF.GoF')
    all_gofs = np.loadtxt(gof_files[0])
    for f in gof_files[1:]:
        all_gofs = np.vstack((all_gofs, np.loadtxt(f)))
    # sort according to GoF (first column)
    I = np.argsort(all_gofs[:, 0])
    all_gofs = all_gofs[I]
    # print("sorted GoFs:", all_gofs)
    # save models to be removed later on parameter files
    tm = opts.theoretical_max
    if tm is None:
        tm = np.inf
    models_to_rm = all_gofs[all_gofs[:,0] > tm]
    if models_to_rm.size != 0:
        warn('Inconsistent models (GoF > theoretical max.: '+str(tm)+' -- see'
             ' /tmp/models_to_rm.csv)')
        np.savetxt('/tmp/models_to_rm.csv', models_to_rm, delimiter=',', fmt='%.6g',
                                 header='gof, iter, proc')
    # remove inconsistent models (GoF > theoretical max)
    sgofs = all_gofs[all_gofs[:,0] <= tm]
    # keep ncsv models to save in sGoF.csv (separator is ,)
    ncsv = opts.n_csv_models if opts.n_csv_models is not None else opts.n_models
    ncsv = min(ncsv, all_gofs.shape[0])
    np.savetxt('sGoF.csv', sgofs[-ncsv:], delimiter=',', fmt='%.6g',
                                 header='gof, iter, proc')
    ok_print("Saved sorted "+str(ncsv)+" consistent models in sGoF.csv")
    return all_gofs

def selec_download_best_models(opts, conf, runtype, itermax, valid_gofs):
    """
    Selects the best models (in terms of GoF) and downloads the associated mineos/herrmann-*.txt.

    The number of best models selected is defined by the option --n_models.
    The download of model files is made by rsync according to the address
    specified in option --rsync_src (note: defaultly the source is local).
    All model files are downloaded in `best-pdf' directory.

    Args:
        opts: the parsed options of this script.
        conf: the parsed configuration of the MCMC (option
        -f|--mcmc_conf_file).
        runtype: 'hot_run' or 'cold_run' (the latter shouldn't happen because
        the script works normally on hot-runs).
        itermax: the maximum number of iterations of Markov Chains (defined in
        the configuration conf).
        valid_gofs: the set of valid models/GoFs formed by
        merge_validate_sort_gofs.
    """
    # select best models
    nbest = min(opts.n_models, len(valid_gofs))
    if nbest == len(valid_gofs):
        warn('The number of models available ('+str(len(valid_gofs))+') is lower than n_models'
             ' option (' +str(opts.n_models)+')')
    nbest_gofs = valid_gofs[-nbest::][::-1] # descendingly
    download_models(opts, conf, runtype, itermax, nbest_gofs, 'best',
    'best-pdf')

def selec_download_rand_models(opts, conf, runtype, itermax, valid_gofs, nrand):
    """
    Selects random models (in terms of GoF) and downloads the associated mineos/herrmann-*.txt.

    The download of model files is made by rsync according to the address
    specified in option --rsync_src (note: defaultly the source is local).
    All model files are downloaded in `rand-pdf' directory.

    Args:
        opts: the parsed options of this script.
        conf: the parsed configuration of the MCMC (option
        -f|--mcmc_conf_file).
        runtype: 'hot_run' or 'cold_run' (the latter shouldn't happen because
        the script works normally on hot-runs).
        itermax: the maximum number of iterations of Markov Chains (defined in
        the configuration conf).
        valid_gofs: the set of valid models/GoFs normally formed by
        merge_validate_sort_gofs and from which to pick random models.
        nrand: the number of random models to return.

    Returns:
        The nrand random models from valid_gofs.

    Output file:
        rGoF.csv in format "gof, iter, proc".
    """
    nrand = min(nrand, len(valid_gofs))
    if nrand == len(valid_gofs):
        warn('The number of models available ('+str(len(valid_gofs))+') is'
             ' lower than nrand'
             ' (' +str(nrand)+' = min(20, n_models * .01))')
    rand_gofs = valid_gofs[np.random.permutation(len(valid_gofs))][:nrand]
    np.savetxt('rGoF.csv', rand_gofs, delimiter=',', fmt='%.6g',
                                 header='gof, iter, proc')
    ok_print('Saved random models in rGoF.csv')
    download_models(opts, conf, runtype, itermax, rand_gofs, 'random',
    'rand-pdf')
    return rand_gofs

def download_models(opts, conf, runtype, itermax, selected_gofs, name,
                    targetdir, zresampling=True, gen_K_MU=True):
    """
    Downloads a list of selected models using rsync or simply copy them locally if the MCMC data is not remote.

    Args:
        opts: the parsed options of this script.
        conf: the parsed configuration of the MCMC (option
        -f|--mcmc_conf_file).
        runtype: 'cold_run' or 'hot_run'.
        itermax: the maximum number of iterations of the MCMC (it should be the
        same in conf).
        selected_gofs: the selected models (refer to merge_validate_sort_gofs
        to see how it's formatted -- selected_gofs is a subset of all the valid models).
        name: just for message output.
        targetdir: where to download the files.
        zresampling: to resample the models downloaded for a regular depth of
        layers (see zresample_mdl()).
        gen_K_MU: if K and MU exist in the mcmc directory (that is
        conf.scale_type should be >= 2), then if this argument is True, K and
        MU models will be generated from VP, VS and RHO, according to their
        relationships.

    """
    # list associated full model files
    nmods = selected_gofs.shape[0]
    smodels = []
    out_smodels = []
    swcptype = 'herrmann' if conf.scale_type % 2 == 0 else 'mineos'
    # record files to download for rsync
    to_dl = '/tmp/nk.ls'
    dl_files = open(to_dl, 'w')
    for i in range(selected_gofs.shape[0]):
        it = int(selected_gofs[i, 1])
        proc = int(selected_gofs[i, 2]) # chain
        nzeros = len(str(itermax)) - len(str(it))
        smodels += [join(opts.mcmc_directory, chain_id2name(conf, proc),
                               swcptype+'-'+runtype+'-'+('0'*nzeros)+str(it)+'.txt')]
        out_smodels += \
                [str(i)+'_neemuds-out_'+chain_id2name(conf, proc)+'-'+str(it)+'.txt']
        if it == 0:
            # 0-it model already downloaded (best cold-run converted to hot-run it0)
            # see try_pre_download_mcmc_dir (nested function scp_best_mods)
            # just copy it in targetdir, keeping relative path as rsync does
            copy_file_with_rpath(smodels[-1], targetdir)

        else:
            # the model will be downloaded
            dl_files.write(smodels[-1]+'\n')
    dl_files.close()
    # download selected models
    rsync_cmd = 'rsync -a --copy-links --relative --files-from='+to_dl+ \
            ' '+opts.rsync_src+' '+targetdir
    loop_on_rsync(rsync_cmd)
    # copy all files according to out_smodels
    for f, cf in zip(smodels, out_smodels):
        out_file = join(targetdir, cf)
        copyfile(join(targetdir, f), out_file)
        if zresampling:
            zresample_mdl(opts, conf, out_file)
    ok_print("Copied "+str(nmods)+" "+name+" full models in files "+
             targetdir + "/<i>_neemuds_out-<proc>-<iter>.txt")
    if zresampling:
        ok_print("Generated "+str(nmods)+" "+name+" full regularized parameter models in files "+
                 targetdir + "/<i>_neemuds_out-<proc>-<iter>.txt.z<parameter>")
    if zresampling and conf.scale_type >= 2:
        gen_K_MU_models(opts, conf, targetdir)

def loop_on_rsync(rsync_cmd, print_cmd=True):
    """
    Tries to execute the rsync command defined by rsync_cmd a maximum number of
    MAX_RSYNC_TRIALS times in case of failure.

    Args:
        rsync_cmd: it should be a valid rsync command.
        print_cmd: rsync_cmd is echoed iff True.
    """
    sysret = 1
    trials = 1
    if print_cmd:
        print(rsync_cmd)
    while trials < MAX_RSYNC_TRIALS and sysret != 0:
        sysret = system(rsync_cmd)
        trials += 1
        if sysret != 0:
            warn("rsync cmd failed, retrying for the "+str(trials+1)+"-th"
                 " time")
    if sysret != 0:
        raise Exception('rsync command failed after ' +
                        str(MAX_RSYNC_TRIALS) +' trials.')
    ok_print('Rsync command finished successfully')
    return sysret

def try_pre_download_mcmc_dir(opts, conf, swctype, dl_chain_by_chain=True):
    """
    If the -r|--rsync_src option is used, then try to download automatically
    the MCMC directory (or synchronize the files if they pre-existed).
    The minimal set of files is downloaded to pursue the post-mcmc operations.
    It excludes all full sampled accepted models except best cold runs that
    might be used.

    Args:
        opts: the parsed options of this script.
        conf: the parsed configuration of the MCMC (option
        -f|--mcmc_conf_file).
        dl_chain_by_chain: if True (default) the function downloads the remote
        directories/files chain by chain (it is particularly useful when the
        network connectivity is bad). If False the files are downloaded all
        chains together.
    """
    from os.path import sep, join, isdir, exists, dirname, basename
    if '@' in opts.rsync_src: # TODO: we should be more precise to match a ssh addr
        targetdir = opts.mcmc_directory
        targetdir = targetdir.replace(sep + 'hot_run', '')
        targetdir = targetdir.replace(sep + 'cold_run', '')
        if exists(targetdir) and isdir(targetdir):
            resp = None
            while resp not in ["yes", "no", "y", "n"]:
                print(bold(targetdir+" already exists locally, do you"
                           " want to synchronize with remote counterpart"
                           " directory (otherwise local directory is kept"
                           " untouched)? [y/n]"))
                resp = input()
            if resp.startswith('n'):
                return

        # full sampled models are ignored (only used ones will be downloaded later)
        rsync_cmd = 'rsync -v -a --copy-links --exclude=mineos*txt' + \
                ' --exclude=herrmann*txt '
        rsync_msg = "rsync cmd to pre-download MCMC directory: "
        if dl_chain_by_chain:
            expected_chain_dirs = zeropad(conf.chain_number, list(range(0,
                                                                        conf.chain_number)))
            if not exists(targetdir):
                mkdir(targetdir)
            for run_dir in ['hot_run', 'cold_run']:
                if not exists(targetdir):
                    mkdir(join(targetdir, run_dir))
                for cd in expected_chain_dirs:
                    rsync_cmd_cd = rsync_cmd +  \
                            join(opts.rsync_src, targetdir, run_dir, cd) + ' ' + join(targetdir, run_dir)
                    ok_print(rsync_msg + rsync_cmd_cd)
                    loop_on_rsync(rsync_cmd_cd, print_cmd=False)
        else:
            rsync_cmd += join(opts.rsync_src, targetdir)+' '+dirname(targetdir)
            ok_print(rsync_msg + rsync_cmd)
            loop_on_rsync(rsync_cmd_cd, print_cmd=False)
        ok_print("Pre-downlading ok in "+targetdir)
        chain_dirs = glob(join(targetdir, 'cold_run','*'))
        def scp_best_mods(*chain_dirs):
            ok_print("Downloading "+swctype+"-cold_run-best-*.txt for chains:", str([basename(cd) for
                                                              cd in chain_dirs]))
            for cd in chain_dirs:
                bmod = swctype+'-cold_run-best-'+ basename(cd)+'.txt'
                last_scp_failed = False
                while not exists(join(cd, bmod)) or last_scp_failed:
                    scp_cmd = 'scp -rp '+join(opts.rsync_src, cd,
                                             bmod)+' '+cd
                    sysret = system(scp_cmd)
                    if sysret != 0:
                        print("scp command failed. Trying again...", file=stderr)
                        last_scp_failed = True
                    else:
                        last_scp_failed = False
        from multiprocessing import cpu_count
        nmods_per_proc = len(chain_dirs) // cpu_count()
        if nmods_per_proc * cpu_count() < len(chain_dirs):
            nmods_per_proc += 1
        processes = []
        for pi in range(cpu_count()):
            start = pi * nmods_per_proc
            stop = min((pi+1) * nmods_per_proc, len(chain_dirs))
            p = Process(target=scp_best_mods, args=(chain_dirs[start:stop]))
            p.start()
            processes.append(p)
        # wait all finished
        for p in processes:
            p.join()

    if not exists(opts.mcmc_directory or not
            isdir(opts.mcmc_directory)):
        raise Exception('The filepath ' +
                        opts.mcmc_directory+' doesn\'t '
                        ' exist or is not a directory.')



def gen_K_MU_models(opts, conf, targetdir):
    """

    Args:
        opts: the parsed options of this script.
        conf: the parsed configuration of the MCMC (option
        -f|--mcmc_conf_file).
        targetdir: where to find *.zRHO, *.zVPv and *.zVSv models.
    """
    VPv_mods = glob(join(targetdir, '*.zVPv'))
    VSv_mods = []
    RHO_mods = []
    for VPv_mod in VPv_mods:
        RHO_mods += [VPv_mod.replace('zVPv', 'zRHO')]
        VSv_mods += [VPv_mod.replace('zVPv', 'zVSv')]
    def gen_K_MU_mod(VPv_fp, VSv_fp, RHO_fp):
        """
        Create only one pair of models (K, MU) from one triplet of models (VPv,
        VSv, RHO).
        """
        # load the VPv, VSv and RHO models
        VPv = np.loadtxt(VPv_fp)
        VSv = np.loadtxt(VSv_fp)
        RHO = np.loadtxt(RHO_fp)
        MU = np.empty(VPv.shape, dtype=VPv.dtype)
        K = np.empty(VPv.shape, dtype=VPv.dtype)
        # compute K and MU models
        MU[:,0] = VPv[:,0]
        MU[:, 1] = VSv[:,1]**2 * RHO[:,1]
        K[:,0] = VPv[:,0]
        K[:,1] = (VPv[:,1]**2 - 4/3 * VSv[:,1]**2) * RHO[:,1]
        # write the K and MU models in the same dir
        K_fp = VPv_fp.replace('zVPv', 'zK')
        MU_fp = VPv_fp.replace('zVPv', 'zMU')
        np.savetxt(K_fp, K, header="# z (m), K (Pa)")
        np.savetxt(MU_fp, MU, header="# z (m), MU (Pa)")
    def gen_K_MU_mods(VPv_fps, VSv_fps, RHO_fps):
        """
        Do a gen_K_MU_mod for a group of VPv, VSv, RHO models.
        """
        for VPv_fp, VSv_fp, RHO_fp in zip(VPv_fps, VSv_fps, RHO_fps):
            gen_K_MU_mod(VPv_fp, VSv_fp, RHO_fp)
    nmods_per_proc = len(VPv_mods) // cpu_count()
    if nmods_per_proc * cpu_count() < len(VPv_mods):
        nmods_per_proc += 1
    processes = []
    for pi in range(cpu_count()):
        start = pi * nmods_per_proc
        stop = min((pi+1) * nmods_per_proc, len(VPv_mods))
        p = Process(target=gen_K_MU_mods, args=(VPv_mods[start:stop],
                                                VSv_mods[start:stop],
                                                RHO_mods[start:stop]))
        p.start()
        processes.append(p)
    # wait all finished
    for p in processes:
        p.join()

def save_best_models_gvels(opts, conf, itermax, nrand, valid_gofs):
    """
    Saves the group velocities of the best (and very best) models.

    The number of best models saved is defined by the n_models option (but it
    could be that the available number of models is smaller than the option
    value. In that case all the models are saved).
    The number of very best models saved is nrand (1% of n_models option wrt to
    the minimum of 20 models -- see main).

    Args:
        opts: the parsed options of this script.
        conf: the parsed configuration of the MCMC (option
        -f|--mcmc_conf_file).
        itermax: the maximum number of iterations of Markov Chains (defined in
        nrand: the number of very best models to save the group velocities.
        valid_gofs: array of all valid models from which the select the best ones.

    Output files:
        best-pdf/<RAYL|LOVE>-GVELS/<proc>_<iteration>.txt
        best-pdf/<RAYL|LOVE>-GVELS/very_best/<proc>_<iteration>.txt
    """
    egvls = get_grp_velocities(opts, conf, check_consistency=False)

    # save nrand best group velocities
    print(bold(r('='*5 + ' Save group velocities of the '+str(nrand)+' best models'
           ' '+'='*5)))
    nrand_best_gofs = valid_gofs[-nrand:]
    save_gof_gvels(conf, egvls, nrand_best_gofs, 'best-pdf', itermax, 'very_best', verbose=True, tag='best')

    # save n_models best group velocities
    n = opts.n_models
    print(bold(r('='*5 + ' Save group velocities of '+str(n)+' best models'
           ' '+'='*5)))
    n_best_gofs = valid_gofs[-n:]
    save_gof_gvels(conf, egvls, n_best_gofs, 'best-pdf', itermax, verbose=False,
                    show_progress=True, tag='best')

    #TODO: verify best-pdf/very_best/RAYL-GVELS/* and best-pdf/RAYL-GVELS/*
    # this must be the best models (see it with sGoF.csv)

def save_rand_models_gvels(opts, conf, itermax, nrand, rand_gofs):
    """
    Saves the group velocities of nrand random models.

    Args:
        opts: the parsed options of this script.
        conf: the parsed configuration of the MCMC (option
        -f|--mcmc_conf_file).
        itermax: the maximum number of iterations of Markov Chains (defined in
        nrand: the number of random models to save.
        rand_gofs: array of random and valid models from which to save the
        first nrand ones.

    Output files:
        rand-pdf/<RAYL|LOVE>-GVELS/<proc>_<iteration>.txt
    """
    egvls = get_grp_velocities(opts, conf, check_consistency=False)
    # save nrand group velocities
    print(bold(r('='*5 + ' Save group velocities of '+str(nrand)+' rand models'
           ' '+'='*5)))
    nrand_rand_gofs = rand_gofs[-nrand:]
    save_gof_gvels(conf, egvls, nrand_rand_gofs, 'rand-pdf', itermax, verbose=True, tag='rand')

def save_gof_gvels(conf, egvls, gofs, targetdir, itermax, subdir='', show_progress=False,
                   verbose=False, tag=''):
    """
    Saves the group velocities of the models defined in gofs.

    Args:
        egvls: (list) the group velocities to save (valid items: 'RAYL-GVELS'
        or 'LOVE-GVELS'). Cf. get_grp_velocities.
        gofs: the models (including their GoFs) to save the group velocities.
        targetdir: the directory where files are saved (created if not already
        existing).
        itermax: the maximum number of iterations on each markov chain.
        subdir: the subdirectory of targetdir to save the files (created if not
        existing).
        show_progress: True to show the progress of file saving, False
        otherwise.
        verbose: True for verbose mode, False otherwise.
        tag: a name to designate the type of models to save on output messages
        of verbose mode.
    """
    for i, (it, proc) in enumerate(zip(gofs[:,1], gofs[:, 2])):
        it = int(it)
        proc = int(proc)
        for egvl in egvls:
            gvel_file = join(opts.mcmc_directory, chain_id2name(conf, proc), str(egvl))
            TU = get_mod_grp_vel(gvel_file, it)
            # create output directory
            out_dir = join(targetdir, egvl)
            if not exists(out_dir):
                mkdir(out_dir)
            if subdir not in [None, '']:
                out_dir = join(out_dir, subdir)
                if not exists(out_dir):
                    mkdir(out_dir)
            nzeros = len(str(itermax)) - len(str(it)) # zero padding
            out_file = join(out_dir, chain_id2name(conf, proc) + "_" +  nzeros*'0' + str(it)+".txt" )
            np.savetxt(out_file, TU, fmt='%.6g')
            if verbose:
                ok_print("Saved "+tag+" model in:", out_file)
            if show_progress:
                print('\r', int(i*100/gofs.shape[0]), '%', end='')
    if show_progress:
        print("\r100 %\n")
    ok_print("Saved all files: ", join(out_dir, "<proc>_" +  "<it>.txt" ))

def save_eprm_csv(opts, conf):
    """
    Saves one CSV by effective parameter (VPv, VSv, RHO and potentially ETA, XI).

    The *.GoF files generated after decimation of each chain are the input of the
    function (see decimate()).

    The rows are sorted increasingly:
        - first according to their GoF,
        - then their iteration (for a same GoF),
        - finally the depth (for a same model).

    Args:
        opts: the parsed options of this script.
        conf: the parsed configuration of the MCMC (option
        -f|--mcmc_conf_file).

    Output files: Bzpt_<parameter>.csv with parameter one among VPv, VSv, RHO,
    ETA and XI.
    """
    eprms = get_explored_parameters(opts, conf)
    tm = opts.theoretical_max
    if tm is None:
        tm = np.inf
    n = -1 # initialized after first iteration of next loop
    for eprm in eprms:
        eprm_files = glob(opts.mcmc_directory+'/*/'+eprm+'.GoF')
        eprm_mods = np.loadtxt(eprm_files[0])
        # merge all models for eprm
        for f in eprm_files[1:]:
            a = np.loadtxt(f) # GoF, z, param, it, proc
            eprm_mods = np.vstack((eprm_mods, a))
        # mods_to_rm = np.loadtxt('/tmp/models_to_rm.csv')
        # no need to use the file, directly filtering models here again
        eprm_mods = eprm_mods[eprm_mods[:, 0] <= tm]
        # sort according to GoF
        I = np.argsort(eprm_mods[:, 0])
        eprm_mods = eprm_mods[I]
        # sort rows of same GoF according to their iteration
        i = 0
        while i < len(eprm_mods)-1:
            j = i +1
            while j < len(eprm_mods) and eprm_mods[i, 0] == eprm_mods[j, 0]:
                j += 1
            # s is a slice of same GoF
            s = eprm_mods[i:j, :]
            I = np.argsort(s[:, 3])
            s = s[I]
            # sort same iteration rows of s according to depth z
            k = 0
            while k < len(s) - 1:
                l = k + 1
                while l < len(s) and s[k, 3] == s[l, 3]:
                    l += 1
                s2 = s[k:l, :]
                J = np.argsort(s2[:, 1])
                s2 = s2[J]
                s[k:l, :] = s2
                k = l
            eprm_mods[i:j, :] = s
            i = j
        if n != -1 and eprm_mods.shape[0] != n:
            raise Exception('Number of lines in parameter files ' +
                            str(eprms) +
                            ' are not the same')
        n = len(eprm_mods)
        if eprm.startswith('V'):  # VPv, VSv
            # convert in km/s
            eprm_mods[:, 2] /= 1000
        # rho is already in kg/m^3
        out_file = 'Bzpt_'+eprm+'.csv'
        np.savetxt(out_file, eprm_mods, fmt="%.6g", delimiter=',',
                   header='gof, z, '+eprm.lower()+', iter, proc')
        ok_print('Bézier points for '+eprm+' written in '+out_file)


def merge_chains(opts, conf, runtype, itermax, nrand):
    """
    Merges and cleans up all chains results.
    """
    print(bold(r('='*5 + ' Merge and clean up all chains results' + '='*5)))

    valid_gofs = merge_validate_sort_gofs(opts)
    selec_download_best_models(opts, conf, runtype, itermax, valid_gofs)

    save_best_models_gvels(opts, conf, itermax, nrand, valid_gofs)

    rand_gofs = selec_download_rand_models(opts,
                                           conf,
                                           runtype, itermax, valid_gofs, nrand)
    save_rand_models_gvels(opts, conf, itermax, nrand, rand_gofs)
    save_eprm_csv(opts, conf)


def lin_interpolate(mdl, zmin, zmax, dz):
    """
    Regularizes the model in depth (mdl[:,0]) by linearly interpolating the
    parameter (mdl[:, 1])

    Args:
        mdl: the array of the model.
        zmin, zmax: the min and max depth of interest
                    (rows outside of this range
                    are ignored).
        dz: the layer depth used to regularize the model.

    Returns: the evenly spaced model according to dz.
    """
    mdl = mdl[mdl[:, 0] >= zmin]
    mdl = mdl[mdl[:, 0] <= zmax]
    if mdl[0, 0] > zmin:
        # assuming zmin is not necessarily 0
        a = (mdl[1, 1] - mdl[0, 1]) / (mdl[1, 0] - mdl[0, 0])
        b = mdl[0, 1] - a * mdl[0, 0]
        mdl = np.vstack(([zmin, a * zmin + b], mdl))
    # mdl[z1i, 0] == zmin
    z1i = 0
    z2i = 1
    out_mdl = np.array([[zmin, mdl[0, 1]]])
    z = zmin
    while out_mdl[-1, 0] < zmax and z < zmax:
        z = out_mdl[-1, 0] + dz
        while z2i < mdl.shape[0] - 1 and mdl[z2i, 0] < z:
            z1i += 1
            z2i += 1
        a = (mdl[z2i, 1] - mdl[z1i, 1]) / (mdl[z2i, 0] - mdl[z1i, 0])
        b = mdl[z1i, 1] - a * mdl[z1i, 0]
        y = a * z + b
        out_mdl = np.vstack((out_mdl, [z, y]))
    return out_mdl


def zresample_mdl(opts, conf, mdl_file, verbose=False):
    """
    Resamples the mdl_file model evenly in z dimension using lin_interpolate.

    Args:

        opts: the parsed options of this script.
        conf: the parsed configuration of the MCMC (option
        -f|--mcmc_conf_file).
        mdl_file: model filepath.

    """
    if conf.scale_type % 2 == 0:
        # local scale
        mdl = np.loadtxt(mdl_file)
        VPv_mdl = mdl[:, [0, 1]]
        VSv_mdl = mdl[:, [0, 2]]
        RHO_mdl = mdl[:, [0, 3]]
        mdls = [('VPv', VPv_mdl, 'm/s'), ('VSv', VSv_mdl, 'm/s'), ('RHO',
                                                                   RHO_mdl,
                                                                   'kg/m³')]
        if mdl.shape[1] >= 6:
            XI_mdl = np.hstack((mdl[:, 0].reshape(-1, 1),
                                (mdl[:, 5]**2 /
                                 mdl[:, 2]**2).reshape(-1, 1)))
            mdls += [('XI', XI_mdl, 'no unit')]
        for mdl_ in mdls:
            # convert the depth in meters
            mdl_[1][:, 0] *= 1000
    else:
        # global scale
        mdl = np.loadtxt(mdl_file, skiprows=3)
        # get the planet radius
        r = mdl[-1, 0]
        if verbose:
            ok_print("Planet radius:", r)
        z = r - mdl[:, 0]
        z = z.reshape((z.size, 1))
        # reshape is necessary for concatenating two
        # cols (hstack of two vectors is not the
        # same)
        # RHO is already in kg/m^3
        RHO_mdl = np.hstack((z, mdl[:, 1].reshape((z.size, 1))))
        VPv_mdl = np.hstack((z, mdl[:, 2].reshape((z.size, 1))))
        VSv_mdl = np.hstack((z, mdl[:, 3].reshape((z.size, 1))))
        VPh_mdl = np.hstack((z, mdl[:, 6].reshape((z.size, 1))))
        VSh_mdl = np.hstack((z, mdl[:, 7].reshape((z.size, 1))))
        ETA_mdl = np.hstack((z, mdl[:, 8].reshape((z.size, 1))))
        XI_mdl = np.hstack((z, (mdl[:, 7]**2 / mdl[:, 3]**2).reshape((z.size,
                                                                      1))))
        mdls = [('VPv', VPv_mdl, 'm/s'), ('VSv', VSv_mdl, 'm/s'), ('RHO',
                                                                   RHO_mdl,
                                                                   'kg/m³'),
                ('XI', XI_mdl, 'no unit'), ('VPh', VPh_mdl, 'm/s'),
                ('VSh', VSh_mdl, 'm/s'), ('ETA', ETA_mdl, 'no unit')]
        for i, (name, mdl, unit) in enumerate(mdls):
            mdl = mdl[::-1]  # sort in increasing depth
            mdls[i] = (name, mdl, unit)
    # need to conv (km in conf and m in model file for depth)
    conv_depth = 1000
    for name, mdl, unit in mdls:
        rmdl = lin_interpolate(mdl, conf.min_depth * conv_depth,
                               conf.max_depth * conv_depth,
                               conf.layer_thickness * conv_depth)
        np.savetxt(
            mdl_file+'.z'+name, rmdl, fmt='%.6g', header="z (m), "+name+' '
            '('+unit+')')


if __name__ == '__main__':
    # TODO: verbose option (to enable verbose function opt. args), with maybe a
    # level of verbosity
    if len(argv) == 1 or '-h' in argv or '--help' in argv:
        usage()
        exit(0)
    opts = PostMCMCOpts()
    opts_str, remaining = getopt(argv[1:], PostMCMCOpts.short_opts,
                                 PostMCMCOpts.long_opts)
    parse_opts(opts_str, opts)
    opts.print()
    opts.check_all_opts()
    main(opts)
