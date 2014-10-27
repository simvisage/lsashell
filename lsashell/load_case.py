'''
Created on 13. 4. 2014

@author: Vancikv
'''

from traits.api import \
    HasTraits, List, Float, Enum, Dict, Callable, \
    Array, Str, Property, cached_property, WeakRef

import numpy as np

class LC(HasTraits):
    '''Loading case class
    '''

    reader = WeakRef

    lcc_table = WeakRef

    # name of the file containing the stress resultants
    #
    file_name = Str(input=True)

    # data filter (used to hide unwanted values, e.g. high sigularities etc.)
    #
    data_filter = Callable(input=True)

    # name of the loading case
    #
    name = Str(input=True)

    # category of the loading case
    #
    category = Enum('dead-load', 'additional dead-load', 'imposed-load', input=True)

    # list of keys specifying the names of the loading cases
    # that can not exist at the same time, i.e. which are exclusive to each other
    #
    exclusive_to = List(Str, input=True)
    def _exclusive_to_default(self):
        return []

    # combination factors (need to be defined in case of imposed loads)
    #
    psi_0 = Float(input=True)
    psi_1 = Float(input=True)
    psi_2 = Float(input=True)

    # safety factors ULS
    #
    gamma_fav = Float(input=True)
    def _gamma_fav_default(self):
        if self.category == 'dead-load':
            return 1.00
        if self.category == 'additional dead-load':
            return 0.00
        if self.category == 'imposed-load':
            return 0.00

    gamma_unf = Float(input=True)
    def _gamma_unf_default(self):
        if self.category == 'dead-load':
            return 1.35
        if self.category == 'additional dead-load':
            return 1.35
        if self.category == 'imposed-load':
            return 1.50

    # security factors SLS:
    # (used to distinguish combinations where imposed-loads
    # or additional-dead-loads are favorable or unfavorable.)
    #
    gamma_fav_SLS = Float(input=True)
    def _gamma_fav_SLS_default(self):
        if self.category == 'dead-load':
            return 1.00
        elif self.category == 'additional dead-load' or \
             self.category == 'imposed-load':
            return 0.00

    gamma_unf_SLS = Float(input=True)
    def _gamma_unf_SLS_default(self):
        return 1.00

    # original state data (before filtering)
    #
    state_data_orig = Property(Dict, depends_on='file_name')
    @cached_property
    def _get_state_data_orig(self):
        return self.reader.read_state_data(self.file_name)

    # state data (after filtering)
    #
    state_data_dict = Property(Dict, depends_on='file_name, +filter')
    @cached_property
    def _get_state_data_dict(self):
        d = {}
        for k, arr in self.state_data_orig.items():
            d[ k ] = self.data_filter(self.lcc_table, arr)
        return d

    sr_columns = Property(List)
    def _get_sr_columns(self):
        '''return the list of the stress resultants to be use within the combinations of LCC.
        '''
        # if LCCTableReaderInfoCAD is used:
        # use displacement stored in 'state_data' within 'plot_col' method of the reader
        # sr_columns = List(['mx', 'my', 'mxy', 'nx', 'ny', 'nxy', 'ux_elem', 'uy_elem', 'uz_elem'])
        # if LCCTableReaderRFEM is used:
        # no displacement is available yet
        # sr_columns = List(['mx', 'my', 'mxy', 'nx', 'ny', 'nxy'])
        return self.reader.sr_columns

    sr_arr = Property(Array)
    def _get_sr_arr(self):
        '''return the stress resultants of the loading case
        as stack of all sr-column arrays.
        '''
        sd_dict = self.state_data_dict
        return np.hstack([ sd_dict[ sr_key ] for sr_key in self.sr_columns ])

#    # deformation data
#    #
#    u_data_dict = Property(Dict)
#    @cached_property
#    def _get_u_data_dict(self):
#        return self.reader.read_u_data(self.file_name)
#
#    u_arr = Property(Array)
#    def _get_u_arr(self):
#        '''return the element deformation of the loading case
#        as stack of all u-column arrays.
#        '''
#        u_dict = self.u_data_dict
#        return hstack([ u_dict[ u_key ] for u_key in u_dict.keys() ])
