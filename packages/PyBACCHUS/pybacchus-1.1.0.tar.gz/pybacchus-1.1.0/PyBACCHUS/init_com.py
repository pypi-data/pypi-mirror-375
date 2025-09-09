import numpy as np
import pandas as pd

from PyBACCHUS.helper_methods import *

class Init(object):
    def __init__(self,path):
        self.path = path
        self.read()
        # with open(self.path) as file:
        #     self.lines = file.readlines()
        #     self.original = file.readlines()
        # file.close()

        self.turbo_idx = get_linenumber(self.lines, 'turbo_path')
        self.turbo_path = get_existing_state(self.turbo_idx,self.lines)

        self.util_idx = get_linenumber(self.lines, 'util_path')
        self.util_path = get_existing_state(self.util_idx,self.lines)

        self.interpol_idx = get_linenumber(self.lines, 'interpol_path')
        self.interpol_path = get_existing_state(self.interpol_idx,self.lines)

        self.dotsm_idx = get_linenumber(self.lines, 'dotsm')
        self.dotsm = get_existing_state(self.dotsm_idx,self.lines)

        self.solabufile_idx = get_linenumber(self.lines, 'solabufile')
        self.solabufile = get_existing_state(self.solabufile_idx,self.lines)

        self.wavereffile_idx = get_linenumber(self.lines, 'wavereffile')
        self.wavereffile = get_existing_state(self.wavereffile_idx,self.lines)

        self.linelist_idx = get_linenumber(self.lines, 'linelist_ref')
        self.linelist_ref = get_existing_state(self.linelist_idx,self.lines)

        self.profile_conv_idx = get_linenumber(self.lines, 'profile_conv')
        self.profile_conv = int(get_existing_state(self.profile_conv_idx,self.lines))

        self.convol_inst_idx = get_linenumber(self.lines, 'convol_inst')
        self.convol_inst = float(get_existing_state(self.convol_inst_idx,self.lines))
        
        self.MARCSFILE_idx = get_linenumber(self.lines, 'MARCSFILE')
        self.MARCSFILE = get_existing_state(self.MARCSFILE_idx,self.lines)

        self.SPH_idx = get_linenumber(self.lines, 'SPH')
        self.SPH = get_existing_state(self.SPH_idx,self.lines)

        self.diff_star_idx = get_linenumber(self.lines, 'diff_star')
        self.diff_star = get_existing_state(self.diff_star_idx,self.lines)   

        self.diff_star_offset_idx = get_linenumber(self.lines, 'diff_star_offset')
        self.diff_star_offset = get_existing_state(self.diff_star_offset_idx,self.lines) 

        self.eqw_rej_idx = get_linenumber(self.lines, 'eqw_rej')
        self.eqw_rej = get_existing_state(self.eqw_rej_idx,self.lines) 

        #####

        self.ncpu_idx = get_linenumber(self.lines, 'ncpu')
        self.ncpu = int(get_existing_state(self.ncpu_idx,self.lines)) 

        self.compute_idx = get_linenumber(self.lines, 'compute')
        self.compute = int(get_existing_state(self.compute_idx,self.lines)) 

        self.reset_idx = get_linenumber(self.lines, 'reset')
        self.reset = int(get_existing_state(self.reset_idx,self.lines)) 

        self.manual_idx = get_linenumber(self.lines, 'manual')
        self.manual = int(get_existing_state(self.manual_idx,self.lines)) 

        self.nonorm_idx = get_linenumber(self.lines, 'nonorm')
        self.nonorm = int(get_existing_state(self.nonorm_idx,self.lines)) 

        self.cleanup_idx = get_linenumber(self.lines, 'cleanup')
        self.cleanup = int(get_existing_state(self.cleanup_idx,self.lines)) 

        self.debug_idx = get_linenumber(self.lines, 'debug')
        self.debug = int(get_existing_state(self.debug_idx,self.lines)) 

        #####

        self.alllines_list_idx = get_linenumber(self.lines, 'alllines_list')
        self.alllines_list = int(get_existing_state(self.alllines_list_idx,self.lines)) 

        self.TEFFunknown_idx = get_linenumber(self.lines, 'TEFFunknown')
        self.TEFFunknown = int(get_existing_state(self.TEFFunknown_idx,self.lines)) 

        self.LOGGunknown_idx = get_linenumber(self.lines, 'LOGGunknown')
        self.LOGGunknown = int(get_existing_state(self.LOGGunknown_idx,self.lines)) 

        self.METALLICunknown_idx = get_linenumber(self.lines, 'METALLICunknown')
        self.METALLICunknown = int(get_existing_state(self.METALLICunknown_idx,self.lines))

        self.TURBVELunknown_idx = get_linenumber(self.lines, 'TURBVELunknown')
        self.TURBVELunknown = int(get_existing_state(self.TURBVELunknown_idx,self.lines))

        self.CONVOLunknown_idx = get_linenumber(self.lines, 'CONVOLunknown')
        self.CONVOLunknown = int(get_existing_state(self.CONVOLunknown_idx,self.lines))

        self.updateabu_idx = get_linenumber(self.lines, 'updateabu')
        self.updateabu = int(get_existing_state(self.updateabu_idx,self.lines))

    ###### updating methods ######
    def set_turbo_path(self, turbopath):

        self.turbo_path = turbopath
        newline = 'set turbo_path = "{}"\n'.format(turbopath)
        self.edit(self.turbo_idx, newline)
        # self.lines = edit_line(self.lines,self.turbo_idx, newline)
        # update_line(self.lines, self.path)

    def set_util_path(self, utilpath):

        self.util_path = utilpath
        newline = 'set util_path = "{}"\n'.format(utilpath)
        self.edit(self.util_idx, newline)
        # self.lines = edit_line(self.lines,self.util_idx, newline)
        # update_line(self.lines, self.path)

    def set_interpol_path(self, interpolpath):

        self.interpol_path = interpolpath
        newline = 'set interpol_path = "{}"\n'.format(interpolpath)
        self.edit(self.interpol_idx, newline)
        # self.lines = edit_line(self.lines,self.interpol_idx, newline)
        # update_line(self.lines, self.path)

    def set_solarabu_file(self, solarabu_file):
        
        self.solabufile = solarabu_file
        newline = 'set solabufile = "{}"\n'.format(solarabu_file)
        self.edit(self.solabufile_idx, newline)
        # self.lines = edit_line(self.lines,self.solabufile_idx, newline)
        # update_line(self.lines, self.path)

    def set_waveref_file(self, waveref_file):

        self.wavereffile = waveref_file
        newline = 'set wavereffile = "{}"\n'.format(waveref_file)
        self.edit(self.wavereffile_idx, newline)
        # self.lines = edit_line(self.lines,self.wavereffile_idx, newline)
        # update_line(self.lines, self.path)

    def set_linelist(self, linelist):

        self.linelist_ref = linelist
        newline = 'set linelist_ref = "{}"\n'.format(linelist)
        self.edit(self.linelist_idx, newline)
        # self.lines = edit_line(self.lines,self.linelist_idx, newline)
        # update_line(self.lines, self.path)

    def set_convolution_profile(self, conv_profile):

        self.profile_conv = conv_profile
        newline = "set profile_conv = '{}'\n".format(conv_profile)
        self.edit(self.profile_conv_idx, newline)
        # self.lines = edit_line(self.lines,self.profile_conv_idx, newline)
        # update_line(self.lines, self.path)

    def set_convolution_floor(self, floor):

        self.convol_inst = floor
        newline = 'set convol_inst = {}\n'.format(floor)
        self.edit(self.convol_inst_idx, newline)
        # self.lines = edit_line(self.lines,self.convol_inst_idx, newline)
        # update_line(self.lines, self.path)

    def set_marcsfile(self, mformat):

        self.convol_inst = mformat
        newline = 'set MARCSFILE = {}\n'.format(mformat)
        self.edit(self.MARCSFILE_idx, newline)
        # self.lines = edit_line(self.lines,self.MARCSFILE_idx, newline)
        # update_line(self.lines, self.path)

    def set_SPH(self, geometry):

        self.SPH = geometry
        newline = 'set SPH = {}\n'.format(geometry)
        self.edit(self.SPH_idx, newline)
        # self.lines = edit_line(self.lines,self.SPH_idx, newline)
        # update_line(self.lines, self.path)

    # #### DIFFERENTIAL ABUNDANCES ####

    def set_differential_star_name(self, diff_star_name):

        self.diff_star = diff_star_name
        newline = "set diff_star = '{}'\n".format(diff_star_name)
        self.edit(self.diff_star_idx, newline)
        # self.lines = edit_line(self.lines,self.diff_star_idx, newline)
        # update_line(self.lines, self.path)

    def set_diff_offset(self, offset):

        self.diff_star_offset = offset
        newline = "set diff_star_offset = '{}'\n".format(offset)
        self.edit(self.diff_star_offset_idx, newline)
        # self.lines = edit_line(self.lines,self.diff_star_offset_idx, newline)
        # update_line(self.lines, self.path)

    def set_eqw_rejection_limit(self, limit):

        self.eqw_rej = limit
        newline = 'set eqw_rej = "{}"\n'.format(limit)
        self.edit(self.eqw_rej_idx, newline)
        # self.lines = edit_line(self.lines,self.eqw_rej_idx, newline)
        # update_line(self.lines, self.path)

    # #### COMPUTE PARAMETERS ####

    def set_ncpu(self, n_cpu):
        
        self.ncpu = n_cpu
        newline = 'set ncpu = {}\n'.format(n_cpu)
        self.edit(self.ncpu_idx, newline)
        # self.lines = edit_line(self.lines,self.ncpu_idx, newline)
        # update_line(self.lines, self.path)

    def set_compute(self, _compute):

        self.compute = _compute
        newline = 'set compute = "{}"\n'.format(_compute)
        self.edit(self.compute_idx, newline)
        # self.lines = edit_line(self.lines,self.compute_idx, newline)
        # update_line(self.lines, self.path)

    def set_reset(self, _reset):

        self.reset = _reset
        newline = 'set reset = "{}"\n'.format(_reset)
        self.edit(self.reset_idx, newline)
        # self.lines = edit_line(self.lines,self.reset_idx, newline)
        # update_line(self.lines, self.path)
        
    def set_manual(self, _manual):

        self.reset = _manual
        newline = 'set manual = "{}"\n'.format(_manual)
        self.edit(self.manual_idx, newline)
        # self.lines = edit_line(self.lines,self.manual_idx, newline)
        # update_line(self.lines, self.path)

    def set_nonorm(self, _nonorm):

        self.reset = _nonorm
        newline = 'set nonorm = "{}"\n'.format(_nonorm)
        self.edit(self.nonorm_idx, newline)
        # self.lines = edit_line(self.lines,self.nonorm_idx, newline)
        # update_line(self.lines, self.path)

    def set_cleanup(self, _cleanup):

        self.cleanup = _cleanup
        newline = 'set cleanup = "{}"\n'.format(_cleanup)
        self.edit(self.cleanup_idx, newline)
        # self.lines = edit_line(self.lines,self.cleanup_idx, newline)
        # update_line(self.lines, self.path)

    def set_debug(self, _debug):

        self.debug = _debug
        newline = 'set debug = "{}"\n'.format(_debug)
        self.edit(self.debug_idx, newline)
        # self.lines = edit_line(self.lines,self.debug_idx, newline)
        # update_line(self.lines, self.path)

    # #### STELLAR PARAMETERS ####

    def set_alllines_list(self, _alllines):
        
        self.alllines_list = _alllines
        newline = 'set alllines_list = "{}"\n'.format(_alllines)
        self.edit(self.alllines_list_idx, newline)
        # self.lines = edit_line(self.lines,self.alllines_list_idx, newline)
        # update_line(self.lines, self.path)

    def set_TEFFunknown(self, teff):
        
        self.TEFFunknown = teff
        newline = 'set TEFFunknown = "{}"\n'.format(teff)
        self.edit(self.TEFFunknown_idx, newline)
        # self.lines = edit_line(self.lines,self.TEFFunknown_idx, newline)
        # update_line(self.lines, self.path)

    def set_LOGGunknown(self, logg):
        
        self.LOGGunknown = logg
        newline = 'set LOGGunknown = "{}"\n'.format(logg)
        self.edit(self.LOGGunknown_idx, newline)
        # self.lines = edit_line(self.lines,self.LOGGunknown_idx, newline)
        # update_line(self.lines, self.path)

    def set_METALLICunknown(self, met):
        
        self.METALLICunknown = met
        newline = 'set METALLICunknown = "{}"\n'.format(met)
        self.edit(self.METALLICunknown_idx, newline)
        # self.lines = edit_line(self.lines,self.METALLICunknown_idx, newline)
        # update_line(self.lines, self.path)

    def set_TURBOVELunknown(self, vmicro):
        
        self.TURBOVELunknown = vmicro
        newline = 'set TURBOVELunknown = "{}"\n'.format(vmicro)
        self.edit(self.TURBVELunknown_idx, newline)
        # self.lines = edit_line(self.lines,self.TURBVELunknown_idx, newline)
        # update_line(self.lines, self.path)

    def set_CONVOLunknown(self, conv):
        
        self.CONVOLunknown = conv
        newline = 'set CONVOLunknown = "{}"\n'.format(conv)
        self.edit(self.CONVOLunknown_idx, newline)
        # self.lines = edit_line(self.lines,self.CONVOLunknown_idx, newline)
        # update_line(self.lines, self.path)

    def set_updateabu(self, abu):
        
        self.LOGGunknown = abu
        newline = 'set updateabu = "{}"\n'.format(abu)
        self.edit(self.updateabu_idx, newline)
        # self.lines = edit_line(self.lines,self.updateabu_idx, newline)
        # update_line(self.lines, self.path)

    ######

    def show(self):
        for n, i in enumerate(self.lines):
            print('{}, {}'.format(n, i))
            
    def read(self):
        with open(self.path) as file:
            self.lines = file.readlines()
        file.close()
        
    def write(self,newfile=False, newfilename=''):
        if newfile==True:
            with open(newfilename, "w") as file:
                file.writelines(self.lines)
            file.close()
        else:
            with open(self.path, "w") as file:
                file.writelines(self.lines)
            file.close()  

    def edit(self, line_number, text):
        new_lines = []
        for count,i in enumerate(self.lines):
            if count != line_number:
                self.lines[count] = i
            else:
                self.lines[count] = text

    def add_line(self, line2add, line_num = -1):
        if line_num == -1:
            self.lines = np.insert(self.lines,len(self.lines), line2add)
        else:
            self.lines = np.insert(self.lines,line_num, line2add)
                    
    def add_lines(self, lines2add, linenumbers = []):
        if linenumbers != []:
            for count, i in enumerate(lines2add):
                self.add_line(i, linenumbers[count])
        else:
            for count, i in enumerate(lines2add):
                self.add_line(i)

    def remove_lines(self, lines2remove):
        truth = np.isin(self.lines,lines2remove)
        self.lines = np.array(self.lines)[truth==False]

    