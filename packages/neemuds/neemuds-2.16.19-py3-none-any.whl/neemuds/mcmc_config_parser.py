import configparser
from os.path import exists, expanduser, join, basename
from py3toolset.nmath import str_isint, str_isfloat
from math import pi
import numpy as np
from neemuds.params import parse_params_conf_file
from neemuds.planet_params import PlanetParams
from neemuds.local_params import LocalParams
from re import match
from py3toolset.txt_color import warn
from tempfile import gettempdir
from time import sleep
from random import randint

class MCMCConfig(configparser.ConfigParser):

        SCALE_LOCAL_HERRMANN = 0
        SCALE_GLOBAL_MINEOS = 1
        SCALE_LOCAL_HERRMANN_K_MU = 2
        SCALE_GLOBAL_MINEOS_K_MU = 3
        CLAMPING_SAMPLES_INTO_PRIORS = 1
        CLAMPING_SAMPLES_INTO_EPRIORS = 2
        GOF_CALC_METH_DISCRETE = 0
        GOF_CALC_METH_CONTINUOUS = 1
        PHI_RADIUS_PRIOR_RELATIONSHIP_NONE = 0
        PHI_RADIUS_PRIOR_RELATIONSHIP_LINEAR1 = 1
        PHI_RADIUS_PRIOR_RELATIONSHIP_LINEAR2 = 2
        PHI_RADIUS_PRIOR_RELATIONSHIP_QUAD = 3

        CONF_SECTION_1 = "#1  MCMC Profile Name"
        CONF_SECTION_2 = "#2  Scale Type"
        CONF_SECTION_3 = "#3  Disper96/Mineos Configuration File"
        CONF_SECTION_3_DEPRECATED = "#3  Herrmann/Mineos Configuration File"
        CONF_SECTION_4 = "#4  Reference Model"
        CONF_SECTION_4_DEPRECATED = "#4  PREM File"
        CONF_SECTION_5 = "#5  Prior Files"
        CONF_SECTION_6 = "#6  K and MU Prior Files"
        CONF_SECTION_7 = "#7  Number Of Markov Chains"
        CONF_SECTION_8 = "#8  Markov Chain Seeds"
        CONF_SECTION_9 = "#9  Numbers of Iterations for Cold and Hot Runs "
        CONF_SECTION_10 = "#10  Minimal and Maximal Depths for Models Exploration"
        CONF_SECTION_11 = "#11  The Max Depth of the MCMC Working Zone"
        CONF_SECTION_12 = "#12  Number of Bézier Blocks/Curves per Parameter"
        CONF_SECTION_12_DEPRECATED = "#12  Number of Bezier Blocks/Curves per Parameter"
        CONF_SECTION_13 = "#13  Minimal distance between two anchor points"
        CONF_SECTION_14 = "#14  Layer Thickness of the Depth Models"
        CONF_SECTION_15 = "#15  Radius/Modulus/Norm for the gradient/tangent of each Bézier curve"
        CONF_SECTION_15_DEPRECATED = "#15  Radius/Modulus/Norm for the gradient/tangent of each Bezier curve"
        CONF_SECTION_16 = "#16  Radius Prior Domain "
        CONF_SECTION_17 = "#17  PHI Reference Angle"
        CONF_SECTION_18 = "#18  PHI Prior Min Max Bounds"
        CONF_SECTION_19 = "#19  VS Prem Join Value (at max depth or just after) "
        CONF_SECTION_20 = "#20  VP Prem Join Value (at max depth or just after)"
        CONF_SECTION_21 = "#21  RHO Prem Join Value (at max depth or just after)"
        CONF_SECTION_22 = "#22  Anisotropy XI Prem Join Value (at max depth or just after)"
        CONF_SECTION_23 = "#23  Prior ETA Bounds (min and max)"
        CONF_SECTION_24 = "#24  Prior XI bounds (min and max)"
        CONF_SECTION_25 = "#25  Slope Regularization of Sampled-models"
        CONF_SECTION_25_DEPRECATED = "#25  Reserved section for future use"
        CONF_SECTION_26 = "#26  Coefficients for Effective Prior Building 3rd Method"
        CONF_SECTION_26_DEPRECATED = "#26  Coefficients for 2nd Method Prior Construction and 3rd Method Effective Prior Construction"
        CONF_SECTION_27 = "#27  Effective Prior Construction Method"
        CONF_SECTION_28 = "#28  Dynamic Triangle for Effective Prior Construction  "
        CONF_SECTION_29 = "#29  Gradients for VS effective prior method 5 (see section #27)"
        CONF_SECTION_30 = "#30  Clamping VS, VP, RHO etc. sample-points into priors"
        CONF_SECTION_31 = "#31  Constraining VP and RHO samples from VS"
        CONF_SECTION_32 = "#32  Gaussian width parameters for VP, VS, RHO, XI, ETA, depth, radius and PHI"
        CONF_SECTION_33 = "#33  Flushing period for result output in files"
        CONF_SECTION_34 = "#34  Sampled Models Output Option"
        CONF_SECTION_35 = "#35  Accepting All Models in Metropolis Hastings Algo."
        CONF_SECTION_36 = "#36  Weight coefficients for hot run model change probability law"
        CONF_SECTION_37 = "#37  Hot run probabilities of picking one parameter instead of another"
        CONF_SECTION_38 = "#38  Goodness of Fit Computation Method"
        CONF_SECTION_39 = "#39  Radius-phi Priors Relationship"
        CONF_SECTION_40 = "#40  Computing (VP/VS) Bézier model"
        SECTION_NUMBER = 40

        # not used yed because the parsing of mineos/herrmann file is handled by parse_params_conf_file
        MINEOS_CONF_TITLE = "Mineos/Global Scale configuration"
        DISPER96_CONF_TITLE = "Disper96/Local Scale configuration"

        section_err_msg = "Error in conf section #"

        def __init__(self, filepath=None):
            super(MCMCConfig, self).__init__()
            if filepath is not None:
                filepath = expanduser(filepath)
                self.filepath = filepath
                self.read(filepath)
                self.finish_parsing()
            self.filepath = filepath

        def section_num_to_title(c, num):
            return \
            c.__getattribute__('CONF_SECTION_'+str(num))

        def check_section_field_float(c, section_number, field,
                                      mandatory=True, abs=True):
            section_title = c.section_num_to_title(section_number)
            if mandatory and field not in c[section_title]:
                raise Exception(c.section_err_msg+str(section_number)+" the "
                                "mandatory "+field+" variable is missing in"
                                " conf.")
            if field in c[section_title]:
                if not str_isfloat(c[section_title][field], abs=abs):
                    raise Exception(c.section_err_msg+str(section_number)+": the "
                                    "variable "+field+" must be"
                                    " set to a "+("positive" if abs else "")+" float value.")
                return float(c[section_title][field])
            else:
                return None

        def check_section_float_list_field(c, section_number, field,
                                           mandatory=True, abs=True):
            section_title = c.section_num_to_title(section_number)
            if mandatory and field not in c[section_title]:
                raise Exception(c.section_err_msg+str(section_number)+" the"
                                " mandatory"+field+" variable is missing in"
                                " conf.")
            if field not in c[section_title]:
                raise Exception(c.section_err_msg+str(section_number)+": the"
                                +field+" must be"
                                " set to a float values.")
            subfields = c[section_title][field].split()
            for i,f in enumerate(subfields):
                if not str_isfloat(f, abs=abs):
                    raise Exception(c.section_err_msg+str(section_number)+": "
                                    +f+" is not a float.")
                subfields[i] = float(f)
            return subfields

        def check_section_int_list_field(c, section_number, field,
                                         mandatory=True, abs=True,
                                         eval_str_mul=False):
            section_title = c.section_num_to_title(section_number)
            if mandatory and field not in c[section_title]:
                raise Exception(c.section_err_msg+str(section_number)+" the"
                                " mandatory"+field+" variable is missing in"
                                " conf.")
            if field not in c[section_title]:
                raise Exception(c.section_err_msg+str(section_number)+": the"
                                +field+" must be"
                                " set to a int values.")
            val = c[section_title][field]
            if eval_str_mul and '*' in val:
                # handle str mul operator if used
                regex1 = r'["\']\s*(\d+\s+)+["\']\s*\*\s*(\d+)'
                regex2 = r'\s*(\d+)\s*\*\s*["\'](\s+\d+)+["\']'
                if m1 := match(regex1, val):
                    val = eval(val)
                elif m2 := match(regex2, val):
                    val = eval(val)
                else:
                    raise ValueError(c.section_err_msg+str(section_number)+": "
                                    +field+" contains a str multiplication"
                                  " operator which must be used only in a form"
                                  " like \"1 2 3 \"*5 or 5*\" 1 2 3\" (take care"
                                  " of spaces)")
            subfields = val.split()
            for i,f in enumerate(subfields):
                if not str_isint(f, abs=abs):
                    raise Exception(c.section_err_msg+str(section_number)+": "
                                    +f+" is not a int.")
                subfields[i] = int(f)
            return subfields

        def check_section_field_int(c, section_number, field,
                                      mandatory=True, abs=True):
            section_title = c.section_num_to_title(section_number)
            if mandatory and field not in c[section_title]:
                raise Exception(c.section_err_msg+str(section_number)+" the "
                                "mandatory "+field+" variable is missing in"
                                " conf.")
            if field in c[section_title]:
                if not str_isint(c[section_title][field], abs=abs):
                    raise Exception(c.section_err_msg+str(section_number)+": the "
                                    "variable "+field+" must be"
                                    " set to a"+(" positive" if abs else "")+" int value.")
                return int(c[section_title][field])
            else:
                return None

        def print_section_err(c, section_number, msg):
            raise Exception(c.section_err_msg+str(section_number)+": "+msg)


        def check_normalized_field(c, section_number, field):
            # field is supposed to be initialized in c and of type float
            fval = c.__getattribute__(field)
            if fval < 0 or fval > 1:
                c.print_section_err(section_number, field+" must be a "
                                    "normalized value (between 0 and 1)")

        def check_mineos_mod_format(c, filepath, section, extra_name=''):
            """
            Verifies filepath is a well-formatted mineos input model.
            """
            # TODO: verify the three first rows
            in_mod = np.loadtxt(filepath, skiprows=3)
            if in_mod.shape[1] != 9:
                raise Exception(filepath+' in conf. section #' + str(section) +
                                ((' model ' + extra_name) if extra_name != '' else
                                '')+
                                ' is not a Mineos well-formatted file (the'
                                ' model data lines must have 9 fields: z,'
                                ' rho, vpv, vsv,' ' qshear, qkappa, vph, vsh,'
                                ' eta')
            # ==== verify the format and spacing between fields
            # 1. generate a well-formatted file from input
            tmp_out = None
            while tmp_out is None or exists(tmp_out):
                tmp_out = join(gettempdir(), basename(filepath)+str(randint(1,
                                                                            2**30)))
            fmt = ('%7.0f.','%8.2f','%8.2f','%8.2f',
                   '%8.1f','%8.1f','%8.2f','%8.2f','%8.5f')
            # In mineos doc it is: (f8.0, 3f9.2, 2f9.1, 2f9.2, f9.5)
            # but this is the fortran format
            # anyway prem_noocean.txt which comes from mineos archive
            # (from geodynamics.org) matches the format fmt so it is
            # our reference
            np.savetxt(tmp_out+'_', in_mod, fmt=fmt)
            f = open(filepath, 'r')
            all_lines = f.readlines()[:3]
            f.close()
            f = open(tmp_out+'_', 'r')
            all_lines += f.readlines()
            f.close()
            # print("generating well-formatted mineos file:", tmp_out)
            f = open(tmp_out, 'w')
            f.writelines(all_lines)
            f.close()
            # 2. verify the two files are identical
            f1 = open(filepath, 'r')
            f2 = open(tmp_out, 'r')
            lines1 = f1.readlines()
            lines2 = f2.readlines()
            if np.any(lines1 != lines2):
                sleep_t = 5
                warn(filepath+' in conf. section #' + str(section) +
                     ((' model ' + extra_name) if extra_name != ''
                      else '')+
                     ' the Mineos file is not well-formatted'
                     ' (proper format is: '+str(fmt)+'). You can'
                     ' replace your file by this generated equivalent one '+
                     tmp_out+ ' [at your own risk: verify the files'
                     ' before!!]')
                warn('execution will continue in ' + str(sleep_t) + 's if'
                     ' you don\'t stop it  (CTLR-C).')
#                sleep(sleep_t) # let user time to see the warning

        def parse_section_1(c):
            if c[c.CONF_SECTION_1]['profile_name'] == None:
                raise Exception(c.section_err_msg+"1: The profile name can't be"
                                " empty in section #1.")
            c.profile_name = c[c.CONF_SECTION_1]['profile_name']

        def parse_section_2(c):
            if not str_isint(c[c.CONF_SECTION_2]['scale_type']) or \
               int(c[c.CONF_SECTION_2]['scale_type']) not in [c.SCALE_GLOBAL_MINEOS,
                                                              c.SCALE_LOCAL_HERRMANN,
                                                              c.SCALE_GLOBAL_MINEOS_K_MU,
                                                              c.SCALE_LOCAL_HERRMANN_K_MU]:
                raise Exception(c.section_err_msg+"2: the scale type is not "
                                "valid, it must be in :"
                                +str(c.SCALE_GLOBAL_MINEOS)+
                                "  "+str(c.SCALE_LOCAL_HERRMANN)+
                                "  "+str(c.SCALE_GLOBAL_MINEOS_K_MU)+
                                "  "+str(c.SCALE_LOCAL_HERRMANN_K_MU))
            c.scale_type = int(c[c.CONF_SECTION_2]['scale_type'])

        def parse_section_3(c):
            if 'grv_conf_file' in c[c.CONF_SECTION_3]:
                tmp_val = expanduser(c[c.CONF_SECTION_3]['grv_conf_file'])
                if not exists(tmp_val):
                    raise Exception(c.section_err_msg+"3 the file "
                                    +str(tmp_val)+" doesn't exist.")
                c.grv_conf_file = tmp_val
                if c.scale_type%2 == c.SCALE_GLOBAL_MINEOS:
                    c.parse_mineos_config()
                elif c.scale_type%2 == c.SCALE_LOCAL_HERRMANN:
                    c.parse_herrmann_config()
            elif c.scale_type%2 == c.SCALE_GLOBAL_MINEOS:
                raise Exception('grv_conf_file variable is not'
                                ' set in section #3 (it is mandatory if scale'
                                ' type is '+str(c.SCALE_GLOBAL_MINEOS))


        def parse_section_4(c):
            if 'ref_mod_file' in c[c.CONF_SECTION_4]:
                tmp_val = expanduser(c[c.CONF_SECTION_4]['ref_mod_file'])
                if c.scale_type%2 == c.SCALE_LOCAL_HERRMANN and \
                   tmp_val.lower() != 'none':
                    raise Exception('If scale type in section #2 is '
                                    +str(c.SCALE_LOCAL_HERRMANN)+
                                    ' (local/Herrmann scale) the section #4'
                                    ' ref_mod_file must be set to none. The value found'
                                    ' is: '+str(tmp_val))
                if c[c.CONF_SECTION_4]['ref_mod_file'] not in [None, 'None', 'none'] \
                   and not exists(tmp_val):
                    raise Exception(c.section_err_msg+"4: the file "
                                    +tmp_val+" doesn't exists.")
                c.ref_mod_file = tmp_val
                if c.scale_type%2 == c.SCALE_GLOBAL_MINEOS:
                    c.check_mineos_mod_format(c.ref_mod_file, 4)
            elif c.scale_type%2 == c.SCALE_GLOBAL_MINEOS:
                raise Exception('ref_mod_file variable is not'
                                ' set in section #4 (it is mandatory if scale'
                                ' type is '+str(c.SCALE_GLOBAL_MINEOS))

        def parse_section_5(c):
            # the priority is to prior_lo_file and prior_hi_file variables
            # and secondarily to the per-wave-type variables
            # rayl/love_prior_lo/hi_file
            c.prior_lo_file = c.rayl_prior_lo_file = \
                    c.love_prior_lo_file = None
            c.prior_hi_file = c.rayl_prior_hi_file = \
                    c.love_prior_hi_file = None
            c.specific_love_prior = False
            if 'prior_lo_file' in c[c.CONF_SECTION_5]:
                tmp_val = expanduser(c[c.CONF_SECTION_5]['prior_lo_file'])
                if not exists(tmp_val):
                    raise Exception(c.section_err_msg+"5: the file "
                                    +tmp_val+
                                    " (low boundary prior file) doesn't"
                                    " exist.")
                c.prior_lo_file = tmp_val
                c.rayl_prior_lo_file = c.prior_lo_file
                c.love_prior_lo_file = c.prior_lo_file
            if 'prior_hi_file' in c[c.CONF_SECTION_5]:
                tmp_val = expanduser(c[c.CONF_SECTION_5]['prior_hi_file'])
                if not exists(tmp_val):
                    raise Exception(c.section_err_msg+"5: the file "
                                    +tmp_val+
                                    " (high boundary prior file) doesn't"
                                    " exist.")
                c.prior_hi_file = tmp_val
                c.rayl_prior_hi_file = c.prior_hi_file
                c.love_prior_hi_file = c.prior_hi_file
            if 'rayl_prior_lo_file' in c[c.CONF_SECTION_5]:
                if not exists(c[c.CONF_SECTION_5]['rayl_prior_lo_file']):
                    raise Exception(c.section_err_msg+"5: the file"
                                    +c[c.CONF_SECTION_5]['rayl_prior_lo_file']+
                                    " (rayl_prior_lo_file) doesn't"
                                    " exist.")
                c.rayl_prior_lo_file = expanduser(c[c.CONF_SECTION_5]['rayl_prior_lo_file'])
            if 'rayl_prior_hi_file' in c[c.CONF_SECTION_5]:
                if not exists(c[c.CONF_SECTION_5]['rayl_prior_hi_file']):
                    raise Exception(c.section_err_msg+"5: the file"
                                    +c[c.CONF_SECTION_5]['rayl_prior_hi_file']+
                                    " (rayl_prior_hi_file) doesn't exist.")
                c.rayl_prior_hi_file = expanduser(c[c.CONF_SECTION_5]['rayl_prior_hi_file'])
            if 'love_prior_lo_file' in c[c.CONF_SECTION_5]:
                if not exists(c[c.CONF_SECTION_5]['love_prior_lo_file']):
                    raise Exception(c.section_err_msg+"5: the file "
                                    +c[c.CONF_SECTION_5]['love_prior_lo_file']+
                                    " (love_prior_lo_file) doesn't exist.")
                c.love_prior_lo_file = \
                        expanduser(c[c.CONF_SECTION_5]['love_prior_lo_file'])
                c.specific_love_prior = True
            if 'love_prior_hi_file' in c[c.CONF_SECTION_5]:
                if not exists(c[c.CONF_SECTION_5]['love_prior_hi_file']):
                    raise Exception(c.section_err_msg+"5: the file "
                                    +c[c.CONF_SECTION_5]['love_prior_hi_file']+
                                    " (love_prior_hi_file) doesn't exist.")
                c.love_prior_hi_file = \
                        expanduser(c[c.CONF_SECTION_5]['love_prior_hi_file'])
                c.specific_love_prior = True
            for field in ['rayl_prior_lo_file', 'rayl_prior_hi_file',
                          'love_prior_lo_file', 'love_prior_hi_file']:
                if c.__getattribute__(field) == None:
                    raise Exception(c.section_err_msg+"5 a lower/higher "
                                    "boundary prior is missing in section.")
                if c.scale_type%2 == c.SCALE_GLOBAL_MINEOS:
                    c.check_mineos_mod_format(c.__getattribute__(field), 5,
                                              field.replace('rayl_',
                                                            '*').replace('love_',
                                                                         '*'))


        def parse_section_6(c):
            c.K_prior_file = c.MU_prior_file = None
            if 'K_prior_file' in c[c.CONF_SECTION_6]:
                tmp_val = expanduser(c[c.CONF_SECTION_6]['K_prior_file'])
                if tmp_val != 'None' and not exists(tmp_val):
                    raise Exception(c.section_err_msg+"6: the file "
                                    +tmp_val+
                                    " (K prior file) doesn't"
                                    " exist.")
                c.K_prior_file = None if tmp_val == 'None' else tmp_val
            if 'MU_prior_file' in c[c.CONF_SECTION_6]:
                tmp_val = expanduser(c[c.CONF_SECTION_6]['MU_prior_file'])
                if tmp_val != 'None' and not exists(tmp_val):
                    raise Exception(c.section_err_msg+"6: the file "
                                    +tmp_val+
                                    " (MU prior file) doesn't"
                                    " exist.")
                c.MU_prior_file = None if tmp_val == 'None' else tmp_val
            if c.K_prior_file is None and c.MU_prior_file is not None \
                    or c.K_prior_file is not None and c.MU_prior_file is None:
                        raise Exception('the two K and MU priors must be'
                                        ' defined or none of them in section #6')

        def parse_section_7(c):
            if not 'chain_number' in c[c.CONF_SECTION_7] or not \
            str_isint(c[c.CONF_SECTION_7]['chain_number'], abs=False):
                raise Exception(c.section_err_msg+"7: the number of markov"
                                "chains is invalid. It must be -1 or a "
                                "positive integer.")
            c.chain_number = int(c[c.CONF_SECTION_7]['chain_number'])
            if c.chain_number < 0 and c.chain_number != -1:
                raise Exception(c.section_err_msg+"7: the only valid negative"
                                " value for chain_number variable is -1.")

        def parse_section_8(c):
            c.chain_seeds = c.check_section_int_list_field(8, 'chain_seeds',
                                                    mandatory=True, abs=False)
            if len(c.chain_seeds) < c.chain_number:
                c.chain_seeds += [-1 for i in range(c.chain_number-len(c.chain_seeds))]

            for seed in c.chain_seeds:
                if seed < 0 and seed != -1:
                    raise Exception(c.section_err_msg+"8: the only valid negative"
                                    " value for seed variable is -1.")

        def parse_section_9(c):
            c.cold_n_iters = c.check_section_field_int(9, 'cold_n_iters',
                                                     mandatory=True)
            c.hot_n_iters = c.check_section_field_int(9, 'hot_n_iters',
                                                     mandatory=True)

        def parse_section_10(c):
            c.min_depth = c.check_section_field_float(10, 'min_depth',
                                                      mandatory=True)
            c.max_depth = c.check_section_field_float(10, 'max_depth',
                                                      mandatory=True)
            if c.min_depth != 0:
                raise ValueError(c.section_err_msg+"10: nonzero min_depth is"
                                 " not yet implemented.")
            if not 'max_depth' in c[c.CONF_SECTION_10] \
               or not str_isfloat(c[c.CONF_SECTION_10]['max_depth']):
                raise Exception(c.section_err_msg+"10: the max_depth must be a"
                                " float number.")
            c.max_depth = float(c[c.CONF_SECTION_10]['max_depth'])
            c.h = c.max_depth-c.min_depth
            if c.h <= 0:
                raise ValueError(c.section_err_msg+"10: max_depth must be"
                                 " greater than min_depth.")


        def parse_section_11(c):
            c.last_bz3_min_depth = c.check_section_field_float(11,
                                                               'last_bz3_min_depth',
                                                               mandatory=True)
            if c.last_bz3_min_depth > c.max_depth \
               or c.last_bz3_min_depth < c.min_depth:
                raise Exception(c.section_err_msg+"11: the last_bz3_min_depth"
                                " must be between min_depth and max_depth.")

        def parse_section_12(c):
            c.chain_bz3_numbers = c.check_section_int_list_field(12, 'chain_bz3_numbers',
                                                                 mandatory=True, eval_str_mul=True)
            if len(c.chain_bz3_numbers) < c.chain_number:
                c.chain_bz3_numbers += [c.chain_bz3_numbers[-1] for i in
                                        range(len(c.chain_bz3_numbers),
                                              c.chain_number)]
            elif len(c.chain_bz3_numbers) > c.chain_number:
                c.chain_bz3_numbers = c.chain_bz3_numbers[:c.chain_number]
            for i in c.chain_bz3_numbers:
                if i < 2:
                    raise ValueError(c.section_err_msg+"12: the minimum number"
                                     " of Bézier curves is two (one curve"
                                     " before the joint point and one curve"
                                     " after).")


        def parse_section_13(c):
            c.min_dist = c.check_section_field_float(13, 'min_dist',
                                                   mandatory=True)

        def parse_section_14(c):
            c.layer_thickness = c.check_section_field_float(14, 'layer_thickness',
                                                   mandatory=True)
            if c.layer_thickness > c.min_dist:
                raise ValueError(c.section_err_msg+"14: min_dist between"
                                 " anchor points must be greater than sampling the"
                                 " layer thickness.")

        def parse_section_15(c):
            c.bz3_starting_radius = c.check_section_field_float(15, 'bz3_starting_radius',
                                                       mandatory=True)

        def parse_section_16(c):
            c.bz3_radius_min = c.check_section_field_float(16,
                                                                   'bz3_radius_min',
                                                                   mandatory=True)
            c.bz3_radius_max = c.check_section_field_float(16,
                                                                   'bz3_radius_max',
                                                                   mandatory=True)

        def parse_section_17(c):
            c.bz3_starting_angle = c.check_section_field_float(17, 'bz3_starting_angle',
                                                        mandatory=True)
            c.bz3_starting_angle *= pi/180

        def parse_section_18(c):
            c.bz3_angle_min = c.check_section_field_float(18,
                                                                'bz3_angle_min',
                                                                mandatory=True)
            c.bz3_angle_max = c.check_section_field_float(18,
                                                                'bz3_angle_max',
                                                                mandatory=True)
            if c.bz3_angle_min >= c.bz3_angle_max:
                c.print_section_err(18, 'bz3_angle_min must be smaller'
                                    ' than bz3_angle_max')
            c.bz3_angle_min *= pi/180
            c.bz3_angle_max *= pi/180

        def parse_section_19(c):
            is_loc = c.scale_type%2 == c.SCALE_LOCAL_HERRMANN
            c.prem_join_vs = c.check_section_field_float(19, 'prem_join_vs',
                                                         mandatory=is_loc,
                                                         abs=is_loc)

        def parse_section_20(c):
            is_loc = c.scale_type%2 == c.SCALE_LOCAL_HERRMANN
            c.prem_join_vp = c.check_section_field_float(20, 'prem_join_vp',
                                                         mandatory=is_loc,
                                                         abs=is_loc)

        def parse_section_21(c):
            is_loc = c.scale_type%2 == c.SCALE_LOCAL_HERRMANN
            c.prem_join_rho = c.check_section_field_float(21, 'prem_join_rho',
                                                         mandatory=is_loc,
                                                         abs=is_loc)

        def parse_section_22(c):
            c.prem_join_xi = c.check_section_field_float(22, 'prem_join_xi',
                                                         mandatory=False,
                                                         abs=True)
            #TODO: no way to determine if it's mandatory (R+L updf given case
            # to MCMC)
            # should be an argument passed to the ctor

        def parse_section_23(c):
            is_glob = c.scale_type % 2 == c.SCALE_GLOBAL_MINEOS
            c.eta_prior_min = c.check_section_field_float(23, 'eta_prior_min',
                                                          abs=False,
                                                          mandatory=is_glob)
            c.eta_prior_max = c.check_section_field_float(23, 'eta_prior_max',
                                                          abs=False,
                                                          mandatory=is_glob)
            if is_glob and c.eta_prior_min >= c.eta_prior_max:
                c.print_section_err(23, 'eta_prior_min must be smaller'
                                    ' than eta_prior_max')



        def parse_section_24(c):
            c.xi_prior_min = c.check_section_field_float(24, 'xi_prior_min',
                                                      abs=False)
            c.xi_prior_max = c.check_section_field_float(24, 'xi_prior_max',
                                                      abs=False)
            if c.xi_prior_min >= c.xi_prior_max:
                c.print_section_err(24, 'xi_prior_min must be smaller'
                                    ' than xi_prior_max')

        def parse_section_25(c):
            # deprecated old section 25 default
            c.prior_construct_method = 1 # TODO: should be completly deleted
                                         # one day
            # now set current section 25 slope_reg
            section_name = c.__getattribute__("CONF_SECTION_25")
            section_name_dep = \
                    c.__getattribute__("CONF_SECTION_25_DEPRECATED")
            if section_name not in c:
                section_name = section_name_dep
            if 'slope_reg' in c[section_name]:
                c.slope_reg = str(c[section_name]['slope_reg'])
            else:
                c.slope_reg = None # for old conf files
            except_regex = r'(\d+):(\d+):([-0-9.]+)'
            nlayers = int(np.ceil(c.max_depth / c.layer_thickness))
            if c.slope_reg in ['None', None]:
                c.slope_reg = np.array([])
            elif str_isfloat(c.slope_reg, abs=False):
                c.slope_reg = np.full(nlayers, float(c.slope_reg))
            else:
                slope_reg_list = c.slope_reg.split()
                glob_slope = slope_reg_list[0]
                if not str_isfloat(glob_slope, abs=False):
                    raise ValueError('Global slope in slope_reg (section #25)'
                                     ' is not a float (value:' + glob_slope)
                slope_reg = np.full(nlayers, float(glob_slope))
                for s_except in slope_reg_list[1:]:
                    if m := match(except_regex, s_except):
                        z1 = m.group(1)
                        z2 = m.group(2)
                        slope = m.group(3)
                        for z in [z1, z2]:
                            if not str_isfloat(z):
                                raise ValueError(z + " is not a float in "
                                                 "section #25, exception block:"
                                                 + s_except)
                        if not str_isfloat(slope, abs=False):
                            raise ValueError('slope must be a float.'
                                             ' Verify section #25'
                                             ' exception block: ' + s_except)
                        slope = float(slope)
                        z1 = float(z1)
                        z2 = float(z2)
                        for z in [z1, z2]:
                            if z < 0 or z > c.max_depth:
                                raise ValueError(str(z) + " is not in valid"
                                                 " 0-depth_max range "
                                                 "section #25, exception block:"
                                                 + s_except)
                        z1i = int(float(z1) // c.layer_thickness)
                        z2i = int(float(z2) // c.layer_thickness)
                        slope_reg[z1i:z2i+1] = slope
                        c.slope_reg = slope_reg
                    else:
                        raise ValueError("Invalid format for `slope_reg' see"
                                         " conf. doc")
                # c.slope_reg is an array of slopes for each layer of
                # c.layer_thickness for all the models (from 0 to c.max_depth)


        def parse_section_26(c):
            section_title = c.section_num_to_title(26)
            if 'prem_vsv2prior_vs_percent' in c[section_title]:
                warn("prem_vsv2prior_vs_percent found in conf. section 26 is a"
                     " deprecated parameter and should not be used"
                     " anymore (it is ignored by neemuds_mcmc.py).")
                c.prem_vsv2prior_vs_percent = \
                        c.check_section_field_float(26, 'prem_vsv2prior_vs_percent')
                c.check_normalized_field(26, "prem_vsv2prior_vs_percent")
            else:
                c.prem_vsv2prior_vs_percent = -1
            c.prior_vs2vp_coeffs = \
                    c.check_section_float_list_field(26,
                                                     'prior_vs2vp_coeffs')
            c.prior_vp2rho_coeffs = \
                    c.check_section_float_list_field(26,
                                                     'prior_vp2rho_coeffs')
            c.prior_rho_offsets = \
                    c.check_section_float_list_field(26, 'prior_rho_offsets')

        def parse_section_27(c):
            c.eprior_construct_method = c.check_section_field_int(27,
                                                            'eprior_construct_method')
            valid_vals = [1, 2, 3, 4, 5]
            if c.eprior_construct_method not in valid_vals:
                c.print_section_err(27, 'eprior_construct_method must be in '
                                    +str(valid_vals))

        def parse_section_28(c):
            c.prior_triangle_angle = c.check_section_field_float(28,
                                                                 'prior_triangle_angle',
                                                                 abs=False)
            c.prior_triangle_angle *= pi / 180

        def parse_section_29(c):
            c.eprior_triangle_gradients = c.check_section_float_list_field(29,
                                                                           'eprior_triangle_gradients',
                                                                           abs=False)
            if c.eprior_triangle_gradients[0] > c.eprior_triangle_gradients[1]:
                c.print_section_err(29, "the two gradiants must be in"
                                    " ascending order.")

        def parse_section_30(c):
            c.clamping_samples = c.check_section_int_list_field(30, 'clamping_samples',
                                                                mandatory=True, abs=True,
                                                                eval_str_mul=True)
            valid_vals = [0, 1, 2]
            for v in c.clamping_samples:
                if v not in valid_vals:
                    c.print_section_err(30, 'clamping_samples value(s) must be in '
                                        +str(valid_vals))

            if len(c.clamping_samples) == 1:
                # only one integer specified in conf
                # it applies to all parameters
                c.clamping_samples = [c.clamping_samples[0] for _ in range(5)]

            # 5 for VP, VS, RHO, XI, ETA
            d = 5 - len(c.clamping_samples)
            if d < 0:
                raise ValueError("Too many values for clamping_samples, max is"
                                 " 5")
            elif d > 0:
                c.clamping_samples += [ 0 ] * d

        def parse_section_31(c):
            c.constraining_vp_rho_from_vs = c.check_section_field_int(31,
                                                                      'constraining_vp_rho_from_vs')
            valid_vals = [0, 1]
            if c.constraining_vp_rho_from_vs not in valid_vals:
                c.print_section_err(31, 'constraining_vp_rho_from_vs must be in '
                                    +str(valid_vals))

        def parse_section_32(c):
            for field in [ 'coldrun_vp_meth', 'coldrun_vs_meth', 'coldrun_rho_meth', 'coldrun_xi_meth',
                          'coldrun_eta_meth', 'hotrun_vp_meth', 'hotrun_vs_meth', 'hotrun_rho_meth',
                          'hotrun_xi_meth', 'hotrun_eta_meth', 'coldrun_depth_meth', 'hotrun_depth_meth',
                          'coldrun_radius_meth', 'coldrun_phi_meth', 'hotrun_radius_meth',
                          'hotrun_phi_meth', 'coldrun_vp_const_sigma', 'coldrun_vs_const_sigma',
                          'coldrun_rho_const_sigma', 'coldrun_xi_const_sigma', 'coldrun_eta_const_sigma',
                          'hotrun_vp_const_sigma', 'hotrun_vs_const_sigma', 'hotrun_rho_const_sigma',
                          'hotrun_xi_const_sigma', 'hotrun_eta_const_sigma', 'coldrun_depth_const_sigma',
                          'hotrun_depth_const_sigma', 'coldrun_radius_const_sigma',
                          'coldrun_phi_const_sigma', 'hotrun_radius_const_sigma',
                          'hotrun_phi_const_sigma', 'coldrun_vp_wdiv', 'coldrun_vs_wdiv',
                          'coldrun_rho_wdiv', 'coldrun_xi_wdiv', 'coldrun_eta_wdiv', 'hotrun_vp_wdiv',
                          'hotrun_vs_wdiv', 'hotrun_rho_wdiv', 'hotrun_xi_wdiv', 'hotrun_eta_wdiv',
                          'coldrun_depth_wdiv', 'hotrun_depth_wdiv', 'coldrun_radius_wdiv',
                          'coldrun_phi_wdiv', 'hotrun_radius_wdiv',
                          'hotrun_phi_wdiv' ]:
                c.__setattr__(field, c.check_section_field_float(32, field))
            # degrees to radians conversions
            c.coldrun_phi_const_sigma *= pi/180
            c.hotrun_phi_const_sigma *= pi/180

        def parse_section_33(c):
            c.output_flush_iter_period = c.check_section_field_int(33,
                                                                   'output_flush_iter_period')
        def parse_section_34(c):
            c.outputting_sampled_models = c.check_section_field_int(34,
                                                                   'outputting_sampled_models')
            valid_vals = [0, 1]
            if c.outputting_sampled_models not in valid_vals:
                c.print_section_err(34, 'outputting_sampled_models must be in '
                                    +str(valid_vals))

        def parse_section_35(c):
            c.accepting_all_models = c.check_section_field_int(35,
                                                               'accepting_all_models')
            valid_vals = [0, 1, 2]
            if c.accepting_all_models not in valid_vals:
                c.print_section_err(35, 'accepting_all_models must be in '
                                    +str(valid_vals))

        def parse_section_36(c):
            c.hotrun_alpha = c.check_section_field_float(36, 'hotrun_alpha')
            c.hotrun_beta = c.check_section_field_float(36, 'hotrun_beta')
            c.hotrun_gamma = c.check_section_field_float(36, 'hotrun_gamma')

        def parse_section_37(c):
            c.using_hotrun_param_custom_probas = c.check_section_field_int(37,
                                                                           'using_hotrun_param_custom_probas')
            valid_vals = [0, 1]
            if c.using_hotrun_param_custom_probas not in valid_vals:
                c.print_section_err(34, 'using_hotrun_param_custom_probas must be in '
                                    +str(valid_vals))
            c.hotrun_param_choice_custom_prob_law = \
            c.check_section_float_list_field(37, 'hotrun_param_choice_custom_prob_law')
            if (sum(c.hotrun_param_choice_custom_prob_law)-1 >
                np.finfo(np.float64).eps):
                c.print_section_err(37, 'the probability law must be correctly defined (the sum has to be less or equal to 1.')


        def parse_section_38(c):
            c.gof_calc_method = c.check_section_field_int(38,
                                                          'gof_calc_method')
            valid_vals = [0, 1]
            if c.gof_calc_method not in valid_vals:
                c.print_section_err(38, 'gof_calc_method must be in '
                                    +str(valid_vals))


        def parse_section_39(c):
            c.phi_radius_prior_relation = c.check_section_field_int(39,
                                                                    'phi_radius_prior_relation')
            valid_vals = [0, 1, 2, 3]
            if c.phi_radius_prior_relation not in valid_vals:
                c.print_section_err(39, 'phi_radius_prior_relation must be in '
                                    +str(valid_vals))



        def parse_section_40(c):
            c.enabling_vp_over_vs_model = c.check_section_field_int(40,
                                                                    'enabling_vp_over_vs_model')
            valid_vals = [0, 1]
            if c.enabling_vp_over_vs_model not in valid_vals:
                c.print_section_err(40, 'enabling_vp_over_vs_model must be in '
                                    +str(valid_vals))



        def finish_parsing(c):
            for i in range(1, c.SECTION_NUMBER+1):
                section_name = c.__getattribute__("CONF_SECTION_"+str(i))
                deprecated_section_id = "CONF_SECTION_"+str(i)+"_DEPRECATED"
                if hasattr(c, deprecated_section_id):
                    section_name_deprecated = \
                            c.__getattribute__(deprecated_section_id)
                else:
                    section_name_deprecated = None
                if section_name not in c and section_name_deprecated is None:
                    raise Exception("The section '"+section_name+"' is missing"
                                    " (notice that it must be exactly the same"
                                    " title in the config.)")
                if section_name_deprecated in c:
                    warn("Configuration section #"+str(i)+" title is"
                         " deprecated, it should be exactly:"
                         " '"+section_name+"'. Please update your"
                         " configuration file: "+c.filepath+
                         " because the title used might not work in a future"
                         " version.")
                    c[section_name] = c[section_name_deprecated]
            for i in range(1, 41):
                c.__getattribute__('parse_section_'+str(i))()

        def parse_mineos_config(c):
            if c.grv_conf_file not in [None, 'None']:
                # retrieve scale name in properly formatted filename (e.g.:
                    # neemuds_earth.conf, earth is the scale)
                g = match(r'.*_([^.]+)\..*', c.grv_conf_file)
                if g is None:
                    raise ValueError("the file"+str(c.grv_conf_file)+
                                     " is not in the good format: it must be in "
                                     "format neemuds_<name>.conf or"
                                     " neemuds_<name>.ini")
                scale = g.groups(1)
                p = parse_params_conf_file(scale, PlanetParams,
                                       filepath=c.grv_conf_file)
                c.mineos_rhobar = p.rhobar
                c.mineos_nmin = p.nmin
                c.mineos_nmax = p.nmax
                c.mineos_lmin = p.lmin
                c.mineos_lmax = p.lmax
                # p.print_params()

        def parse_herrmann_config(c):
            if c.grv_conf_file not in [None, 'None']:
                # retrieve scale name in properly formatted filename (e.g.:
                    # neemuds_earth.conf, earth is the scale)
                g = match(r'.*_([^.]+)\..*', c.grv_conf_file)
                if g is None:
                    raise ValueError("the file"+str(c.grv_conf_file)+
                                     " is not in the good format: it must be in "
                                     "format neemuds_<name>.conf or"
                                     " neemuds_<name>.ini")
                scale = g.groups(1)
                p = parse_params_conf_file(scale, LocalParams,
                                       filepath=c.grv_conf_file)
                c.herrmann_fM = p.fM
                c.herrmann_fU = p.fU
                c.herrmann_fS = p.fS
                c.herrmann_f2 = p.f2
                c.herrmann_f3 = p.f3
                c.herrmann_ic = p.ic
                c.herrmann_h = p.h
                c.herrmann_f1 = p.f1
                c.herrmann_use_slu_disp96 = p.use_slu_disp96
                # p.print_params()

        @staticmethod
        def gen_earth_conf(filepath='neemuds_mcmc_earth.ini'):
            c = MCMCConfig()
            c.filepath = filepath
            c[c.CONF_SECTION_1] = {'profile_name': 'mcmc_earth_global'}
            c[c.CONF_SECTION_2] = {'scale_type': c.SCALE_GLOBAL_MINEOS}
            c[c.CONF_SECTION_3] = {'grv_conf_file':
                                 'neemuds_earth.conf'}
            c[c.CONF_SECTION_4] = {'ref_mod_file': '~/.ndata/prior/prem_noocean.txt'}
            c[c.CONF_SECTION_5] = {'prior_lo_file': '~/.ndata/prior/mod_earth_rayl_lo',
                                   'prior_hi_file': '~/.ndata/prior/mod_earth_rayl_hi'}
#        {'rayl_prior_lo_file':
#                             '~/.ndata/prior/mod_earth_rayl_lo',
#                             'rayl_prior_hi_file':
#                             '~/.ndata/prior/mod_earth_rayl_hi',
#                             'love_prior_lo_file':
#                             '~/.ndata/prior/mod_earth_love_lo',
#                             'love_prior_hi_file':
#                             '~/.ndata/prior/mod_earth_love_hi'}
            c[c.CONF_SECTION_6] = {'K_prior': None, 'MU_prior': None}
            c[c.CONF_SECTION_7] = {'chain_number': 4}
            c[c.CONF_SECTION_8] = {'chain_seeds': '855 435 678 835'}
            c[c.CONF_SECTION_9] = {'cold_n_iters': 300, 'hot_n_iters': 600}
            c[c.CONF_SECTION_10] = {'min_depth': 0, 'max_depth': 1500}
            c.h = \
            float(c[c.CONF_SECTION_10]['max_depth'])-float(c[c.CONF_SECTION_10]['min_depth'])
            c[c.CONF_SECTION_11] = {'last_bz3_min_depth': 1300}
            c[c.CONF_SECTION_12] = {'chain_bz3_numbers': 10}
            c[c.CONF_SECTION_13] = {'min_dist': 10}
            c[c.CONF_SECTION_14] = {'layer_thickness': .2}
            c[c.CONF_SECTION_15] = {'bz3_starting_radius': 5}
            c[c.CONF_SECTION_16] = {'bz3_radius_min': 75,
                                    'bz3_radius_max': 525}
            c[c.CONF_SECTION_17] = {'bz3_starting_angle': 22}
            c[c.CONF_SECTION_18] = {'bz3_angle_min': 2,
                                    'bz3_angle_max': 45}
            c[c.CONF_SECTION_19] = {'prem_join_vs': -1}
            c[c.CONF_SECTION_20] = {'prem_join_vp': -1}
            c[c.CONF_SECTION_21] = {'prem_join_rho': -1}
            c[c.CONF_SECTION_22] = {'prem_join_xi': 1}
            c[c.CONF_SECTION_23] = {'eta_prior_min': .95, 'eta_prior_max': 1.05}
            c[c.CONF_SECTION_24] = {'xi_prior_min': .9, 'xi_prior_max': 1.1}
            c[c.CONF_SECTION_25] = {}
            c[c.CONF_SECTION_26] = {'prior_vs2vp_coeffs': '1.6733200530'
                                  ' 1.9235384061', 'prior_vp2rho_coeffs':
                                  '.328 .3788', 'prior_rho_offsets': '252 768'}
            c[c.CONF_SECTION_27] = {'eprior_construct_method': 1}
            c[c.CONF_SECTION_28] = {'prior_triangle_angle': -10}
            c[c.CONF_SECTION_29] = {'eprior_triangle_gradients': '-0.0055555 0.1'}
            c[c.CONF_SECTION_30] = {'clamping_samples':
                                  c.CLAMPING_SAMPLES_INTO_EPRIORS}
            c[c.CONF_SECTION_31] = {'constraining_vp_rho_from_vs': 0}
            c[c.CONF_SECTION_32] = {
                'coldrun_vp_meth': 1,'coldrun_vs_meth': 2,'coldrun_rho_meth': 1,
                'coldrun_xi_meth': 1,'coldrun_eta_meth': 1,
                'hotrun_vp_meth': 1,'hotrun_vs_meth': 2,'hotrun_rho_meth': 1,
                'hotrun_xi_meth': 1,'hotrun_eta_meth': 1,
                'coldrun_depth_meth': 2, 'hotrun_depth_meth': 1,
                'coldrun_radius_meth': 1,
                'coldrun_phi_meth': 1,
                'hotrun_radius_meth': 1,
                'hotrun_phi_meth': 1,
                'coldrun_vp_const_sigma': 10,
                'coldrun_vs_const_sigma': 10,
                'coldrun_rho_const_sigma': 300,
                'coldrun_xi_const_sigma': .5,
                'coldrun_eta_const_sigma': .5,
                'coldrun_depth_const_sigma': 750,
                'coldrun_radius_const_sigma': 300,
                'coldrun_phi_const_sigma': 20,
                'hotrun_vp_const_sigma': .5,
                'hotrun_vs_const_sigma': .5,
                'hotrun_rho_const_sigma': 300,
                'hotrun_xi_const_sigma': .5,
                'hotrun_eta_const_sigma': .5,
                'hotrun_depth_const_sigma': 375,
                'hotrun_radius_const_sigma': 150,
                'hotrun_phi_const_sigma': 10,
                'coldrun_vp_wdiv': 4,
                'coldrun_vs_wdiv': 4,
                'coldrun_rho_wdiv': 4,
                'coldrun_xi_wdiv': 4,
                'coldrun_eta_wdiv': 4,
                'hotrun_vp_wdiv': 10,
                'hotrun_vs_wdiv': 10,
                'hotrun_rho_wdiv': 10,
                'hotrun_xi_wdiv': 10,
                'hotrun_eta_wdiv': 10,
                'coldrun_depth_wdiv': 1,
                'hotrun_depth_wdiv': 2,
                'coldrun_radius_wdiv': 4,
                'coldrun_phi_wdiv': 1.4,
                'hotrun_radius_wdiv': 10,
                'hotrun_phi_wdiv': 2.4
            } #TODO
            c[c.CONF_SECTION_33] = {'output_flush_iter_period': 10}
            c[c.CONF_SECTION_34] = {'outputting_sampled_models': 1}
            c[c.CONF_SECTION_35] = {'accepting_all_models': 0}
            c[c.CONF_SECTION_36] = {'hotrun_alpha': 10, 'hotrun_beta': 15,
                                  'hotrun_gamma': 5}
            c[c.CONF_SECTION_37] = {'using_hotrun_param_custom_probas': 1,
                                  'hotrun_param_choice_custom_prob_law': '.3'
                                  ' .6 .1 0 0'}
            c[c.CONF_SECTION_38] = {'gof_calc_method': c.GOF_CALC_METH_DISCRETE}
            c[c.CONF_SECTION_39] = {'phi_radius_prior_relation':
                                  c.PHI_RADIUS_PRIOR_RELATIONSHIP_LINEAR1}
            c[c.CONF_SECTION_40] = {'enabling_VP_over_VS_model': 0}
            with open(filepath, 'w') as configfile:
                c.write(configfile)


        @staticmethod
        def gen_mars_conf(filepath="neemuds_mcmc_mars.ini"):
            c = MCMCConfig()
            c.filepath = filepath
            c[c.CONF_SECTION_1] = {'profile_name': 'mcmc_mars_global'}
            c[c.CONF_SECTION_2] = {'scale_type': c.SCALE_GLOBAL_MINEOS}
            c[c.CONF_SECTION_3] = {'grv_conf_file':
                                 'neemuds_mars.conf'}
            c[c.CONF_SECTION_4] = {'ref_mod_file': '~/.ndata/prior/mars/DWThot.tvel'}
            c[c.CONF_SECTION_5] = {'prior_lo_file': '~/.ndata/prior/mod_mars_rayl_lo',
                                   'prior_hi_file': '~/.ndata/prior/mod_mars_rayl_hi'}
#            c[c.CONF_SECTION_5] = {'rayl_prior_lo_file':
#                                 '~/.ndata/prior/mod_mars_rayl_lo',
#                                 'rayl_prior_hi_file':
#                                 '~/.ndata/prior/mod_mars_rayl_hi',
#                                 'love_prior_lo_file':
#                                 '~/.ndata/prior/mod_mars_love_lo',
#                                 'love_prior_hi_file':
#                                 '~/.ndata/prior/mod_mars_love_hi'}
            c[c.CONF_SECTION_6] = {'K_prior': None, 'MU_prior': None}
            c[c.CONF_SECTION_7] = {'chain_number': 10}
            c[c.CONF_SECTION_8] = {'chain_seeds': -1}
            c[c.CONF_SECTION_9] = {'cold_n_iters': 1500, 'hot_n_iters': 10000}
            c[c.CONF_SECTION_10] = {'min_depth': 0, 'max_depth': 500}
            c.h = \
            float(c[c.CONF_SECTION_10]['max_depth'])-float(c[c.CONF_SECTION_10]['min_depth'])
            c[c.CONF_SECTION_11] = {'last_bz3_min_depth': 300}
            c[c.CONF_SECTION_12] = {'chain_bz3_numbers': 10}
            c[c.CONF_SECTION_13] = {'min_dist': 4}
            c[c.CONF_SECTION_14] = {'layer_thickness': 4}
            c[c.CONF_SECTION_15] = {'bz3_starting_radius': 3}
            c[c.CONF_SECTION_16] = {'bz3_radius_min': 7.5,                                  'bz3_radius_max': 20}
            c[c.CONF_SECTION_17] = {'bz3_starting_angle': 15}
            c[c.CONF_SECTION_18] = {'bz3_angle_min': 2.5,
                                  'bz3_angle_max': 25}
            c[c.CONF_SECTION_19] = {'prem_join_vs': -1}
            c[c.CONF_SECTION_20] = {'prem_join_vp': -1}
            c[c.CONF_SECTION_21] = {'prem_join_rho': -1}
            c[c.CONF_SECTION_22] = {'prem_join_xi': 1}
            c[c.CONF_SECTION_23] = {'eta_prior_min': .95, 'eta_prior_max': 1.05}
            c[c.CONF_SECTION_24] = {'xi_prior_min': .9, 'xi_prior_max': 1.1}
            c[c.CONF_SECTION_25] = {'slope_reg': None}
            c[c.CONF_SECTION_26] = {'prior_vs2vp_coeffs': '1.6733200530 '
                                    '1.816590212', 'prior_vp2rho_coeffs':
                                  '.328 .3788', 'prior_rho_offsets': '252 768'}
            c[c.CONF_SECTION_27] = {'eprior_construct_method': 5}
            c[c.CONF_SECTION_28] = {'prior_triangle_angle': -.1}
            c[c.CONF_SECTION_29] = {'eprior_triangle_gradients': '5 20'}
            c[c.CONF_SECTION_30] = {'clamping_samples':
                                  c.CLAMPING_SAMPLES_INTO_PRIORS}
            c[c.CONF_SECTION_31] = {'constraining_vp_rho_from_vs': 0}
            c[c.CONF_SECTION_32] = {
                'coldrun_vp_meth': 2,'coldrun_vs_meth': 2,'coldrun_rho_meth': 2,
                'coldrun_xi_meth': 2,'coldrun_eta_meth': 2,
                'hotrun_vp_meth': 2,'hotrun_vs_meth': 2,'hotrun_rho_meth': 2,
                'hotrun_xi_meth': 2,'hotrun_eta_meth': 2,
                'coldrun_depth_meth': 2, 'hotrun_depth_meth': 2,
                'coldrun_radius_meth': 2,
                'coldrun_phi_meth': 2,
                'hotrun_radius_meth': 2,
                'hotrun_phi_meth': 2,
                'coldrun_vp_const_sigma': 10,
                'coldrun_vs_const_sigma': 10,
                'coldrun_rho_const_sigma': 300,
                'coldrun_xi_const_sigma': .5,
                'coldrun_eta_const_sigma': .5,
                'coldrun_depth_const_sigma': 750,
                'coldrun_radius_const_sigma': 300,
                'coldrun_phi_const_sigma': 20,
                'hotrun_vp_const_sigma': .5,
                'hotrun_vs_const_sigma': .5,
                'hotrun_rho_const_sigma': 300,
                'hotrun_xi_const_sigma': .5,
                'hotrun_eta_const_sigma': .5,
                'hotrun_depth_const_sigma': 375,
                'hotrun_radius_const_sigma': 300,
                'hotrun_phi_const_sigma': 20,
                'coldrun_vp_wdiv': 4,
                'coldrun_vs_wdiv': 4,
                'coldrun_rho_wdiv': 4,
                'coldrun_xi_wdiv': 4,
                'coldrun_eta_wdiv': 4,
                'hotrun_vp_wdiv': 10,
                'hotrun_vs_wdiv': 10,
                'hotrun_rho_wdiv': 10,
                'hotrun_xi_wdiv': 10,
                'hotrun_eta_wdiv': 10,
                'coldrun_radius_wdiv': 4,
                'coldrun_phi_wdiv': 1.4,
                'hotrun_radius_wdiv': 10,
                'hotrun_phi_wdiv': 2.4
            }
            c[c.CONF_SECTION_33] = {'output_flush_iter_period': 10}
            c[c.CONF_SECTION_34] = {'outputting_sampled_models': 1}
            c[c.CONF_SECTION_35] = {'accepting_all_models': 0}
            c[c.CONF_SECTION_36] = {'hotrun_alpha': 20, 'hotrun_beta': 15,
                                  'hotrun_gamma': 5}
            c[c.CONF_SECTION_37] = {'using_hotrun_param_custom_probas': 1,
                                  'hotrun_param_choice_custom_prob_law': '.3'
                                  ' .85 .05 0 0'}
            c[c.CONF_SECTION_38] = {'gof_calc_method': c.GOF_CALC_METH_DISCRETE}
            c[c.CONF_SECTION_39] = {'phi_radius_prior_relation':
                                  c.PHI_RADIUS_PRIOR_RELATIONSHIP_LINEAR1}
            c[c.CONF_SECTION_40] = {'enabling_VP_over_VS_model': 0}
            with open(filepath, 'w') as configfile:
                c.write(configfile)

        @staticmethod
        def gen_local_conf(filepath="neemuds_mcmc_local.ini"):
            c = MCMCConfig()
            c.filepath = filepath
            c[c.CONF_SECTION_1] = {'profile_name': 'mcmc_local'}
            c[c.CONF_SECTION_2] = {'scale_type': c.SCALE_LOCAL_HERRMANN}
            c[c.CONF_SECTION_3] = {'grv_conf_file':
                                 'neemuds_local.conf'}
            c[c.CONF_SECTION_4] = {'ref_mod_file': 'None'}
            c[c.CONF_SECTION_5] = {'prior_lo_file': '~/.ndata/prior/mod_loc_lo',
                                   'prior_hi_file': '~/.ndata/prior/mod_loc_hi'}
#            c[c.CONF_SECTION_5] = {'rayl_prior_lo_file':
#                                 '~/.ndata/prior/mod_loc_lo',
#                                 'rayl_prior_hi_file':
#                                 '~/.ndata/prior/mod_loc_hi',
#                                 'love_prior_lo_file':
#                                 '~/.ndata/prior/mod_loc_lo',
#                                 'love_prior_hi_file':
#                                 '~/.ndata/prior/mod_loc_hi'}
            c[c.CONF_SECTION_6] = {'K_prior': None, 'MU_prior': None}
            c[c.CONF_SECTION_7] = {'chain_number': 4}
            c[c.CONF_SECTION_8] = {'chain_seeds': '855 435 678 835'}
            c[c.CONF_SECTION_9] = {'cold_n_iters': 10000, 'hot_n_iters': 30000}
            c[c.CONF_SECTION_10] = {'min_depth': 0, 'max_depth': 192}
            c.h = \
            float(c[c.CONF_SECTION_10]['max_depth'])-float(c[c.CONF_SECTION_10]['min_depth'])
            c[c.CONF_SECTION_11] = {'last_bz3_min_depth': 100}
            c[c.CONF_SECTION_12] = {'chain_bz3_numbers': 4}
            c[c.CONF_SECTION_13] = {'min_dist': 10}
            c[c.CONF_SECTION_14] = {'layer_thickness': 2}
            c[c.CONF_SECTION_15] = {'bz3_starting_radius': 5}
            c[c.CONF_SECTION_16] = {'bz3_radius_min': 9.6,
                                    'bz3_radius_max': 67.2}
            c[c.CONF_SECTION_17] = {'bz3_starting_angle': 22}
            c[c.CONF_SECTION_18] = {'bz3_angle_min': 2,
                                    'bz3_angle_max': 45}
            c[c.CONF_SECTION_19] = {'prem_join_vs': 4400}
            c[c.CONF_SECTION_20] = {'prem_join_vp': 7621}
            c[c.CONF_SECTION_21] = {'prem_join_rho': 4500}
            c[c.CONF_SECTION_22] = {'prem_join_xi': 1}
            c[c.CONF_SECTION_23] = {'eta_prior_min': -1, 'eta_prior_max': -1}
            c[c.CONF_SECTION_24] = {'xi_prior_min': .9, 'xi_prior_max': 1.1}
            c[c.CONF_SECTION_25] = {'slope_reg': None}
            c[c.CONF_SECTION_26] = {'prior_vs2vp_coeffs': '1.6733200530'
                                    ' 1.9235384061', 'prior_vp2rho_coeffs':
                                    '.328 .3788', 'prior_rho_offsets': '252 768'}
            c[c.CONF_SECTION_27] = {'eprior_construct_method': 5}
            c[c.CONF_SECTION_28] = {'prior_triangle_angle': -10}
            c[c.CONF_SECTION_29] = {'eprior_triangle_gradients': '-0.0055555 0.1'}
            c[c.CONF_SECTION_30] = {'clamping_samples':
                                  c.CLAMPING_SAMPLES_INTO_EPRIORS}
            c[c.CONF_SECTION_31] = {'constraining_vp_rho_from_vs': 0}
            c[c.CONF_SECTION_32] = {
                'coldrun_vp_meth': 2,'coldrun_vs_meth': 2,'coldrun_rho_meth': 2,
                'coldrun_xi_meth': 2,'coldrun_eta_meth': 2,
                'hotrun_vp_meth': 2,'hotrun_vs_meth': 2,'hotrun_rho_meth': 2,
                'hotrun_xi_meth': 2,'hotrun_eta_meth': 2,
                'coldrun_depth_meth': 2, 'hotrun_depth_meth': 2,
                'coldrun_radius_meth': 2,
                'coldrun_phi_meth': 2,
                'hotrun_radius_meth': 2,
                'hotrun_phi_meth': 2,
                'coldrun_vp_const_sigma': 10000,
                'coldrun_vs_const_sigma': 10000,
                'coldrun_rho_const_sigma': 300,
                'coldrun_xi_const_sigma': .5,
                'coldrun_eta_const_sigma': .5,
                'hotrun_vp_const_sigma': 500,
                'hotrun_vs_const_sigma': 500,
                'hotrun_rho_const_sigma': 300,
                'hotrun_xi_const_sigma': .5,
                'hotrun_eta_const_sigma': .5,
                'coldrun_depth_const_sigma': 750,
                'hotrun_depth_const_sigma': 375,
                'coldrun_radius_const_sigma': 300,
                'coldrun_phi_const_sigma': 20,
                'hotrun_radius_const_sigma': 150,
                'hotrun_phi_const_sigma': 10,
                'coldrun_vp_wdiv': 4,
                'coldrun_vs_wdiv': 4,
                'coldrun_rho_wdiv': 4,
                'coldrun_xi_wdiv': 4,
                'coldrun_eta_wdiv': 4,
                'hotrun_vp_wdiv': 10,
                'hotrun_vs_wdiv': 10,
                'hotrun_rho_wdiv': 10,
                'hotrun_xi_wdiv': 10,
                'hotrun_eta_wdiv': 10,
                'coldrun_depth_wdiv': 1,
                'hotrun_depth_wdiv': 2,
                'coldrun_radius_wdiv': 4,
                'coldrun_phi_wdiv': 1.4,
                'hotrun_radius_wdiv': 10,
                'hotrun_phi_wdiv': 2.4
            } #TODO
            c[c.CONF_SECTION_33] = {'output_flush_iter_period': 10}
            c[c.CONF_SECTION_34] = {'outputting_sampled_models': 1}
            c[c.CONF_SECTION_35] = {'accepting_all_models': 0}
            c[c.CONF_SECTION_36] = {'hotrun_alpha': 10, 'hotrun_beta': 15,
                                  'hotrun_gamma': 5}
            c[c.CONF_SECTION_37] = {'using_hotrun_param_custom_probas': 1,
                                  'hotrun_param_choice_custom_prob_law': '.3'
                                  ' .6 .1 0 0'}
            c[c.CONF_SECTION_38] = {'gof_calc_method': c.GOF_CALC_METH_DISCRETE}
            c[c.CONF_SECTION_39] = {'phi_radius_prior_relation':
                                  c.PHI_RADIUS_PRIOR_RELATIONSHIP_LINEAR1}
            c[c.CONF_SECTION_40] = {'enabling_VP_over_VS_model': 1}
            with open(filepath, 'w') as configfile:
                c.write(configfile)
