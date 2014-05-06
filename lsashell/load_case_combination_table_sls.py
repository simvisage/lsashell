'''
Created on 13. 4. 2014

@author: Vancikv
'''

from traits.api import \
    List, Array, Property, cached_property, Enum, Dict

import numpy as np

from load_case_combination_table import \
    LCCTable

class LCCTableSLS(LCCTable):
    '''LCCTable for serviceability limit state
    '''

    # set limit state to 'SLS'
    # (attribute is used by 'LSTable')
    #
    ls = 'SLS'

    # possible definitions of the serviceability limit state
    # are: 'rare', 'freq', 'perm'
    #
    combination_SLS = Enum('rare', 'freq', 'perm')
    def _combination_SLS_default(self):
        return 'rare'

    # 'gamma' - safety factors
    #
    gamma_list = Property(List, depends_on='lc_list_')
    @cached_property
    def _get_gamma_list(self):

        # generate [1.0]-entry in case of body-loads:
        #
        gamma_list = [[ 1.0 ]] * len(self.lc_list)

        # overwrite those in case of imposed-loads:
        #
        for imposed_idx in self.imposed_idx_list:
            gamma_fav_SLS = getattr(self.lc_list[ imposed_idx ], 'gamma_fav_SLS')
            gamma_unf_SLS = getattr(self.lc_list[ imposed_idx ], 'gamma_unf_SLS')
            gamma_list[ imposed_idx ] = [ gamma_unf_SLS, gamma_fav_SLS ]

        return gamma_list

    # 'psi' - combination factors
    #
    psi_lead_dict = Property(Dict)
    def _get_psi_lead_dict(self):
        return {'rare' : np.ones_like(self._get_psi_arr('psi_0')) ,
                'freq' : self._get_psi_arr('psi_1'),
                'perm' : self._get_psi_arr('psi_2')}

    psi_non_lead_dict = Property(Dict)
    def _get_psi_non_lead_dict(self):
        return {'rare' : self._get_psi_arr('psi_0') ,
                'freq' : self._get_psi_arr('psi_2'),
                'perm' : self._get_psi_arr('psi_2')}

    # combination factors (psi) for leading
    # and non leading load cases
    #
    psi_lead_arr = Property(Array, depends_on='lc_list_, combination_SLS')
    @cached_property
    def _get_psi_lead_arr(self):
        return self.psi_lead_dict[ self.combination_SLS ]

    psi_non_lead_arr = Property(Array, depends_on='lc_list_, combination_SLS')
    @cached_property
    def _get_psi_non_lead_arr(self):
        return self.psi_non_lead_dict[ self.combination_SLS ]

