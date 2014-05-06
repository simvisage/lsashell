'''
Created on 13. 4. 2014

@author: Vancikv
'''

from traits.api import \
    List, Array, Property, cached_property

import numpy as np

from load_case_combination_table import \
    LCCTable

class LCCTableULS(LCCTable):
    '''LCCTable for ultimate limit state
    '''

    # set limit state to 'ULS'
    # (attribute is used by 'LSTable')
    #
    ls = 'ULS'

    # 'gamma' - safety factors
    #
    gamma_list = Property(List, depends_on='lc_list_')
    @cached_property
    def _get_gamma_list(self):
        return [[ lc.gamma_fav, lc.gamma_unf ] for lc in self.lc_list ]

    # 'psi' - combination factors (psi) for leading
    # and non leading load cases
    #
    psi_non_lead_arr = Property(Array, depends_on='lc_list_')
    @cached_property
    def _get_psi_non_lead_arr(self):
        return self._get_psi_arr('psi_0')

    psi_lead_arr = Property(Array, depends_on='lc_list_')
    @cached_property
    def _get_psi_lead_arr(self):
        return np.ones(len(self.lc_list))
