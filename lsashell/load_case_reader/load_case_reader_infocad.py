'''
Created on 13. 4. 2014

@author: Vancikv
'''

from tvtk.api import tvtk

import os

import numpy as np

from StringIO import StringIO

from lsashell.load_case_reader.load_case_reader import \
    LCReader

class LCReaderInfoCAD(LCReader):

    def read_state_data(self, f_name):

        file_name = os.path.join(self.data_dir, 'state_data',
                                 'Flaechenschnittgroessen',
                                 'Schwerpunkt', f_name)

        print '*** read state data from file: %s ***' % (file_name)

        input_arr = np.loadtxt(file_name)

        elem_no_idx, nx_idx, ny_idx, nxy_idx, mx_idx, my_idx, mxy_idx = range(0, 7)

        # element number:
        #
        elem_no = input_arr[:, [elem_no_idx]]

        # moments [kNm/m]
        #
        mx = input_arr[:, [mx_idx]]
        my = input_arr[:, [my_idx]]
        mxy = input_arr[:, [mxy_idx]]

        # normal forces [kN/m]:
        #
        nx = input_arr[:, [nx_idx]]
        ny = input_arr[:, [ny_idx]]
        nxy = input_arr[:, [nxy_idx]]

        file_name = os.path.join(self.data_dir, 'state_data',
                                 'Knotendeformationen',
                                 f_name)

        print '*** read deformation data from file: %s ***' % (file_name)

        input_arr = np.loadtxt(file_name)

        node_no_idx, ux_idx, uy_idx, uz_idx, phix_idx, phiy_idx, phiz_idx = range(0, 7)

        ux = input_arr[:, [ux_idx]]
        uy = input_arr[:, [uy_idx]]
        uz = input_arr[:, [uz_idx]]

        # nodal displacements [m] (arranged as array with 3 columns)
        #
        node_U = input_arr[:, [ux_idx, uy_idx, uz_idx]]

        #-----------
        # get the element displacement at the center of gravity
        # the calculation based on the nodal displacement needs the information stored in 'geo_data'
        #-----------

        # the path to the 'geo_data' files is specified specifically in the definition of 'read_geo_data'
        gd = self.read_geo_data(f_name)

        # get mapping from 'geo_data'
        #
        t_elem_node_map = gd['t_elem_node_map']
        q_elem_node_map = gd['q_elem_node_map']
        t_idx = gd['t_idx']
        q_idx = gd['q_idx']

        # average element displacements (unordered)
        #
        t_elem_node_U = node_U[ t_elem_node_map ]
        q_elem_node_U = node_U[ q_elem_node_map ]
        t_elem_U = np.average(t_elem_node_U, axis=1)
        q_elem_U = np.average(q_elem_node_U, axis=1)

        # average element displacements (ordered in ascending element number)
        #
        elem_U = np.zeros((len(t_elem_U) + len(q_elem_U), 3), dtype='float')
        elem_U[t_idx, :] = t_elem_U
        elem_U[q_idx, :] = q_elem_U

        # average element displacements stored in 1d column arrays
        #
        ux_elem = elem_U[:, 0, None]
        uy_elem = elem_U[:, 1, None]
        uz_elem = elem_U[:, 2, None]

        return { 'elem_no' : elem_no,
                 'mx' : mx, 'my' : my, 'mxy' : mxy,
                 'nx' : nx, 'ny' : ny, 'nxy' : nxy,
                 'ux' : ux, 'uy' : uy, 'uz' : uz,
                 'node_U' : node_U,
                 #-------------------
                 'ux_elem' : ux_elem,
                 'uy_elem' : uy_elem,
                 'uz_elem' : uz_elem
               }

    # stress resultants to be multiplied within the LCC combinations
    #
    sr_columns = ['mx', 'my', 'mxy', 'nx', 'ny', 'nxy', 'ux_elem', 'uy_elem', 'uz_elem']

    def read_geo_data(self, file):
        '''to read the thickness file exported from InfoCAD
        using 'tab' as filed delimiter.
        '''
        geo_dir = os.path.join(self.data_dir, 'geo_data')
        node_file = os.path.join(geo_dir, 'Knotenkoordinaten.txt')
        elem_file = os.path.join(geo_dir, 'Elementbeschreibung.txt')
        thic_file = os.path.join(geo_dir, 'Querschnittswerte.txt')

        print '*** read geo data from node file: %s ***' % (node_file)
        print '*** read geo data from elem file: %s ***' % (elem_file)
        print '*** read geo data from thic files: %s ***' % (thic_file)

        node_arr = np.loadtxt(node_file)

        elem_line_arr = np.loadtxt(elem_file, usecols=(0, 1,), dtype=str)

        elem_no_arr, elem_type_arr = elem_line_arr[:, (0, 1)].T
        t_idx = np.argwhere(elem_type_arr == 'SH36')[:, 0]
        q_idx = np.argwhere(elem_type_arr == 'SH46')[:, 0]

        elem_file_ = open(elem_file, 'r')
        lines = elem_file_.readlines()
        line_arr = np.array(lines)
        elem_file_.close()

        t_line_arr = line_arr[t_idx]
        q_line_arr = line_arr[q_idx]

        t_str = StringIO(''.join(t_line_arr))
        q_str = StringIO(''.join(q_line_arr))

        t_elems = np.loadtxt(t_str, usecols=(0, 2, 3, 4, 5), dtype=int)
        q_elems = np.loadtxt(q_str, usecols=(0, 2, 3, 4, 5, 6), dtype=int)

        t_elem_node_map = t_elems[:, 1:-1] - 1
        q_elem_node_map = q_elems[:, 1:-1] - 1
        t_thickness_idx = t_elems[:, -1] - 1
        q_thickness_idx = q_elems[:, -1] - 1

        node_idx = np.array(node_arr[:, 0] - 1, dtype='int')
        node_X = node_arr[:, 1:][node_idx]

        t_elem_node_X = node_X[ t_elem_node_map ]
        q_elem_node_X = node_X[ q_elem_node_map ]

        t_elem_X = np.average(t_elem_node_X, axis=1)
        q_elem_X = np.average(q_elem_node_X, axis=1)

        n_X = np.zeros((len(line_arr), 3), dtype='float')

        n_X[t_idx, :] = t_elem_X
        n_X[q_idx, :] = q_elem_X

        X, Y, Z = n_X.T

        thic_file_ = open(thic_file, 'r')
        lines = thic_file_.readlines()
        line_arr = np.array(lines)
        thic_file_.close()

        idx_list = []
        d_list = []
        nr_lines = range(0, len(lines), 2)
        for line in line_arr[nr_lines]:
            nr, idx_str, id, d_str = line.split()
            idx = int(idx_str)
            d = float(d_str.split('=')[1])
            idx_list.append(idx)
            d_list.append(d)

        d_arr = np.array(d_list, dtype='f')
        d_arr = d_arr[np.array(idx_list, dtype='int_') - 1]

        thickness_arr = np.zeros((elem_line_arr.shape[0],), dtype='f')
        thickness_arr[t_idx] = d_arr[ t_thickness_idx ]
        thickness_arr[q_idx] = d_arr[ q_thickness_idx ]

        # convert strings entries to floats
        #
        elem_no_arr = np.array(elem_no_arr, dtype=float)

        # convert 1d-arrays to 2d-column arrays
        #
        elem_no_arr = elem_no_arr[:, np.newaxis]

        X = X[:, np.newaxis]
        Y = Y[:, np.newaxis]
        Z = Z[:, np.newaxis]
        thickness_arr = thickness_arr[:, np.newaxis]

        return  {'elem_no':elem_no_arr,
                 'X':X, 'Y':Y, 'Z':Z,
                 'node_X' : node_X,
                 't_elem_node_map' : t_elem_node_map,
                 'q_elem_node_map' : q_elem_node_map,
                 't_idx' : t_idx,
                 'q_idx' : q_idx,
                 'thickness':thickness_arr
                 }

    def plot_mesh(self, mlab, geo):

        points = geo['node_X']
        triangles = geo['t_elem_node_map']
        quads = geo['q_elem_node_map']
        # scalars = random.random(points.shape)

        # The TVTK dataset.
        qmesh = tvtk.PolyData(points=points, polys=quads)
        mlab.pipeline.surface(qmesh, representation='wireframe')

        # The TVTK dataset.
        tmesh = tvtk.PolyData(points=points, polys=triangles)
        mlab.pipeline.surface(tmesh, representation='wireframe')

    def plot_deformed_mesh(self, mlab, geo_data, state_data={'node_U' : np.array([0., 0., 0.])}, warp_factor=1.0):
        '''plot the deformed mesh based on the nodal displacement defined in 'state_data'
        '''
        points = geo_data['node_X']
        node_U = state_data['node_U']

        node_U_warped = node_U * warp_factor
        points += node_U_warped

        triangles = geo_data['t_elem_node_map']
        quads = geo_data['q_elem_node_map']

        # The TVTK dataset.
        qmesh = tvtk.PolyData(points=points, polys=quads)
        mlab.pipeline.surface(qmesh, representation='wireframe')

        # The TVTK dataset.
        tmesh = tvtk.PolyData(points=points, polys=triangles)
        mlab.pipeline.surface(tmesh, representation='wireframe')

    def plot_sd(self, mlab, geo_data, sd_key,
                state_data={'node_U' : np.array([0., 0., 0.])},
                warp_factor=1.0):
        '''plot the chosen state data defined by 'sd_key' at the center of gravity of the elements
        together with the element mesh; 'warp_factor' can be used to warp the deformation state in the plot.
        '''
        gd = geo_data
        sd = state_data

        # plot the deformed geometry (as mesh)
        #
        self.plot_deformed_mesh(mlab, gd, state_data=sd, warp_factor=warp_factor)

        # get mapping from 'geo_data'
        #
        t_elem_node_map = gd['t_elem_node_map']
        q_elem_node_map = gd['q_elem_node_map']
        t_idx = gd['t_idx']
        q_idx = gd['q_idx']

        # nodal displacement
        #
        node_U = sd['node_U']

        # average element displacement (unordered)
        #
        t_elem_node_U = node_U[ t_elem_node_map ]
        q_elem_node_U = node_U[ q_elem_node_map ]
        t_elem_U = np.average(t_elem_node_U, axis=1)
        q_elem_U = np.average(q_elem_node_U, axis=1)

        # element displacement (ordered in ascending element number)
        #
        elem_U = np.zeros((len(t_elem_U) + len(q_elem_U), 3), dtype='float')
        elem_U[t_idx, :] = t_elem_U
        elem_U[q_idx, :] = q_elem_U

        # element coordinates of the undeformed shape
        # (2d column arrays)
        #
        X = gd['X']
        Y = gd['Y']
        Z = gd['Z']

        # average element deformations
        #
        ux_elem = elem_U[:, 0, None]
        uy_elem = elem_U[:, 1, None]
        uz_elem = elem_U[:, 2, None]

        # element coordinates of the deformed state
        # considering the specified warp factor
        #
        X_def = X + ux_elem * warp_factor
        Y_def = Y + uy_elem * warp_factor
        Z_def = Z + uz_elem * warp_factor

        # plot state data in the deformed geometry
        #
        mlab.points3d(X_def, Y_def, Z_def, sd[sd_key],
                      mode="cube")

    def plot_col(self, mlab, plot_col, geo_data,
                 state_data={'ux_elem' : np.array([[0.], [0.], [0.]]),
                               'uy_elem' : np.array([[0.], [0.], [0.]]),
                               'uz_elem' : np.array([[0.], [0.], [0.]])},
                 warp_factor=1.0):
        '''
        plot the chosen plot_col array at the center of gravity of the elements;
        method is used by 'ls_table' to plot the selected plot variable
        ('warp_factor' can be used to warp the deformation state in the plot).
        '''
        gd = geo_data
        sd = state_data

        # element coordinates of the undeformed shape
        # (2d column arrays)
        #
        X = gd['X']
        Y = gd['Y']
        Z = gd['Z']

        # average element deformations
        #
        ux_elem = sd['ux_elem']
        uy_elem = sd['uy_elem']
        uz_elem = sd['uz_elem']

        # element coordinates of the deformed state
        # considering the specified warp factor
        #
        X_def = X + ux_elem * warp_factor
        Y_def = Y + uy_elem * warp_factor
        Z_def = Z + uz_elem * warp_factor

        X_def = X_def.flatten()
        Y_def = Y_def.flatten()
        Z_def = Z_def.flatten()

        # plot state data in the deformed geometry
        #
        mlab.points3d(X_def, Y_def, Z_def, plot_col,
                      mode="cube",
                      scale_mode='none',
                      scale_factor=0.05)

    def check_for_consistency(self, lc_list, geo_data_dict):
        print '*** check for consistency ***'

        for lc in lc_list:
            # check internal LC-consitency:
            # (compare elem_no of first LC with all other LC's in 'lc_list')
            #
            if not all(lc_list[0].state_data_dict['elem_no'] == lc.state_data_dict['elem_no']):
                raise ValueError, "element numbers in loading case '%s' and loading case '%s' are not identical. Check input files for internal consistency!" \
                        % (self.lc_list[0].name, lc.name)
                return False

            # check external consistency:
            # (compare 'elem_no' in 'geo_data' and 'elem_no' in state data of all loading-cases
            # input files (e.g. 'LC1.txt') defined in 'lc_list')
            #
            if not all(geo_data_dict['elem_no'] == lc.state_data_dict['elem_no']):
                raise ValueError, "element numbers in loading case '%s' and loading case '%s' are not identical. Check input files for external consistency!" \
                        % (lc_list[0].name, lc.name)
                return False

        print '*** input files checked for consistency (OK) ***'
        return True
