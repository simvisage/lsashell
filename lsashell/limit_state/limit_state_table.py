'''
Created on 13. 4. 2014

@author: Vancikv
'''

from traits.api import \
    HasTraits, Int, Dict, Property, cached_property, \
    Bool, Array, Float, Trait, Instance

from traitsui.api import \
    View, Tabbed, Item
    
from numpy import \
    sin, cos, arctan, sqrt, ones_like, pi

from serviceability_limit_state import \
    SLS

from ultimate_limit_state import \
    ULS
    
from limit_state import \
    LimitState

class LSTable(HasTraits):
    '''Assessment tool
    '''

    is_id = Int(0)
    # geo data: coordinates and element thickness
    #
    geo_data = Dict

    #------------------------------------------------------------
    # evaluation with conservative simplification for 'k_alpha'
    #------------------------------------------------------------
    # if flag is set to 'True' the resistance values 'n_Rdt' and 'm_Rd' below are
    # multiplied with the highest reduction factor 'k_alpha = 0.707', independently
    # of the true deflection angel 'beta_q' and 'beta_l'
    #
    k_alpha_min = Bool(False)

    elem_no = Property(Array)
    def _get_elem_no(self):
        return self.geo_data['elem_no']

    X = Property(Array)
    def _get_X(self):
        return self.geo_data['X']

    Y = Property(Array)
    def _get_Y(self):
        return self.geo_data['Y']

    Z = Property(Array)
    def _get_Z(self):
        return self.geo_data['Z']

    thickness = Property(Array)
    def _get_thickness(self):
        '''element thickness [m])'''
        return self.geo_data['thickness']

    # state data: stress resultants
    #
    state_data = Dict

    mx = Property(Array)
    def _get_mx(self):
        return self.state_data['mx']

    my = Property(Array)
    def _get_my(self):
        return self.state_data['my']

    mxy = Property(Array)
    def _get_mxy(self):
        return self.state_data['mxy']

    nx = Property(Array)
    def _get_nx(self):
        return self.state_data['nx']

    ny = Property(Array)
    def _get_ny(self):
        return self.state_data['ny']

    nxy = Property(Array)
    def _get_nxy(self):
        return self.state_data['nxy']

    # ------------------------------------------------------------
    # Index sig: calculate principle direction of the stresses at
    # the lower and upper side and get the corresponding values of
    # the stresses at the opposite side. Also get the corresponding
    # values of the normal force and the moment in this direction
    # ------------------------------------------------------------

    princ_values_sig = Property(Dict, depends_on='data_file_stress_resultants')
    @cached_property
    def _get_princ_values_sig(self):
        '''principle value of the stresses for the lower ('lo') and upper ('up') face:
        '''
        # stress_resultants in global coordinates
        # --> moments in kNm
        # --> normal forces in kN
        # --> area in m**2
        # --> resisting moment in m**3
        # --> stresses in MPa
        #
        mx = self.mx
        my = self.my
        mxy = self.mxy
        nx = self.nx
        ny = self.ny
        nxy = self.nxy

        # geometrical properties:
        #
        A = self.thickness * 1.0
        W = self.thickness ** 2 * 1.0 / 6.


        # compare the formulae with the RFEM-manual p.290

        # stresses [MPa] upper face in global drection:
        #
        sigx_up = (nx / A - mx / W) / 1000.
        sigy_up = (ny / A - my / W) / 1000.
        sigxy_up = (nxy / A - mxy / W) / 1000.

        # stresses [MPa] lower face in global direction:
        #
        sigx_lo = (nx / A + mx / W) / 1000.
        sigy_lo = (ny / A + my / W) / 1000.
        sigxy_lo = (nxy / A + mxy / W) / 1000.

        #--------------
        # upper face:
        #--------------

        # principal stresses upper face:
        #
        sig1_up = 0.5 * (sigx_up + sigy_up) + 0.5 * sqrt((sigx_up - sigy_up) ** 2 + 4 * sigxy_up ** 2)
        sig2_up = 0.5 * (sigx_up + sigy_up) - 0.5 * sqrt((sigx_up - sigy_up) ** 2 + 4 * sigxy_up ** 2)

        alpha_sig_up = pi / 2. * ones_like(sig1_up)

        # from mechanic formula book (cf. also InfoCAD manual)
        #
        bool_arr = sig2_up != sigx_up
        alpha_sig_up[ bool_arr ] = arctan(sigxy_up[ bool_arr ] / (sig2_up[ bool_arr ] - sigx_up[ bool_arr ]))

        # mohr-circle formula
        #
#         bool_arr = sigx_up != sigy_up
#         alpha_sig_up[ bool_arr ] = 0.5 * arctan(sigxy_up[ bool_arr ] / (sigx_up[ bool_arr ] - sigy_up[ bool_arr ]))

        # angle of principle stresses (2-direction = minimum stresses (compression))
        #
        alpha_sig2_up = alpha_sig_up + pi / 2

        # RFEM-manual (NOTE that manual contains typing error!)
        # the formula as given below yields the same results then the used mechanic formula
#        bool = sigx_up != sigy_up
#        alpha_sig_up[ bool ] = 0.5 * arctan( 2 * sigxy_up[ bool ] / ( sigx_up[ bool ] - sigy_up[ bool ] ) )

        alpha_sig_up_deg = alpha_sig_up * 180. / pi

        # transform formula taken from mechanic formula book
        # transform the stresses at the lower face to the principle tensile direction (1-direction) of the upper stresses
        sig1_lo_sig_up = 0.5 * (sigy_lo + sigx_lo) - 0.5 * (sigy_lo - sigx_lo) * cos(2 * alpha_sig_up) - sigxy_lo * sin(2 * alpha_sig_up)

        # transform moments and normal forces in the direction of the principal stresses (1-direction)
        #
        m_sig_up = 0.5 * (my + mx) - 0.5 * (my - mx) * cos(2 * alpha_sig_up) - mxy * sin(2 * alpha_sig_up)
        n_sig_up = 0.5 * (ny + nx) - 0.5 * (ny - nx) * cos(2 * alpha_sig_up) - nxy * sin(2 * alpha_sig_up)
#         m_sig_up = 0.5 * (mx + my) + 0.5 * (mx - my) * cos(2 * alpha_sig_up) + mxy * sin(2 * alpha_sig_up)
#         n_sig_up = 0.5 * (nx + ny) + 0.5 * (nx - ny) * cos(2 * alpha_sig_up) + nxy * sin(2 * alpha_sig_up)

        # transform moments and normal forces in the direction of the principal stresses (1-direction)
        #
        m_sig2_up = 0.5 * (my + mx) - 0.5 * (my - mx) * cos(2 * alpha_sig2_up) - mxy * sin(2 * alpha_sig2_up)
        n_sig2_up = 0.5 * (ny + nx) - 0.5 * (ny - nx) * cos(2 * alpha_sig2_up) - nxy * sin(2 * alpha_sig2_up)
        #
#         m_sig2_up = 0.5 * (mx + my) - 0.5 * (mx - my) * cos(2 * alpha_sig_up) - mxy * sin(2 * alpha_sig_up)
#         n_sig2_up = 0.5 * (nx + ny) - 0.5 * (nx - ny) * cos(2 * alpha_sig_up) - nxy * sin(2 * alpha_sig_up)
        #
#         m_sig2_up = 0.5 * (mx + my) + 0.5 * (mx - my) * cos(2 * alpha_sig_up) - mxy * sin(2 * alpha_sig_up)
#         n_sig2_up = 0.5 * (nx + ny) + 0.5 * (nx - ny) * cos(2 * alpha_sig_up) - nxy * sin(2 * alpha_sig_up)

        #--------------
        # lower face:
        #--------------

        # principal stresses lower face:
        #
        sig1_lo = 0.5 * (sigx_lo + sigy_lo) + 0.5 * sqrt((sigx_lo - sigy_lo) ** 2 + 4 * sigxy_lo ** 2)
        sig2_lo = 0.5 * (sigx_lo + sigy_lo) - 0.5 * sqrt((sigx_lo - sigy_lo) ** 2 + 4 * sigxy_lo ** 2)

        alpha_sig_lo = pi / 2. * ones_like(sig1_lo)

#        # from mechanic formula book (cf. also InfoCAD manual)
#        #
        bool_arr = sig2_lo != sigx_lo
        alpha_sig_lo[ bool_arr ] = arctan(sigxy_lo[ bool_arr ] / (sig2_lo[ bool_arr ] - sigx_lo[ bool_arr ]))

        # mohr-circle formula
        #
#         bool_arr = sigx_lo != sigy_lo
#         alpha_sig_lo[ bool_arr ] = 0.5 * arctan(sigxy_lo[ bool_arr ] / (sigx_lo[ bool_arr ] - sigy_lo[ bool_arr ]))

        # angle of principle stresses (2-direction = minimum stresses (compression))
        #
        alpha_sig2_lo = alpha_sig_lo + pi / 2

        # RFEM-manual (NOTE that manual contains typing error!)
        # the formula as given below yields the same results then the used mechanic formula
#        bool = sigx_lo != sigy_lo
#        alpha_sig_lo[ bool ] = 0.5 * arctan( 2 * sigxy_lo[ bool ] / ( sigx_lo[ bool ] - sigy_lo[ bool ] ) )

        alpha_sig_lo_deg = alpha_sig_lo * 180. / pi

        # transform the stresses at the lower face to the principle tensile direction (1-direction) of the upper stresses
        # Note: transformation forumla taken from mechanic formula book
        #
        sig1_up_sig_lo = 0.5 * (sigy_up + sigx_up) - 0.5 * (sigy_up - sigx_up) * cos(2 * alpha_sig_lo) - sigxy_up * sin(2 * alpha_sig_lo)

        # transform moments and normal forces in the direction of the principal stresses (1-direction)
        #
        m_sig_lo = 0.5 * (my + mx) - 0.5 * (my - mx) * cos(2 * alpha_sig_lo) - mxy * sin(2 * alpha_sig_lo)
        n_sig_lo = 0.5 * (ny + nx) - 0.5 * (ny - nx) * cos(2 * alpha_sig_lo) - nxy * sin(2 * alpha_sig_lo)
#         m_sig_lo = 0.5 * (mx + my) + 0.5 * (mx - my) * cos(2 * alpha_sig_lo) + mxy * sin(2 * alpha_sig_lo)
#         n_sig_lo = 0.5 * (nx + ny) + 0.5 * (nx - ny) * cos(2 * alpha_sig_lo) + nxy * sin(2 * alpha_sig_lo)

        # transform moments and normal forces in the direction of the principal stresses (2-direction)
        #
        m_sig2_lo = 0.5 * (my + mx) - 0.5 * (my - mx) * cos(2 * alpha_sig2_lo) - mxy * sin(2 * alpha_sig2_lo)
        n_sig2_lo = 0.5 * (ny + nx) - 0.5 * (ny - nx) * cos(2 * alpha_sig2_lo) - nxy * sin(2 * alpha_sig2_lo)
        #
#         m_sig2_lo = 0.5 * (mx + my) - 0.5 * (mx - my) * cos(2 * alpha_sig_lo) - mxy * sin(2 * alpha_sig_lo)
#         n_sig2_lo = 0.5 * (nx + ny) - 0.5 * (nx - ny) * cos(2 * alpha_sig_lo) - nxy * sin(2 * alpha_sig_lo)
        #
#         m_sig2_lo = 0.5 * (mx + my) + 0.5 * (mx - my) * cos(2 * alpha_sig_lo) - mxy * sin(2 * alpha_sig_lo)
#         n_sig2_lo = 0.5 * (nx + ny) + 0.5 * (nx - ny) * cos(2 * alpha_sig_lo) - nxy * sin(2 * alpha_sig_lo)

        return {
                 'sigx_up' : sigx_up, 'sigy_up' : sigy_up, 'sigxy_up' : sigxy_up,
                 'sig1_up' : sig1_up, 'sig2_up' : sig2_up, 'alpha_sig_up' : alpha_sig_up_deg,

                 'sig1_lo_sig_up' : sig1_lo_sig_up,
                 'm_sig_up' : m_sig_up, 'n_sig_up' : n_sig_up,
                 'm_sig2_up' : m_sig2_up, 'n_sig2_up' : n_sig2_up,

                 'sigx_lo' : sigx_lo, 'sigy_lo' : sigy_lo, 'sigxy_lo' : sigxy_lo,
                 'sig1_lo' : sig1_lo, 'sig2_lo' : sig2_lo, 'alpha_sig_lo' : alpha_sig_lo_deg,

                 'sig1_up_sig_lo' : sig1_up_sig_lo,
                 'm_sig_lo' : m_sig_lo, 'n_sig_lo' : n_sig_lo,
                 'm_sig2_lo' : m_sig2_lo, 'n_sig2_lo' : n_sig2_lo,

               }

    # stresses upper face:
    #
    sigx_up = Property(Float)
    def _get_sigx_up(self):
        return self.princ_values_sig['sigx_up']

    sigy_up = Property(Float)
    def _get_sigy_up(self):
        return self.princ_values_sig['sigy_up']

    sigxy_up = Property(Float)
    def _get_sigxy_up(self):
        return self.princ_values_sig['sigxy_up']

    sig1_up = Property(Float)
    def _get_sig1_up(self):
        return self.princ_values_sig['sig1_up']

    sig2_up = Property(Float)
    def _get_sig2_up(self):
        return self.princ_values_sig['sig2_up']

    alpha_sig_up = Property(Float)
    def _get_alpha_sig_up(self):
        return self.princ_values_sig['alpha_sig_up']

    sig1_lo_sig_up = Property(Float)
    def _get_sig1_lo_sig_up(self):
        return self.princ_values_sig['sig1_lo_sig_up']

    m_sig_up = Property(Float)
    def _get_m_sig_up(self):
        return self.princ_values_sig['m_sig_up']

    n_sig_up = Property(Float)
    def _get_n_sig_up(self):
        return self.princ_values_sig['n_sig_up']

    m_sig2_up = Property(Float)
    def _get_m_sig2_up(self):
        return self.princ_values_sig['m_sig2_up']

    n_sig2_up = Property(Float)
    def _get_n_sig2_up(self):
        return self.princ_values_sig['n_sig2_up']

    # stresses lower face:
    #
    sigx_lo = Property(Float)
    def _get_sigx_lo(self):
        return self.princ_values_sig['sigx_lo']

    sigy_lo = Property(Float)
    def _get_sigy_lo(self):
        return self.princ_values_sig['sigy_lo']

    sigxy_lo = Property(Float)
    def _get_sigxy_lo(self):
        return self.princ_values_sig['sigxy_lo']

    sig1_lo = Property(Float)
    def _get_sig1_lo(self):
        return self.princ_values_sig['sig1_lo']

    sig2_lo = Property(Float)
    def _get_sig2_lo(self):
        return self.princ_values_sig['sig2_lo']

    alpha_sig_lo = Property(Float)
    def _get_alpha_sig_lo(self):
        return self.princ_values_sig['alpha_sig_lo']

    sig1_up_sig_lo = Property(Float)
    def _get_sig1_up_sig_lo(self):
        return self.princ_values_sig['sig1_up_sig_lo']

    m_sig_lo = Property(Float)
    def _get_m_sig_lo(self):
        return self.princ_values_sig['m_sig_lo']

    n_sig_lo = Property(Float)
    def _get_n_sig_lo(self):
        return self.princ_values_sig['n_sig_lo']

    m_sig2_lo = Property(Float)
    def _get_m_sig2_lo(self):
        return self.princ_values_sig['m_sig2_lo']

    n_sig2_lo = Property(Float)
    def _get_n_sig2_lo(self):
        return self.princ_values_sig['n_sig2_lo']

    #------------------------------------------
    # combinations of limit states, stress resultants and directions
    #------------------------------------------

    ls = Trait('ULS',
                {'ULS' : ULS,
                 'SLS' : SLS })

    ls_class = Instance(LimitState)
    def _ls_class_default(self):
        '''ls instances, e.g. ULS()
        '''
        ls_class = self.ls_
        return ls_class(ls_table=self)

    assess_value = Property
    def _get_assess_value(self):
        ls = self.ls_class
        return getattr(ls, ls.assess_name)

    traits_view = View(Tabbed(
                            Item('ls_class@' , label="ls", show_label=False),
                            scrollable=False,
                         ),
                      resizable=True,
                      scrollable=True,
                      height=1000,
                      width=1100
                      )
