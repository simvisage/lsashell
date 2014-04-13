'''
Created on 13. 4. 2014

@author: Vancikv
'''

import os

import numpy as np

from lsashell.load_case_reader.load_case_reader import \
    LCReader

class LCReaderRFEM(LCReader):

    def read_state_data(self, f_name):

        '''to read the stb-stress resultants save the xls-worksheet
        to a csv-file using ';' as filed delimiter and ' ' (blank)
        as text delimiter.
        '''

        file_name = os.path.join(self.data_dir, f_name)

        print '*** read state data from file: %s ***' % (file_name)

        # get the column headings defined in the second row 
        # of the csv soliciotations input file
        # column_headings = np.array(["Nr.","Punkt","X","Y","Z","mx","my","mxy","vx","vy","nx","ny","nxy"])
        #
        file_ = open(file_name, 'r')
        lines = file_.readlines()
        column_headings = lines[1].split(';')
        # remove '\n' from last string element in list
        #
        column_headings[-1] = column_headings[-1][:-1]
        column_headings_arr = np.array(column_headings)

        elem_no_idx = np.where('Nr.' == column_headings_arr)[0]
        X_idx = np.where('X' == column_headings_arr)[0]
        Y_idx = np.where('Y' == column_headings_arr)[0]
        Z_idx = np.where('Z' == column_headings_arr)[0]
        mx_idx = np.where('mx' == column_headings_arr)[0]
        my_idx = np.where('my' == column_headings_arr)[0]
        mxy_idx = np.where('mxy' == column_headings_arr)[0]
        nx_idx = np.where('nx' == column_headings_arr)[0]
        ny_idx = np.where('ny' == column_headings_arr)[0]
        nxy_idx = np.where('nxy' == column_headings_arr)[0]

        file_.close()

        # define np.arrays containing the information from the raw input file
        #
        input_arr = np.loadtxt(file_name , delimiter = ';', skiprows = 2)

        # element number:
        #
        elem_no = input_arr[:, elem_no_idx]

        # coordinates [m]:
        #
        X = input_arr[:, X_idx]
        Y = input_arr[:, Y_idx]
        Z = input_arr[:, Z_idx]

        # moments [kNm/m]
        #
        mx = input_arr[:, mx_idx]
        my = input_arr[:, my_idx]
        mxy = input_arr[:, mxy_idx]

        # normal forces [kN/m]:
        #
        nx = input_arr[:, nx_idx]
        ny = input_arr[:, ny_idx]
        nxy = input_arr[:, nxy_idx]

        return { 'elem_no' : elem_no, 'X' : X, 'Y' : Y, 'Z' : Z,
                 'mx' : mx, 'my' : my, 'mxy' : mxy,
                 'nx' : nx, 'ny' : ny, 'nxy' : nxy,
               }

    # stress resultants to be multiplied within the LCC combinations
    #
    sr_columns = ['mx', 'my', 'mxy', 'nx', 'ny', 'nxy']

    def read_geo_data(self, file_name):
        '''to read the stb - thickness save the xls - worksheet
        to a csv - file using ';' as filed delimiter and ' ' ( blank )
        as text delimiter.
        '''
        print '*** read geo data from file: %s ***' % (file_name)


        # coordinates [m]:
        # (NOTE: corrds are taken from the state data file of the first loading case) 

        # the column headings are defined in the first/second row 
        # of the csv thickness input file
        # Flaeche;;;Material;Dicke;;Exzentrizitaet;Integrierte Objekte;;;

        # (NOTE: the headings contain non-ascii characters. Therefore the
        #       column indices can not be derived using the 'np.where'-method.)

        # read the float data:
        #
        input_arr = np.loadtxt(file_name, usecols = (0, 5), delimiter = ';', skiprows = 2)
        elem_no_idx = 0
        thickness_idx = 1

        # element number:
        # (NOTE: column np.array must be of shape (n_elems, 1)
        #
        elem_no = input_arr[:, elem_no_idx][:, None]

        # element thickness [mm]:
        # (NOTE: column np.array must be of shape (n_elems, 1)
        #
        thickness = input_arr[:, thickness_idx][:, None]
        
        # convert thickness to [m]
        thickness = thickness / 1000.

        # coordinates [m]:
        # (NOTE: corrds are taken from the state data file of the first loading case) 
        #
        X = self.lcc_table.lc_list[0].state_data_orig['X']
        Y = self.lcc_table.lc_list[0].state_data_orig['Y']
        Z = self.lcc_table.lc_list[0].state_data_orig['Z']

        return  {'elem_no':elem_no,
                 'X':X, 'Y':Y, 'Z':Z,
                 'thickness':thickness }

    def plot_col(self, mlab, plot_col, geo_data, state_data, warp_factor = 1.):
        '''
        plot the chosen plot_col array at the center of gravity of the elements;
        method is used by 'ls_table' to plot the selected plot variable
        NOTE: if RFEM-Reader is used no values for the deformed state are read in yet
        '''
        gd = geo_data

        # element coordinates of the undeformed shape 
        # (2d column arrays)
        #
        X = gd['X'].flatten()
        Y = gd['Y'].flatten()
        # switch orientation of the z-axis
        Z = (-1.0) * gd['Z'].flatten()

        # plot state data in the deformed geometry  
        #
        mlab.points3d(X, Y, Z, plot_col,
                           colormap = "YlOrBr",
                           mode = "cube",
                           scale_mode = 'none',
                           scale_factor = 0.15)


    def check_for_consistency(self, lc_list, geo_data_dict):

        for lc in lc_list:
            # check internal LC-consitency: 
            # (compare coords-values of first LC with all other LC's in 'lc_list')
            #
            if not all(lc_list[0].state_data_dict['X'] == lc.state_data_dict['X']) and \
                not all(lc_list[0].state_data_dict['Y'] == lc.state_data_dict['Y']) and \
                not all(lc_list[0].state_data_dict['Z'] == lc.state_data_dict['Z']):
                raise ValueError, "coordinates in loading case '%s' and loading case '%s' are not identical. Check input files for consistency!" \
                        % (self.lc_list[0].name, lc.name)
                return False

            # check external consistency:
            # (compare 'elem_no' in 'thickness.csv' and in all loading-cases 
            # input files (e.g. 'LC1.csv') defined in 'lc_list')
            #
            if not all(geo_data_dict['elem_no'] == lc.state_data_dict['elem_no']):
                raise ValueError, "element numbers in loading case '%s' and loading case '%s' are not identical. Check input files for consistency!" \
                        % (lc_list[0].name, lc.name)
                return False

        print '*** input files checked for consistency (OK) ***'
        return True
