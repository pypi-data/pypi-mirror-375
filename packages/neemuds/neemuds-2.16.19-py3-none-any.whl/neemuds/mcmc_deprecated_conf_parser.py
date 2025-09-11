"""
This module is deprecated. It provides functions to parse old format
configuration files (`.conf' file extension).
Use preferably mcmc_config_parser module and .ini configuration files.
"""

import re

COLD_RUN=0
HOT_RUN=1
LOCAL=0
GLOBAL=1


def get_section_lines_from_conf(cfg_file, section_number):
    """
    A section title in conf. file is assumed to take only one line
    and to be between two lines starting by #---, otherwise the function will fail.
    """
    # cfg_file existence is supposed to be ensured by the caller
    section_found = False
    section_lines = []
    in_section_title = False
    in_section_content = False
    with open(cfg_file) as f:
        for l in f.readlines():
            if(section_found):
                if(in_section_title and in_section_content):
                    break # full section read
                elif(not re.match('^\s*#.*', l) and not re.match('^\s*$', l)):
                    section_lines.append(l[:-1].split('#')[0])
                    in_section_content = True
            elif(in_section_title and not section_found):
                section_found = re.match('.*#'+str(section_number)+'\s.*',l) != None
            if(re.match(r'^\s*#\s*-{3,}.*', l)):
                in_section_title = not in_section_title
    return section_lines

def get_resdir_from_conf(cfg_file):
    # cfg_file existence is supposed to be ensured by the caller
    lines = get_section_lines_from_conf(cfg_file, 1)
    if(len(lines) < 1): raise Exception("No section #1 for profile name/result directory was found in config file: "+cfg_file)
    return lines[0]

def get_num_markov_chains_from_conf(cfg_file):
    # cfg_file existence is supposed to be ensured by the caller
    lines = get_section_lines_from_conf(cfg_file, 7)
    if(len(lines) < 1): raise Exception("No section #7 for number of Markov chains was found in config file: "+cfg_file)
    return int(lines[0])

def get_opt_sampled_mods_output_from_conf(cfg_file):
     # cfg_file existence is supposed to be ensured by the caller
    lines = get_section_lines_from_conf(cfg_file, 34)
    if(len(lines) < 1): raise Exception("No section #34 for sampled model output enabling option in config file: "+cfg_file)
    return int(lines[0])

def get_scale_from_conf_file(cfg_file):
    """
        Returns GLOBAL or LOCAL to identify the scale type of the mcmc conf. file cfg_file.
    """
    # cfg_file existence is supposed to be ensured by the caller
    lines = get_section_lines_from_conf(cfg_file, 2)
    if(len(lines) < 1): raise Exception("Not section #2 for scale type in config file: "+cfg_file)
    return int(lines[0]) % 4 # 0 and 2 are for local scale/Herrmann, 1 and 3
    # for global scale/Mineos

def get_max_depth_from_conf_file(cfg_file):
    """
    """
    lines = get_section_lines_from_conf(cfg_file, 10)
    if(len(lines) < 1): raise Exception("Not section #10 for model max depth in config file: "+cfg_file)
    return float(lines[0].split()[1])


def get_num_bz_curves_from_conf(cfg_file):
    # cfg_file existence is supposed to be ensured by the caller
    lines = get_section_lines_from_conf(cfg_file, 12)
    if(len(lines) < 1): raise Exception("No section #12 for number of Bezier curves was found in config file: "+cfg_file)
    return [int(field) for field in lines[0].split() if (re.match('\s*\d+\s*', field))]

def get_runtype_num_of_iterations(cfg_file, runtype):
     # cfg_file existence is supposed to be ensured by the caller
    lines = get_section_lines_from_conf(cfg_file, 9)
    if(len(lines) < 1): raise Exception("No section #9 for number of Markov chains was found in config file: "+cfg_file)
    fields = lines[0].split()
    if(runtype == COLD_RUN):
        return int(fields[0])
    elif(runtype == HOT_RUN):
        return int(fields[1])
    else:
        raise Exception("Invalid runtype.")
