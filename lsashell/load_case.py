'''
Created on 13. 4. 2014

@author: Vancikv
'''

from traits.api import \
    HasTraits, List, Float, Enum, Dict, Callable, \
    Array, Str, Property, cached_property, WeakRef

from traitsui.api import \
    View, Item, Group, TabularEditor

import numpy as np

from traitsui.tabular_adapter import TabularAdapter


class StateArrayAdapter(TabularAdapter):

    columns = [('i', 'index'), ('mx', 0), ('my', 1),  ('mxy', 2),
               ('nx', 3), ('ny', 4),  ('nxy', 5),
               ]

    # Font fails with wx in OSX; see traitsui issue #13:
    # font        = Font('Courier 10')
    alignment = 'right'
    format = '%.4f'

    index_text = Property

    def _get_index_text(self):
        return str(self.row)


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

    def _data_filter_default(self):
        def dummy_filter(lcc_table, arr):
            return arr
        return dummy_filter

    # name of the loading case
    #
    name = Str(input=True)

    category = Enum('dead-load', 'additional dead-load', 'imposed-load',
                    input=True)
    '''Category of the loading case
    '''

    exclusive_to = List(Str, input=True)
    '''List of keys specifying the names of the loading cases
    that can not exist at the same time, i.e. which are exclusive to each other
    '''

    def _exclusive_to_default(self):
        return []

    psi_0 = Float(input=True)
    '''Combination factors
    (need to be defined in case of imposed loads)
    '''
    psi_1 = Float(input=True)
    psi_2 = Float(input=True)

    # =========================================================================
    # Gamma coefficients for ULS design
    # =========================================================================

    gamma_ULS_fav_table = Dict({'dead-load': 1.00,
                                'additional dead-load': 0.00,
                                'imposed-load': 0.00})

    gamma_ULS_fav = Property(Float, depends_on='category')
    '''Safety factors ULS
    for favorable load cases.
    '''

    @cached_property
    def _get_gamma_ULS_fav(self):
        return self.gamma_ULS_fav_table[self.category]

    gamma_ULS_unf_table = Dict({'dead-load': 1.35,
                                'additional dead-load': 1.35,
                                'imposed-load': 1.5})

    gamma_ULS_unf = Property(Float, depends_on='category')
    '''Safety factors ULS
    for unfavored load cases.
    '''

    @cached_property
    def _get_gamma_ULS_unf(self):
        return self.gamma_ULS_unf_table[self.category]

    # =========================================================================
    # Gamma coefficients for SLS design
    # =========================================================================

    gamma_fav_SLS = Float(input=True)
    '''Safety factors SLS
    used to distinguish combinations where imposed-loads
    or additional-dead-loads are favorable or unfavorable.
    '''

    def _gamma_fav_SLS_default(self):
        if self.category == 'dead-load':
            return 1.00
        elif self.category == 'additional dead-load' or \
                self.category == 'imposed-load':
            return 0.00

    gamma_unf_SLS = Float(input=True)
    '''Safety factors for SLS
    unfavored load cases)
   '''

    def _gamma_unf_SLS_default(self):
        return 1.00

    state_data_orig = Property(Dict, depends_on='file_name')
    '''Original state data (before filtering)
    '''
    @cached_property
    def _get_state_data_orig(self):
        return self.reader.read_state_data(self.file_name)

    state_data_dict = Property(Dict, depends_on='file_name, +filter')
    '''state data (after filtering)
    '''
    @cached_property
    def _get_state_data_dict(self):
        d = {}
        for k, arr in self.state_data_orig.items():
            d[k] = self.data_filter(self.lcc_table, arr)
        return d

    sr_columns = Property(List)
    '''Return the list of the stress resultants to be use within
    the combinations of LCC.
    '''

    def _get_sr_columns(self):
        '''
        if LCCTableReaderInfoCAD is used:
        use displacement stored in 'state_data' within 'plot_col'
        method of the reader
        sr_columns = List(['mx', 'my', 'mxy', 'nx', 'ny', 'nxy', 'ux_elem',
                           'uy_elem', 'uz_elem'])
        if LCCTableReaderRFEM is used:
        no displacement is available yet
        sr_columns = List(['mx', 'my', 'mxy', 'nx', 'ny', 'nxy'])
        '''
        return self.reader.sr_columns

    sr_arr = Property(Array)
    '''Return the stress resultants of the loading case
    as stack of all sr-column arrays.
    '''

    @cached_property
    def _get_sr_arr(self):
        sd_dict = self.state_data_dict

        return np.hstack([sd_dict[sr_key] for sr_key in self.sr_columns])

    traits_view = View(Group(
        Item('gamma_ULS_fav_table',
             label='favorable', style='readonly'),
        Item(
            'gamma_ULS_unf_table',
            label='unfavorable', style='readonly'),
        label='Gamma coefficients'
    ),
        Item('category'),
        Item('gamma_ULS_fav', style='readonly'),
        Item('gamma_ULS_unf', style='readonly'),
        Group(
        Item('sr_arr',
             show_label=False,
             style='readonly',
             editor=TabularEditor(adapter=StateArrayAdapter())
             ),
    ),
        width=0.5,
        height=0.3,
        resizable=True,
        buttons=['OK', 'Cancel']
    )
