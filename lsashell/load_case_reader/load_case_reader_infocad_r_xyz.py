'''
Created on 13. 4. 2014

@author: Vancikv
'''

import os

import numpy as np

from lsashell.load_case_reader.load_case_reader import \
    LCReader

class LCReaderInfoCADRxyz(LCReader):

    def read_state_data(self, f_name):

        file_name = os.path.join(self.data_dir, 'state_data',\
                                 'Auflagerreaktionen',\
                                 f_name)

        print '*** read state data from file: %s ***' % (file_name)

        input_arr = np.loadtxt(file_name)

        node_no_idx, Rx_idx, Ry_idx, Rz_idx, Mx_idx, My_idx, Mz_idx = range(0, 7)

        # node number:
        #
        node_no = input_arr[:, [node_no_idx]]

        # forces [kN]:
        #
        Rx = input_arr[:, [Rx_idx]]
        Ry = input_arr[:, [Ry_idx]]
        Rz = input_arr[:, [Rz_idx]]

        # moments [kNm]
        #
        Mx = input_arr[:, [Mx_idx]]
        My = input_arr[:, [My_idx]]
        Mz = input_arr[:, [Mz_idx]]

        return { 'node_no' : node_no,
                 'Rx' : Rx, 'Ry' : Ry, 'Rz' : Rz,
                 'Mx' : Mx, 'My' : My, 'Mz' : Mz }

    def read_geo_data(self, f_name):
        '''read the thickness file exported from InfoCAD
        using 'tab' as filed delimiter.
        '''
        sd = self.read_state_data( f_name )
        node_no = sd['node_no']
        
        geo_dir = os.path.join(self.data_dir, 'geo_data')
        node_file = os.path.join(geo_dir, 'Knotenkoordinaten.txt')
        print '*** read support node file: %s ***' % (node_file)
        node_arr = np.loadtxt(node_file)

        idx_spprt_nodes = [ np.where( node_arr[:,0] == node_no[i] )[0] for i in range( node_no.shape[0] ) ]
        print 'idx_spprt_nodes', idx_spprt_nodes
        X_spprt = node_arr[ idx_spprt_nodes, 1 ]
        Y_spprt = node_arr[ idx_spprt_nodes, 2 ]
        Z_spprt = node_arr[ idx_spprt_nodes, 3 ]
        
        sd['X_spprt'] = X_spprt
        sd['Y_spprt'] = Y_spprt
        sd['Z_spprt'] = Z_spprt
        return sd

    
    def check_for_consistency(self, lc_list, geo_data_dict):
        pass