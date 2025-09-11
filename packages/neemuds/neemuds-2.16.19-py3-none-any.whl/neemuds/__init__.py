
import os
from os.path import join, exists, dirname, basename, expanduser
from glob import glob
import sys
import traceback
import shutil

from py3toolset.txt_color import print_frame, g, bold, col, Color

import ctypes  # for loading of wrapper libs

if 'NEEMUDS_LOAD_LIBS' in os.environ:
    loading_libs = os.environ['NEEMUDS_LOAD_LIBS'] == '1'
else:
    loading_libs = True

installed_from_pip = False


if __file__.count("site-packages") > 0 or __file__.count("dist-packages") > 0:
    # neemuds has been installed through pip, no need to preload wrapper
    # libraries
    loading_libs = False
    installed_from_pip = True

# initialize NEEMUDS data dir if necessary
ndata_dir_ne = join('~', '.ndata') # not expanded
ndata_dir = expanduser(ndata_dir_ne)  # expanduser works on Windows too (even if ~ is used)
pkg_data_dir = join(dirname(__file__), 'data')
if not exists(ndata_dir):
    try:
        # see comment below about MPI
        os.mkdir(ndata_dir)
    except:
        pass
for f in glob(join(pkg_data_dir, '*')):
    dst = join(ndata_dir, basename(f))
    if not exists(dst):
            print(g(bold('[OK]')), "Copying", f, "to NEEMUDS data directory ",
                  ndata_dir)
            # we are maybe in a multiprocess concurrent (MPI) context so
            # the try-catch ensures a failsafe mechanism in case of a file/dir
            # is created in the meantime by another process
            try:
                # the copy is made rather than symlink because on Windows it
                # might fail (not an issue because data is not so heavy up to now)
                shutil.copytree(f, dst)
            except:
                # a parent dir might already exist but not all subdirs/files
                try:
                    shutil.copy(f, dst)
                except:
                    pass

def load_lib(lib_info):
    lib_path = join(PROG_PDIR, lib_info['ppath'][0], lib_info['filename'])
    e = Exception(lib_info['name']+" wasn't found. Please run a make"
                  " -C "+lib_info['ppath'][0]+" in order to build it.")
    if(not exists(lib_path)):
        raise e
    # load the lib
    print("Loading",lib_info['filename'].split('.')[0]+"...")
    ctypes.CDLL(lib_path, ctypes.RTLD_GLOBAL)
    # now try to import the module/package (pywrapper) after adding it to
    # sys.path
    for ppath in lib_info['ppath']:
        sys.path.append(join(PROG_PDIR, ppath))
    if(not check_mod_pkg(lib_info['filename'].split('.')[0])):
        raise e

def check_neemuds_deps():
    if(not check_mod_pkg("numpy")):
        raise Exception(col(Color.RED, "numpy module not found. You must i"
                            "nstall it, read NEEMUDS's doc."))

try:

    from py3toolset.dep import check_mod_pkg
    from py3toolset.fs import get_prog_parent_dir

    BASH_AUTOCOMP_SCRIPT = "autocomp_neemuds.sh"

    PROG_PDIR = get_prog_parent_dir()+os.sep
    # generic code using dict to process all libs
    LIBS_INFO = [
        {'name': 'Mineos Python wrapper lib.',
         'ppath': [ 'Mineos_lib', 'Mineos_lib/src'],
         'filename': 'pymineos_.so',
         'enabled': True},
        {'name': 'DispHermann Python wrapper lib.',
         'ppath': [ 'DispHerrmann_lib', 'DispHerrmann_lib/src'],
         'filename': 'pydisper96_.so',
         'enabled': True},
        {'name': 'MCMC Python wrapper lib.',
         'ppath': [ 'MCMCInv_lib'],
         'filename': 'mcmc.so',
         'enabled': True},
        {'name' : 'Gaussianfilter wrapper lib.',
         'ppath' : [ 'gaussianfilter' ],
         'filename': 'gaussianfilter.so',
         'enabled': False}
    ]

    if loading_libs:
        for lib_info in LIBS_INFO:
            if not lib_info['enabled']:
                continue
            load_lib(lib_info)

    check_neemuds_deps()

except Exception as e:
    traceback.print_exc(file=sys.stdout)
    msg = str(e)
    if(not msg.lower().startswith("error")):
        msg = "Error: " + msg
    print_frame(msg, Color.RED, centering=False)
    sys.exit()
