'''
Created on 13. 4. 2014

@author: Vancikv
'''

from traits.api import \
    HasTraits, Directory, List, Int, Float, \
    Array, Str, Property, cached_property, Trait

from util.home_directory import \
    get_home_directory

from traitsui.api import \
    View, Item, TabularEditor, VGroup, HGroup, \
    Include

import numpy as np

from limit_state import \
    LimitState

from limit_state_array_adapter import \
    LSArrayAdapter

class SLS(LimitState):
    '''Serviceability limit state
    '''

    # ------------------------------------------------------------
    # SLS: material parameters (Inputs)
    # ------------------------------------------------------------

    # tensile strength [MPa]
    f_ctk = Float(5.0, input=True)

    # flexural tensile strength [MPa]
    f_m = Float(5.0, input=True)

    # ------------------------------------------------------------
    # SLS - derived params:
    # ------------------------------------------------------------

    # area
    #
    A = Property(Float)
    def _get_A(self):
        return self.ls_table.thickness * 1.

    # moment of inertia
    #
    W = Property(Float)
    def _get_W(self):
        return 1. * self.ls_table.thickness ** 2 / 6.

    # ------------------------------------------------------------
    # SLS: outputs
    # ------------------------------------------------------------

    ls_columns = List(['m_sig_lo', 'n_sig_lo',
                       'm_sig_up', 'n_sig_up',
                       'eta_n_sig_lo', 'eta_m_sig_lo', 'eta_tot_sig_lo',
                       'eta_n_sig_up', 'eta_m_sig_up', 'eta_tot_sig_up',
                       'eta_tot'])

    ls_values = Property(depends_on='+input')
    @cached_property
    def _get_ls_values(self):
        '''get the outputs for SLS
        '''
        f_ctk = self.f_ctk
        f_m = self.f_m
        A = self.A  # [m**2/m]
        W = self.W  # [m**3/m]
        print 'A', A
        print 'W', W

        n_sig_lo = self.n_sig_lo  # [kN/m]
        m_sig_lo = self.m_sig_lo  # [kNm/m]
        sig_n_sig_lo = n_sig_lo / A / 1000.  # [MPa]
        sig_m_sig_lo = m_sig_lo / W / 1000.  # [MPa]

        n_sig_up = self.n_sig_up
        m_sig_up = self.m_sig_up
        sig_n_sig_up = n_sig_up / A / 1000.
        sig_m_sig_up = m_sig_up / W / 1000.

        eta_n_sig_lo = sig_n_sig_lo / f_ctk
        eta_m_sig_lo = sig_m_sig_lo / f_m
        eta_tot_sig_lo = eta_n_sig_lo + eta_m_sig_lo

        eta_n_sig_up = sig_n_sig_up / f_ctk
        eta_m_sig_up = sig_m_sig_up / f_m
        eta_tot_sig_up = eta_n_sig_up + eta_m_sig_up

        eta_tot = np.max(np.hstack([ eta_tot_sig_up, eta_tot_sig_lo]), axis=1)[:, None]

        return { 'sig_n_sig_lo':sig_n_sig_lo, 'sig_m_sig_lo':sig_m_sig_lo,
                 'sig_n_sig_up':sig_n_sig_up, 'sig_m_sig_up':sig_m_sig_up,
                 'eta_n_sig_lo':eta_n_sig_lo, 'eta_m_sig_lo':eta_m_sig_lo, 'eta_tot_sig_lo':eta_tot_sig_lo,
                 'eta_n_sig_up':eta_n_sig_up, 'eta_m_sig_up':eta_m_sig_up, 'eta_tot_sig_up':eta_tot_sig_up,
                 'eta_tot':eta_tot, }

    # evaluate stresses at lower side:
    #
    sig_n_sig_lo = Property
    def _get_sig_n_sig_lo(self):
        return self.ls_values['sig_n_sig_lo']

    sig_m_sig_lo = Property
    def _get_sig_m_sig_lo(self):
        return self.ls_values['sig_m_sig_lo']

    eta_n_sig_lo = Property
    def _get_eta_n_sig_lo(self):
        return self.ls_values['eta_n_sig_lo']

    eta_m_sig_lo = Property
    def _get_eta_m_sig_lo(self):
        return self.ls_values['eta_m_sig_lo']

    eta_tot_sig_lo = Property
    def _get_eta_tot_sig_lo(self):
        return self.ls_values['eta_tot_sig_lo']

    # evaluate stresses at upper side:
    #
    sig_n_sig_up = Property
    def _get_sig_n_sig_up(self):
        return self.ls_values['sig_n_sig_up']

    sig_m_sig_up = Property
    def _get_sig_m_sig_up(self):
        return self.ls_values['sig_m_sig_up']

    eta_n_sig_up = Property
    def _get_eta_n_sig_up(self):
        return self.ls_values['eta_n_sig_up']

    eta_m_sig_up = Property
    def _get_eta_m_sig_up(self):
        return self.ls_values['eta_m_sig_up']

    eta_tot_sig_up = Property
    def _get_eta_tot_sig_up(self):
        return self.ls_values['eta_tot_sig_up']

    # total eta (upper AND lower side)
    #
    eta_tot = Property
    def _get_eta_tot(self):
        return self.ls_values['eta_tot']


    assess_name = 'max_eta_tot'

    max_eta_tot = Property(depends_on='+input')
    @cached_property
    def _get_max_eta_tot(self):
        return np.max(self.eta_tot)

    #-------------------------------
    # ls view
    #-------------------------------

    # @todo: the dynamic selection of the columns to be displayed
    # does not work in connection with the LSArrayAdapter
    traits_view = View(VGroup(
                            HGroup(Item(name='f_ctk', label='Tensile strength concrete [MPa]: f_ctk '),
                                    Item(name='f_m', label='Flexural tensile trength concrete [MPa]: f_m ')
                                   ),
                            VGroup(
                                Include('ls_group'),

                                # @todo: currently LSArrayAdapter must be called both
                                #        in SLS and ULS separately to configure columns
                                #        arrangement individually
                                #
                                Item('ls_array', show_label=False,
                                      editor=TabularEditor(adapter=LSArrayAdapter()))
                                  ),
                              ),
                      resizable=True,
                      scrollable=True,
                      height=1000,
                      width=1100
                      )
