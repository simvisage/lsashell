'''
Created on 13. 4. 2014

@author: Vancikv
'''

from traits.api import \
    HasTraits, List, Float, Enum, \
    Array, Str, Property, cached_property, \
    WeakRef, Button, Bool

from traitsui.api import \
    View, Item, VGroup, HGroup

from mayavi import \
    mlab

import numpy as np

class LimitState(HasTraits):
    '''Limit state class
    '''

    # backward link to the info shell to access the
    # input data when calculating
    # the limit-state-specific values
    #
    ls_table = WeakRef

    #-------------------------------
    # ls columns
    #-------------------------------
    # defined in the subclasses
    #
    ls_columns = List
    show_ls_columns = Bool(True)

    #-------------------------------
    # geo columns form info shell
    #-------------------------------

    geo_columns = List([ 'elem_no', 'X', 'Y', 'Z', 'thickness' ])
    show_geo_columns = Bool(True)

    elem_no = Property(Array)
    def _get_elem_no(self):
        return self.ls_table.elem_no

    X = Property(Array)
    def _get_X(self):
        return self.ls_table.X

    Y = Property(Array)
    def _get_Y(self):
        return self.ls_table.Y

    Z = Property(Array)
    def _get_Z(self):
        return self.ls_table.Z

    thickness = Property(Array)
    def _get_thickness(self):
        return self.ls_table.thickness

    #-------------------------------
    # state columns form info shell
    #-------------------------------

    state_columns = List([
                           'mx', 'my', 'mxy', 'nx', 'ny', 'nxy',
#                           'sigx_lo', 'sigy_lo', 'sigxy_lo',
#                           'sig1_lo', 'sig1_up_sig_lo',
                            'alpha_sig_lo',
# 'alpha_sig2_lo',
                           'm_sig_lo', 'n_sig_lo',
                           'm_sig2_lo', 'n_sig2_lo',
#                           'sigx_up', 'sigy_up', 'sigxy_up',
#                           'sig1_up', 'sig1_lo_sig_up', 'alpha_sig_up',
                           'm_sig_up', 'n_sig_up',
                           'm_sig2_up', 'n_sig2_up',
                            ])

    show_state_columns = Bool(True)

    mx = Property(Array)
    def _get_mx(self):
        return self.ls_table.mx

    my = Property(Array)
    def _get_my(self):
        return self.ls_table.my

    mxy = Property(Array)
    def _get_mxy(self):
        return self.ls_table.mxy

    nx = Property(Array)
    def _get_nx(self):
        return self.ls_table.nx

    ny = Property(Array)
    def _get_ny(self):
        return self.ls_table.ny

    nxy = Property(Array)
    def _get_nxy(self):
        return self.ls_table.nxy

    n_sig_lo = Property(Array)
    def _get_n_sig_lo(self):
        return self.ls_table.n_sig_lo

    m_sig_lo = Property(Array)
    def _get_m_sig_lo(self):
        return self.ls_table.m_sig_lo

    n_sig_up = Property(Array)
    def _get_n_sig_up(self):
        return self.ls_table.n_sig_up

    m_sig_up = Property(Array)
    def _get_m_sig_up(self):
        return self.ls_table.m_sig_up

    # evaluate principal stresses
    # upper face:
    #
    sigx_up = Property(Array)
    def _get_sigx_up(self):
        return self.ls_table.sigx_up

    sigy_up = Property(Array)
    def _get_sigy_up(self):
        return self.ls_table.sigy_up

    sigxy_up = Property(Array)
    def _get_sigxy_up(self):
        return self.ls_table.sigxy_up

    sig1_up = Property(Array)
    def _get_sig1_up(self):
        return self.ls_table.sig1_up

    sig2_up = Property(Array)
    def _get_sig2_up(self):
        return self.ls_table.sig2_up

    alpha_sig_up = Property(Array)
    def _get_alpha_sig_up(self):
        return self.ls_table.alpha_sig_up

    # lower face:
    #
    sigx_lo = Property(Float)
    def _get_sigx_lo(self):
        return self.ls_table.sigx_lo

    sigy_lo = Property(Float)
    def _get_sigy_lo(self):
        return self.ls_table.sigy_lo

    sigxy_lo = Property(Float)
    def _get_sigxy_lo(self):
        return self.ls_table.sigxy_lo

    sig1_lo = Property(Float)
    def _get_sig1_lo(self):
        return self.ls_table.sig1_lo

    sig2_lo = Property(Float)
    def _get_sig2_lo(self):
        return self.ls_table.sig2_lo

    alpha_sig_lo = Property(Float)
    def _get_alpha_sig_lo(self):
        return self.ls_table.alpha_sig_lo

    #-------------------------------
    # ls table
    #-------------------------------

    # all columns associated with the limit state including the corresponding
    # stress resultants
    #
    columns = Property(List, depends_on='show_geo_columns, show_state_columns, show_ls_columns')
    @cached_property
    def _get_columns(self):
        columns = []

        if self.show_geo_columns:
            columns += self.geo_columns

        if self.show_state_columns:
            columns += self.state_columns

        if self.show_ls_columns:
            columns += self.ls_columns

        return columns

    # select column used for sorting the data in selected sorting order
    #
    sort_column = Enum(values='columns')
    def _sort_column_default(self):
        return self.columns[-1]

    sort_order = Enum('descending', 'ascending', 'unsorted')

    #-------------------------------------------------------
    # get the maximum value of the selected variable
    # 'max_in_column' of the current sheet (only one sheet)
    #-------------------------------------------------------

    # get the maximum value of the chosen column
    #
    max_in_column = Enum(values='columns')
    def _max_in_column_default(self):
        return self.columns[-1]

    max_value = Property(depends_on='max_in_column')
    def _get_max_value(self):
        col = getattr(self, self.max_in_column)[:, 0]
        return max(col)

    #-------------------------------------------------------
    # get the maximum value and the corresponding case of
    # the selected variable 'max_in_column' in all (!) sheets
    #-------------------------------------------------------

    max_value_all = Property(depends_on='max_in_column')
    def _get_max_value_all(self):
        return self.ls_table.max_value_and_case[ self.max_in_column ]['max_value']

    max_case = Property(depends_on='max_in_column')
    def _get_max_case(self):
        return self.ls_table.max_value_and_case[ self.max_in_column ]['max_case']

    #-------------------------------------------------------
    # get ls_table for View
    #-------------------------------------------------------

    # stack columns together for table used by TabularEditor
    #
    ls_array = Property(Array, depends_on='sort_column, sort_order, \
                                              show_geo_columns, \
                                              show_state_columns, \
                                              show_ls_columns')

    @cached_property
    def _get_ls_array(self):

        arr_list = [ getattr(self, col) for col in self.columns ]

        # get the array currently selected by the sort_column enumeration
        #
        sort_arr = getattr(self, self.sort_column)[:, 0]
        sort_idx = np.argsort(sort_arr)
        ls_array = np.hstack(arr_list)

        if self.sort_order == 'descending':
            return ls_array[ sort_idx[::-1] ]
        if self.sort_order == 'ascending':
            return ls_array[ sort_idx ]
        if self.sort_order == 'unsorted':
            return ls_array

    #---------------------------------
    # plot outputs in mlab-window
    #---------------------------------
    warp_factor = Float(100., input=True)

    plot_column = Enum(values='columns')
    plot = Button
    def _plot_fired(self):

        plot_col = getattr(self, self.plot_column).flatten()
        if self.plot_column == 'n_tex':
            plot_col = np.where(plot_col < 0, 0, plot_col)

        mlab.figure(figure="SFB532Demo",
                     bgcolor=(1.0, 1.0, 1.0),
                     fgcolor=(0.0, 0.0, 0.0))

        gd = self.ls_table.geo_data
        sd = self.ls_table.state_data

        r = self.ls_table.reader
        # use plotting function defined by the specific LCCTableReader
        # extract global coordinates ('X','Y','Z') from 'geo_data' and
        # global displacements ('ux_elem','uy_elem','uz_elem') from 'state_data'
        # if this information is available (distinguished by the specific Reader)
        r.plot_col(mlab, plot_col, gd, state_data=sd, warp_factor=self.warp_factor)

        mlab.scalarbar(title=self.plot_column, orientation='vertical')
        mlab.show



    # name of the trait that is used to assess the evaluated design
    #
    assess_name = Str('')

    #-------------------------------
    # ls group
    #-------------------------------

    # @todo: the dynamic selection of the columns to be displayed
    # does not work in connection with the LSArrayAdapter
    ls_group = VGroup(
                        HGroup(# Item( 'assess_name' ),
                                Item('max_in_column'),
                                Item('max_value', style='readonly', format_str='%6.2f'),
                              ),
                        HGroup(Item('sort_column'),
                                Item('sort_order'),
                                Item('show_geo_columns', label='show geo'),
                                Item('show_state_columns', label='show state'),
                                Item('show_ls_columns', label='show ls'),
                                Item('plot_column'),
                                Item('plot'),
                                Item('warp_factor')
                              ),
                     )
