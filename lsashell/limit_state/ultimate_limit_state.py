'''
Created on 13. 4. 2014

@author: Vancikv
'''

from traits.api import \
    List, Float, Array, Property, cached_property

from traitsui.api import \
    View, Item, TabularEditor, VGroup, HGroup, Include

import numpy as np

from math import pi

from limit_state import \
    LimitState
    
from limit_state_array_adapter import \
    LSArrayAdapter

class ULS(LimitState):
    '''Ultimate limit state
    '''

    #--------------------------------------------------------
    # ULS: material parameters (Inputs)
    #--------------------------------------------------------

    #-------------------------
    # sfb-demonstrator
    #-------------------------

    ### 'eval_mode = princ_sig' ###
    #
    # tensile strength of the textile reinforcement [kN/m]
    # design value for SFB-demonstrator (used in 'eval_mode == princ_sig')
    # --> f_Rtex,0 = 6.87 MPa / 10. * 100cm * 6 cm / 12 layers = 34.3 kN/m
    #
    f_Rtex_0 = f_Rtex_90 = 34.3
    # with sig_Rd,0,flection = 7.95 MPa k_fl, evaluates to:
    k_fl = 1.15  # 7.95 / 6.87

    ### 'eval_mode = eta_comp' ###
    #
    # tensile composite strength in 0-direction [MPa]
    # derived applying EN-DIN 1990
    # F_t,exp,m = 103.4 kN # mean value tensile test
    # F_Rk,0 = 86.6 kN # characteristic value
    # F_Rd,0 = 86.6 kN / 1.5 = 57.7 kN # design value
    # sig_Rd,0,t = 57.7 / 14cm / 6cm = 6.87 MPa
    #
#    sig_comp_0_Rd = Float(6.87)

    ### 'eval_mode = eta_nm' ###
    #
    # design values for SFB-demonstrator on specimens with thickness 6 cm
    # evaluation of design values based on a log-normal distribution.
    # tensile resistance as obtained in tensile test (width = 0.14 m)
    #
    n_0_Rdt = 412.  # = 57.7 (=F_tRd)/ 0.14 ### [kN/m] ### 413.6 = 103.4 (mean value) / 0.14 * 0.84 / 1.5
    # compressive strength as obtained in cube test (edge length = 0.150 m) results in C55/67 with f_ck = 55 MPa
    #
    n_Rdc = 2200  # = ( 55 (=f_ck for C55/67) / 1.5 ) * 0.06 * 1000 ### [kN/m] ### 2980 = 74.5 (mean value cube)* 0.1 * (100. * 6.) / 1.5
    # bending strength as obtained in bending test (width = 0.20 m)
    #
#    m_0_Rd = 0.49382716 * 9.6  # = 1.93 (=M_Rd) / 0.20 ### [kNm/m] ### 9.8 = 3.5 (mean value)/ 0.20 * 0.84 / 1.5
    m_0_Rd = 9.6  # = 1.93 (=M_Rd) / 0.20 ### [kNm/m] ### 9.8 = 3.5 (mean value)/ 0.20 * 0.84 / 1.5

    #-------------------------
    # barrelshell
    #-------------------------

    ### 'eval_mode = princ_sig' ###
    #
    # 6 layers carbon:
    # sig_comp,Rd = 40 kN / 0.1m *0.84 / 1.5 = 11.2 MPa
    # --> f_Rtex,0 = 11.2 MPa / 10.(MPa/kN/cm**2) * 100cm * 2 cm / 6 layers = 37.3 kN/m/layer
#    f_Rtex_0 = f_Rtex_90 = 37.3 # corresponds to sig_comp,Rd = 10 MPa
#    k_fl = 1.46 # 29.8 MPa / 20.5 MPa
#    print 'NOTE: f_Rtex_0 = f_Rtex_90 = set to %g kN/m !' % (f_Rtex_0)
#    print 'NOTE: k_fl = set to %g [-] !' % (k_fl)

    # 6 layers AR-glas:
    # --> f_Rtex,0 = 5.8 MPa / 10.(MPa/kN/cm**2) * 100cm * 2 cm / 6 layers = 19.3 kN/m/layer
#    f_Rtex_0 = f_Rtex_90 = 19.3
#    k_fl = 1.77 # 27.3 MPa / 15.2 MPa

    ### 'eval_mode = eta_comp' ###
    #
    sig_comp_0_Rd = Float(10., input=True)

    # tensile composite strength in 90-direction [MPa]
    # use value of the 0-direction as conservative simplification:
    #
    sig_comp_90_Rd = sig_comp_0_Rd

    ### 'eval_mode = eta_nm' ###
    # compressive strength
    # take pure concrete values (design values)
    # f_cd = 38 MPa
    #
#    n_Rdc = 750. # = 38 * 0.1 * (100. * 2.) = 506.7 kN/m

    # 6 layers carbon: experimental values for barrelshell on specimens with thickness 2 cm and width 10 cm
#    n_0_Rdt = 41.1 / 0.1 # [kN/m] # 411 kN/m = tensile resistance as obtained in tensile test
#    m_0_Rd = (3.5 * 0.46 / 4. ) / 0.1 # [kNm/m]
#    print 'experimental values used for resistance values (no gamma)'

    # 6 layers carbon: design values for barrelshell on specimens with thickness 2 cm and width 10 cm
    # factor k_alpha_min is used if flag is set to True
    #
#    n_0_Rdt = 223. # [kN/m] # ZiE value
#    m_0_Rd = 1.7 # [kNm/m] # ZiE value

# #    n_0_Rdt = 41.1 / 0.1  * 0.84 / 1.5 # [kN/m] # 230 kN/m = tensile resistance as obtained in tensile test
# #    m_0_Rd = (3.5 * 0.46 / 4. ) / 0.1 * 0.84 / 1.5 # [kNm/m]
#
# #    # 6 layers carbon: minimal design values for barrelshell on specimens with thickness 2 cm and width 10 cm
# #    n_0_Rdt = 20. / 0.1 * 0.84 / 1.5 # [kN/m]
# #    m_0_Rd = (2.4 * 0.46 / 4. ) / 0.1 * 0.84 / 1.5 # [kNm/m]

#    # 6 layers AR-glas: minimal design values for barrelshell on specimens with thickness 2 cm and width 10 cm
#    n_0_Rdt = 23.8 * 0.7 / 0.1 * 0.84 / 1.5 # [kN/m]
#    m_0_Rd = (1.3 * 0.46 / 4. ) / 0.1 * 0.84 / 1.5 # [kNm/m]

    # assume the same strength in 90-direction (safe side);
    # simplification for deflection angle
    #
    n_90_Rdt = n_0_Rdt  # [kN/m]
    m_90_Rd = m_0_Rd  # [kNm/m]

    # ------------------------------------------------------------
    # ULS - derived params:
    # ------------------------------------------------------------

    # Parameters for the cracked state (GdT):
    # assumptions!

    # (resultierende statische Nutzhoehe)
    #
    d = Property(Float)
    def _get_d(self):
        return 0.75 * self.ls_table.thickness

    # distance from the center of gravity to the resulting reinforcement layer
    #
    zs = Property(Float)
    def _get_zs(self):
        return self.d - self.ls_table.thickness / 2.

    # inner cantilever
    #
    z = Property(Float)
    def _get_z(self):
        return 0.9 * self.d

    # ------------------------------------------------------------
    # ULS: outputs
    # ------------------------------------------------------------

    # sig1_lo -direction:
    #
    sig1_up_sig_lo = Property(Array)
    def _get_sig1_up_sig_lo(self):
        return self.ls_table.sig1_up_sig_lo

    m_sig_lo = Property(Array)
    def _get_m_sig_lo(self):
        return self.ls_table.m_sig_lo

    n_sig_lo = Property(Array)
    def _get_n_sig_lo(self):
        return self.ls_table.n_sig_lo

    m_sig2_lo = Property(Array)
    def _get_m_sig2_lo(self):
        return self.ls_table.m_sig2_lo

    n_sig2_lo = Property(Array)
    def _get_n_sig2_lo(self):
        return self.ls_table.n_sig2_lo

    # sig1_up -direction:
    #
    sig1_lo_sig_up = Property(Array)
    def _get_sig1_lo_sig_up(self):
        return self.ls_table.sig1_lo_sig_up

    m_sig_up = Property(Array)
    def _get_m_sig_up(self):
        return self.ls_table.m_sig_up

    n_sig_up = Property(Array)
    def _get_n_sig_up(self):
        return self.ls_table.n_sig_up

    m_sig2_up = Property(Array)
    def _get_m_sig2_up(self):
        return self.ls_table.m_sig2_up

    n_sig2_up = Property(Array)
    def _get_n_sig2_up(self):
        return self.ls_table.n_sig2_up

    #------------------------------------------------------------
    # choose evaluation mode to calculate the number of reinf-layers 'n_tex':
    #------------------------------------------------------------
    #
#    eval_mode = 'massivbau'
#    eval_mode = 'princ_sig_level_1'
    eval_mode = 'eta_nm'

    ls_values = Property(depends_on='+input')
    @cached_property
    def _get_ls_values(self):
        '''get the outputs for ULS
        '''
        #---------------------------------------------------------
        # conditions for case distinction
        # (-- pure tension -- bending -- compression --)
        # NOTE: based in all cases of 'eval_mode' on the direction of
        #       the maximum principle (tensile) stress
        #---------------------------------------------------------

        #----------------------------------------
        # upper side:
        #----------------------------------------

        # NOTE: the case zero stresses at both sides would be included more then once
        # irrelevant for real situations
        cond_s1u_ge_0 = self.sig1_up >= 0.  # tensile stress upper side
        cond_s1u_le_0 = self.sig1_up <= 0.  # compressive stress upper side
        cond_sl_ge_0 = self.sig1_lo_sig_up >= 0.  # corresponding tensile stress lower side
        cond_sl_le_0 = self.sig1_lo_sig_up <= 0.  # corresponding compressive stress lower side
        cond_s1u_gt_sl = abs(self.sig1_up) > abs(self.sig1_lo_sig_up)
        cond_s1u_lt_sl = abs(self.sig1_up) < abs(self.sig1_lo_sig_up)
        cond_s1u_eq_0 = self.sig1_up == 0.
        cond_sl_eq_0 = self.sig1_lo_sig_up == 0.

        # consider only cases for bending without zero stresses at both sides:
        #----------------------------------------
        cond_up_eq_0 = cond_s1u_eq_0 * cond_sl_eq_0
        cond_up_neq_0 = cond_up_eq_0 - True

        # tension upper side (sig1_up >= 0):
        #----------------------------------------
        #
        # caused by pure tension:
        #
        cond_up_t = cond_s1u_ge_0 * cond_sl_ge_0
        #
        # caused by bending:
        #
        cond_up_tb = cond_s1u_ge_0 * cond_sl_le_0 * cond_up_neq_0
        #
        # caused by bending and a normal tension:
        #
        cond_up_tb_t = cond_up_tb * cond_s1u_gt_sl * cond_up_neq_0
        #
        # caused by bending and a normal compression:
        #
        cond_up_tb_c = cond_up_tb * cond_s1u_lt_sl * cond_up_neq_0

        # compression upper side (sig1_up <= 0):
        #----------------------------------------
        #
        # caused by pure compression:
        #
        cond_up_c = cond_s1u_le_0 * cond_sl_le_0
        #
        # caused by bending:
        #
        cond_up_cb = cond_s1u_le_0 * cond_sl_ge_0

        #----------------------------------------
        # lower side:
        #----------------------------------------

        # NOTE: the case zero stresses at both sides would be included more then once
        # irrelevant for real situations
        cond_s1l_ge_0 = self.sig1_lo >= 0.  # tensile stress lower side
        cond_s1l_le_0 = self.sig1_lo <= 0.  # compressive stress lower side
        cond_su_ge_0 = self.sig1_up_sig_lo >= 0.  # corresponding tensile stress upper side
        cond_su_le_0 = self.sig1_up_sig_lo <= 0.  # corresponding compressive stress upper side
        cond_s1l_gt_su = abs(self.sig1_lo) > abs(self.sig1_up_sig_lo)
        cond_s1l_lt_su = abs(self.sig1_lo) < abs(self.sig1_up_sig_lo)
        cond_s1l_eq_0 = self.sig1_lo == 0.  # zero stresses at lower side
        cond_su_eq_0 = self.sig1_up_sig_lo == 0.  # corresponding zero stresses at upper side

        # consider only cases for bending without zero stresses at both sides:
        #----------------------------------------
        cond_lo_eq_0 = cond_s1l_eq_0 * cond_su_eq_0
        cond_lo_neq_0 = cond_lo_eq_0 - True

        # tension lower side (sig1_lo >= 0):
        #----------------------------------------
        #
        # caused by pure tension:
        #
        cond_lo_t = cond_s1l_ge_0 * cond_su_ge_0
        #
        # caused by bending:
        #
        cond_lo_tb = cond_s1l_ge_0 * cond_su_le_0 * cond_lo_neq_0
        #
        # caused by bending and a normal tension:
        #
        cond_lo_tb_t = cond_lo_tb * cond_s1l_gt_su * cond_lo_neq_0
        #
        # caused by bending and a normal compression:
        #
        cond_lo_tb_c = cond_lo_tb * cond_s1l_lt_su * cond_lo_neq_0

        # compression lower side (sig1_lo <= 0):
        #----------------------------------------
        #
        # caused by pure compression:
        #
        cond_lo_c = cond_s1l_le_0 * cond_su_le_0
        #
        # caused by bending:
        #
        cond_lo_cb = cond_s1l_le_0 * cond_su_ge_0

        # check if all elements are classified in one of the cases
        # 'bending, compression, tension' for the upper and the lower side
        # sum of all conditions must be equal to n_elems * 2 (for upper and lower side)
        #
#        print 'sum_lo', \
#                      self.sig1_lo[cond_lo_t].shape[0] + \
#                      self.sig1_lo[cond_lo_tb].shape[0] + \
#                      self.sig1_lo[cond_lo_c].shape[0] + \
#                      self.sig1_lo[cond_lo_cb].shape[0]
#        print 'sum_up', \
#                      self.sig1_lo[cond_up_t].shape[0] + \
#                      self.sig1_lo[cond_up_tb].shape[0] + \
#                      self.sig1_lo[cond_up_c].shape[0] + \
#                      self.sig1_lo[cond_up_cb].shape[0]

        #------------------------------------------------------------
        # get angel of deflection of the textile reinforcement
        #------------------------------------------------------------
        # angel of deflection of the textile reinforcement
        # distinguished between longitudinal (l) and transversal (q) direction,
        # i.e. 0- and 90-direction of the textile

        alpha_up = self.alpha_sig_up
        alpha_lo = self.alpha_sig_lo

        beta_l_up_deg = abs(alpha_up)  # [degree]
        beta_q_up_deg = 90. - abs(alpha_up)  # [degree]
        beta_l_up = beta_l_up_deg * pi / 180.  # [rad]
        beta_q_up = beta_q_up_deg * pi / 180.  # [rad]

        beta_l_lo_deg = abs(alpha_lo)  # [degree]
        beta_q_lo_deg = 90 - abs(alpha_lo)  # [degree]
        beta_l_lo = beta_l_lo_deg * pi / 180.  # [rad]
        beta_q_lo = beta_q_lo_deg * pi / 180.  # [rad]


        #-------------------------------------------------
        # VAR 1:use simplified reinforced concrete approach
        #-------------------------------------------------
        if self.eval_mode == 'massivbau':

            print 'eval_mode == "massivbau"'

            zs = self.zs
            z = self.z

            #---------------------------------------------------------
            # initialize arrays to be filled by case distinction:
            #---------------------------------------------------------
            #
            f_t_sig_up = np.zeros_like (self.sig1_up)  # [kN/m]
            f_t_sig_lo = np.zeros_like (self.sig1_up)  # [kN/m]
            k_fl_NM_up = np.ones_like (self.sig1_up)  # [-]
            k_fl_NM_lo = np.ones_like (self.sig1_up)  # [-]

            m_Eds = np.zeros_like (self.sig1_up)  # [kNm/m]
            e = np.zeros_like (self.sig1_up)  # [m]

            #---------------------------------------------------------
            # tension upper side (sig1_up > 0):
            #---------------------------------------------------------

            # pure tension case:
            #
            bool_arr = cond_up_t
            m = abs(self.m_sig_up[ bool_arr ])
            n = self.n_sig_up[ bool_arr ]
            # excentricity
            e[ bool_arr ] = abs(m / n)
            # in case of pure tension in the cross section:
            f_t_sig_up[ bool_arr ] = n * (zs[ bool_arr ] + e[ bool_arr ]) / (zs[ bool_arr ] + zs[ bool_arr ])

            # ## bending with tension at the upper side
            #
            bool_arr = cond_up_tb
            m = abs(self.m_sig_up[ bool_arr ])
            n = self.n_sig_up[ bool_arr ]
            # moment at the height of the resulting reinforcement layer:
            m_Eds[ bool_arr ] = abs(m) - zs[ bool_arr ] * n
            # tensile force in the reinforcement for bending and compression
            f_t_sig_up[ bool_arr ] = m_Eds[ bool_arr ] / z[ bool_arr ] + n

            #---------------------------------------------------------
            # compression upper side case (sig1_up < 0):
            #---------------------------------------------------------

            # @todo: remove as this is redundant:
            #
            bool_arr = cond_up_c
            f_t_sig_up[ bool_arr ] = 0.

            bool_arr = cond_up_cb
            f_t_sig_up[ bool_arr ] = 0.

            #---------------------------------------------------------
            # tension lower side (sig1_lo > 0):
            #---------------------------------------------------------

            # pure tension case:
            #
            bool_arr = cond_lo_t
            m = abs(self.m_sig_lo[ bool_arr ])
            n = self.n_sig_lo[ bool_arr ]
            # excentricity
            e[ bool_arr ] = abs(m / n)
            # in case of pure tension in the cross section:
            f_t_sig_lo[ bool_arr ] = n * (zs[ bool_arr ] + e[ bool_arr ]) / (zs[ bool_arr ] + zs[ bool_arr ])

            # ## bending with tension at the lower side
            #
            bool_arr = cond_lo_tb
            m = abs(self.m_sig_lo[ bool_arr ])
            n = self.n_sig_lo[ bool_arr ]
            # moment at the height of the resulting reinforcement layer:
            m_Eds[ bool_arr ] = abs(m) - zs[ bool_arr ] * n
            # tensile force in the reinforcement for bending and compression
            f_t_sig_lo[ bool_arr ] = m_Eds[ bool_arr ] / z[ bool_arr ] + n

            #---------------------------------------------------------
            # compression lower side case (sig1_lo < 0):
            #---------------------------------------------------------

            bool_arr = cond_lo_c
            f_t_sig_lo[ bool_arr ] = 0.

            bool_arr = cond_lo_cb
            f_t_sig_lo[ bool_arr ] = 0.

            #---------------------------------------------------------
            # resulting strength of the bi-directional textile considering the
            # deflection of the reinforcement in the loading direction
            # per reinforcement layer
            #---------------------------------------------------------
            #
            f_Rtex_0 = self.f_Rtex_0  # [kN/m/layer]
            f_Rtex_90 = self.f_Rtex_90
            f_Rtex_lo = f_Rtex_0 * np.cos(beta_l_lo) * (1 - beta_l_lo_deg / 90.) + \
                        f_Rtex_90 * np.cos(beta_q_lo) * (1 - beta_q_lo_deg / 90.)
            f_Rtex_up = f_Rtex_0 * np.cos(beta_l_up) * (1 - beta_l_up_deg / 90.) + \
                        f_Rtex_90 * np.cos(beta_q_up) * (1 - beta_q_up_deg / 90.)

            #------------------------------------------------------------
            # necessary number of reinforcement layers
            #------------------------------------------------------------
            # for the entire cross section (use symmetric arrangement of the upper and
            # lower reinforcement layers
            #
            n_tex_up = f_t_sig_up / f_Rtex_up
            n_tex_lo = f_t_sig_lo / f_Rtex_lo
            n_tex = 2 * np.max(np.hstack([ n_tex_up, n_tex_lo]), axis=1)[:, None]

            #------------------------------------------------------------
            # construct a dictionary containing the return values
            #------------------------------------------------------------
            return { 'e':e, 'm_Eds':m_Eds,
                     'cond_up_tb' : cond_up_tb * 1.0,
                     'cond_lo_tb' : cond_lo_tb * 1.0,
                     'f_t_sig_up' : f_t_sig_up,
                     'f_t_sig_lo' : f_t_sig_lo,
                     'beta_l_up':beta_l_up_deg, 'beta_q_up':beta_q_up_deg,
                     'beta_l_lo':beta_l_lo_deg, 'beta_q_lo':beta_q_lo_deg,
                     'f_Rtex_up':f_Rtex_up,
                     'f_Rtex_lo':f_Rtex_lo,
                     'n_tex_up':n_tex_up,
                     'n_tex_lo':n_tex_lo,
                     'n_tex':n_tex}


        #-------------------------------------------------
        # VAR 2:use principal stresses to calculate the resulting tensile force
        #-------------------------------------------------
        #
        if self.eval_mode == 'princ_sig_level_1':

            print "NOTE: the principle tensile stresses are used to evaluate 'n_tex'"
            # conservative evaluated based on a resulting tensile force of the composite cross section[kN/m]
            # derived from the maximum value of the tensile stresses at the top or the bottom of the cross section
            # i.e. sig1_max = min( 0, max( self.sig1_up, self.sig1_lo ) )

            # evaluation for upper side:
            #
            sig_comp_Ed_up = self.sig1_up

            #---------------------------------------------------------
            # initialize arrays to be filled by case distinction:
            #---------------------------------------------------------
            #
            f_t_sig_up = np.zeros_like (self.sig1_up)  # [kN/m]
            f_t_sig_lo = np.zeros_like (self.sig1_up)  # [kN/m]
            k_fl_NM_up = np.ones_like (self.sig1_up)  # [-]
            k_fl_NM_lo = np.ones_like (self.sig1_up)  # [-]

            #---------------------------------------------------------
            # tension upper side (sig1_up > 0):
            #---------------------------------------------------------
            # pure tension case:
            # (--> 'k_fl_NM' set to 1.0, i.e. no increase of resistance due to bending)
            #
            bool_arr = cond_up_t
            k_fl_NM_up[ bool_arr ] = 1.0
            f_t_sig_up[ bool_arr ] = self.sig1_up[ bool_arr ] * self.thickness[ bool_arr ] * 1000.

            # bending case with tension:
            # (sig_N > 0, i.e. 'sig1_up' results from bending and tension --> interpolate 'k_fl_NM')
            #
            bool_arr = cond_up_tb_t
            sig_b = (abs(self.sig1_up) + abs(self.sig1_lo_sig_up)) / 2
            k_fl_NM_up[ bool_arr ] = 1.0 + (self.k_fl - 1.0) * \
                                 (sig_b[ bool_arr ] / self.sig1_up[ bool_arr ])
            f_t_sig_up[ bool_arr ] = self.sig1_up[ bool_arr ] * self.thickness[ bool_arr ] * 1000.

            # bending case with compression:
            # (sig_N < 0, i.e. 'sig1_up' results only from bending --> full increase for 'k_fl_NM')
            #
            bool_arr = cond_up_tb_c
            sig_comp_Ed_up[ bool_arr ] = self.sig1_up[ bool_arr ]
            k_fl_NM_up[ bool_arr ] = self.k_fl
            f_t_sig_up[ bool_arr ] = self.sig1_up[ bool_arr ] * self.thickness[ bool_arr ] * 1000.

            #---------------------------------------------------------
            # compression upper side case (sig1_up < 0):
            #---------------------------------------------------------

            bool_arr = cond_up_c
            sig_comp_Ed_up[ bool_arr ] = 0.
            k_fl_NM_up[ bool_arr ] = 1.
            f_t_sig_up[ bool_arr ] = 0.

            bool_arr = cond_up_cb
            sig_comp_Ed_up[ bool_arr ] = 0.
            k_fl_NM_up[ bool_arr ] = 1.
            f_t_sig_up[ bool_arr ] = 0.

            #---------------------------------------------------------
            # tension lower side (sig1_lo > 0):
            #---------------------------------------------------------

            # evaluation for lower side:
            #
            sig_comp_Ed_lo = self.sig1_lo

            # pure tension case:
            # (--> 'k_fl_NM' set to 1.0, i.e. no increase of resistance due to bending)
            #
            bool_arr = cond_lo_t
            k_fl_NM_lo[ bool_arr ] = 1.0
            f_t_sig_lo[ bool_arr ] = self.sig1_lo[ bool_arr ] * self.thickness[ bool_arr ] * 1000.

            # bending case with tension:
            # (sig_N > 0, i.e. 'sig1_lo' results from bending and tension --> interpolate 'k_fl_NM')
            #
            bool_arr = cond_lo_tb_t
            sig_b = (abs(self.sig1_lo) + abs(self.sig1_up_sig_lo)) / 2
            k_fl_NM_lo[ bool_arr ] = 1.0 + (self.k_fl - 1.0) * \
                                 (sig_b[ bool_arr ] / self.sig1_lo[ bool_arr ])
            f_t_sig_lo[ bool_arr ] = self.sig1_lo[ bool_arr ] * self.thickness[ bool_arr ] * 1000.

            # bending case with compression:
            # (sig_N < 0, i.e. 'sig1_lo' results only from bending --> full increase for 'k_fl_NM')
            #
            bool_arr = cond_lo_tb_c
            k_fl_NM_lo[ bool_arr ] = self.k_fl
            f_t_sig_lo[ bool_arr ] = self.sig1_lo[ bool_arr ] * self.thickness[ bool_arr ] * 1000.

            #---------------------------------------------------------
            # compression lower side case (sig1_lo < 0):
            #---------------------------------------------------------

            bool_arr = cond_lo_c
            sig_comp_Ed_lo[ bool_arr ] = 0.
            k_fl_NM_lo[ bool_arr ] = 1.
            f_t_sig_lo[ bool_arr ] = 0.

            bool_arr = cond_lo_cb
            sig_comp_Ed_lo[ bool_arr ] = 0.
            k_fl_NM_lo[ bool_arr ] = 1.
            f_t_sig_lo[ bool_arr ] = 0.

            #---------------------------------------------------------
            # composite resitance stress
            #---------------------------------------------------------
            # @todo: check for general case
            # NOTE: needs information about the orientation of the reinforcement
            # works here only because of the simplification that the same resistance of the textile in 0- and 90-direction is assumed
            # and the reinforcement is arranged in the shell approximately orthogonal to
            # the global coordinate system
            #
            sig_comp_Rd_lo = self.sig_comp_0_Rd * np.cos(beta_l_lo) * (1 - beta_l_lo_deg / 90.) + \
                             self.sig_comp_90_Rd * np.cos(beta_q_lo) * (1 - beta_q_lo_deg / 90.)
            sig_comp_Rd_up = self.sig_comp_0_Rd * np.cos(beta_l_up) * (1 - beta_l_up_deg / 90.) + \
                             self.sig_comp_90_Rd * np.cos(beta_q_up) * (1 - beta_q_up_deg / 90.)

            #---------------------------------------------------------
            # ratio of the imposed stresses and the composite resistance
            #---------------------------------------------------------
            # NOTE: resistance is increased by factor 'k_fl_NM' if a bending case is evaluated
            #
            eta_comp_up = sig_comp_Ed_up / (sig_comp_Rd_up * k_fl_NM_up)
            eta_comp_lo = sig_comp_Ed_lo / (sig_comp_Rd_lo * k_fl_NM_lo)
            eta_comp = np.max(np.hstack([ eta_comp_up, eta_comp_lo]), axis=1)[:, None]

            #---------------------------------------------------------
            # resulting strength of the bi-directional textile considering the
            # deflection of the reinforcement in the loading direction
            # per reinforcement layer
            #---------------------------------------------------------
            #
            f_Rtex_0 = self.f_Rtex_0  # [kN/m/layer]
            f_Rtex_90 = self.f_Rtex_90
            f_Rtex_lo = f_Rtex_0 * np.cos(beta_l_lo) * (1 - beta_l_lo_deg / 90.) + \
                        f_Rtex_90 * np.cos(beta_q_lo) * (1 - beta_q_lo_deg / 90.)
            f_Rtex_up = f_Rtex_0 * np.cos(beta_l_up) * (1 - beta_l_up_deg / 90.) + \
                        f_Rtex_90 * np.cos(beta_q_up) * (1 - beta_q_up_deg / 90.)

            #---------------------------------------------------------
            # necessary number of reinforcement layers
            #---------------------------------------------------------
            # for the cases that stresses at the upper or lower face are taken into account
            # for the evaluation of the necessary number of reinforcement layers. 'n_tex' is the
            # maximum of the upper and lower face evaluation.
            # NOTE: resistance is increased by factor 'k_fl_NM' if a bending case is evaluated
            #
            n_tex_up = f_t_sig_up / (f_Rtex_up * k_fl_NM_up)
            n_tex_lo = f_t_sig_lo / (f_Rtex_lo * k_fl_NM_lo)

            # use a symmetric reinforcement layup at the top and at the bottom:
            #
            n_tex = np.max(np.hstack([ n_tex_up, n_tex_lo]), axis=1)[:, None]

            #------------------------------------------------------------
            # construct a dictionary containing the return values
            #------------------------------------------------------------
            return {
                     'cond_up_tb' : cond_up_tb * 1.0,
                     'cond_lo_tb' : cond_lo_tb * 1.0,
                     'f_t_sig_up' : f_t_sig_up,
                     'f_t_sig_lo' : f_t_sig_lo,
                     'beta_l_up':beta_l_up_deg, 'beta_q_up':beta_q_up_deg,
                     'beta_l_lo':beta_l_lo_deg, 'beta_q_lo':beta_q_lo_deg,
                     'sig_comp_Rd_up':sig_comp_Rd_up,
                     'sig_comp_Rd_lo':sig_comp_Rd_lo,
                     'eta_comp_up':eta_comp_up,
                     'eta_comp_lo':eta_comp_lo,
                     'eta_comp':eta_comp,
                     'f_Rtex_up':f_Rtex_up,
                     'k_fl_NM_up':k_fl_NM_up,
                     'f_Rtex_lo':f_Rtex_lo,
                     'k_fl_NM_lo':k_fl_NM_lo,
                     'n_tex_up':n_tex_up,
                     'n_tex_lo':n_tex_lo,
                     'n_tex':n_tex}


        if self.eval_mode == 'eta_nm':

            #-------------------------------------------------
            # VAR 3: NOTE: the principle tensile stresses are used to evaluate the principle direction\
            # 'eta_nm_tot' is evaluated based on linear nm-interaction (derived from test results)
            #-------------------------------------------------
            #
            print "NOTE: the principle tensile stresses are used to evaluate the deflection angle"
            print "      'eta_nm_tot' is evaluated based on linear nm-interaction (derived from test results)"

            # simplification of the transformation formula only valid for assumption of
            # arrangement of the textile reinforcement approximately orthogonal to the global coordinate system
            #
            n_Rdt_lo = self.n_0_Rdt * np.cos(beta_l_lo) * (1 - beta_l_lo_deg / 90.) + \
                       self.n_90_Rdt * np.cos(beta_q_lo) * (1 - beta_q_lo_deg / 90.)
            n_Rdt_up = self.n_0_Rdt * np.cos(beta_l_up) * (1 - beta_l_up_deg / 90.) + \
                       self.n_90_Rdt * np.cos(beta_q_up) * (1 - beta_q_up_deg / 90.)
            m_Rd_lo = self.m_0_Rd * np.cos(beta_l_lo) * (1 - beta_l_lo_deg / 90.) + \
                      self.m_90_Rd * np.cos(beta_q_lo) * (1 - beta_q_lo_deg / 90.)
            m_Rd_up = self.m_0_Rd * np.cos(beta_l_up) * (1 - beta_l_up_deg / 90.) + \
                      self.m_90_Rd * np.cos(beta_q_up) * (1 - beta_q_up_deg / 90.)
            n_Rdc = self.n_Rdc * np.ones_like(n_Rdt_lo)

            k_alpha_lo = np.cos(beta_l_lo) * (1 - beta_l_lo_deg / 90.) + \
                         np.cos(beta_q_lo) * (1 - beta_q_lo_deg / 90.)
            k_alpha_up = np.cos(beta_l_up) * (1 - beta_l_up_deg / 90.) + \
                         np.cos(beta_q_up) * (1 - beta_q_up_deg / 90.)

            if self.ls_table.k_alpha_min == True:
                print "minimum value 'k_alpha_min'=0.707 has been used to evaluate resistance values"
                # NOTE: conservative simplification: k_alpha_min = 0.707 used
                #
                n_Rdt_lo = n_Rdt_up = min(self.n_0_Rdt, self.n_90_Rdt) * 0.707 * np.ones_like(n_Rdt_lo)
                m_Rd_lo = m_Rd_up = min(self.m_0_Rd, self.m_90_Rd) * 0.707 * np.ones_like(m_Rd_lo)

            #----------------------------------------
            # caluclate eta_nm
            #----------------------------------------
            # destinguish the sign of the normal force

            #---------------
            # 1-direction:
            #---------------

            # initialize arrays to be filled based on case distinction
            #
            eta_n_up = np.zeros_like(self.n_sig_up)
            eta_n_lo = np.zeros_like(self.n_sig_lo)

            # cases with a tensile normal force
            #
            cond_nsu_ge_0 = self.n_sig_up >= 0.  # tensile force in direction of principle stress at upper side
            cond_nsl_ge_0 = self.n_sig_lo >= 0.  # tensile force in direction of principle stress at lower side

            # compare imposed tensile normal force with 'n_Rd,t' as obtained from tensile test
            #
            bool_arr = cond_nsu_ge_0
            eta_n_up[bool_arr] = self.n_sig_up[bool_arr] / n_Rdt_up[bool_arr]

            bool_arr = cond_nsl_ge_0
            eta_n_lo[bool_arr] = self.n_sig_lo[bool_arr] / n_Rdt_lo[bool_arr]

            # cases with a compressive normal force
            #
            cond_nsu_lt_0 = self.n_sig_up < 0.  # compressive force in direction of principle stress at upper side
            cond_nsl_lt_0 = self.n_sig_lo < 0.  # compressive force in direction of principle stress at lower side

            # compare imposed compressive normal force with 'n_Rdc' as obtained from compression test
            #
            bool_arr = cond_nsu_lt_0
            eta_n_up[bool_arr] = self.n_sig_up[bool_arr] / n_Rdc[bool_arr]

            bool_arr = cond_nsl_lt_0
            eta_n_lo[bool_arr] = self.n_sig_lo[bool_arr] / n_Rdc[bool_arr]

            # get 'eta_m' based on imposed moment compared with moment resistence
            # NOTE: use a linear increase factor for resistance moment based on reference thickness (= minimum thickness)
            #
            min_thickness = np.min(self.thickness)
            eta_m_lo = self.m_sig_lo / (m_Rd_lo * self.thickness / min_thickness)
            eta_m_up = self.m_sig_up / (m_Rd_up * self.thickness / min_thickness)

            # get total 'eta_mn' based on imposed normal force and moment
            # NOTE: if eta_n is negative (caused by a compressive normal force) take the absolute value
            # NOTE: if eta_m is negative (caused by a negative moment) take the absolute value
            #
            eta_nm_lo = np.abs(eta_n_lo) + np.abs(eta_m_lo)
            eta_nm_up = np.abs(eta_n_up) + np.abs(eta_m_up)

            # get maximum 'eta_mn' of both principle directions of upper and lower side
            #
            eta_nm1_tot = np.max(np.hstack([ eta_nm_up, eta_nm_lo]), axis=1)[:, None]

            #---------------
            # 2-direction:
            #---------------

            # initialize arrays to be filled based on case distinction
            #
            eta_n2_up = np.zeros_like(self.n_sig2_up)
            eta_n2_lo = np.zeros_like(self.n_sig2_lo)

            # cases with a tensile normal force
            #
            cond_ns2u_ge_0 = self.n_sig2_up >= 0.  # tensile force in direction of principle stress at upper side
            cond_ns2l_ge_0 = self.n_sig2_lo >= 0.  # tensile force in direction of principle stress at lower side

            # compare imposed tensile normal force with 'n_Rd,t' as obtained from tensile test
            #
            bool_arr = cond_ns2u_ge_0
            eta_n2_up[bool_arr] = self.n_sig2_up[bool_arr] / n_Rdt_up[bool_arr]

            bool_arr = cond_ns2l_ge_0
            eta_n2_lo[bool_arr] = self.n_sig2_lo[bool_arr] / n_Rdt_lo[bool_arr]

            # cases with a compressive normal force
            #
            cond_ns2u_lt_0 = self.n_sig2_up < 0.  # compressive force in direction of principle stress at upper side
            cond_ns2l_lt_0 = self.n_sig2_lo < 0.  # compressive force in direction of principle stress at lower side

            # compare imposed compressive normal force with 'n_Rdc' as obtained from compression test
            #
            bool_arr = cond_ns2u_lt_0
            eta_n2_up[bool_arr] = self.n_sig2_up[bool_arr] / n_Rdc[bool_arr]

            bool_arr = cond_ns2l_lt_0
            eta_n2_lo[bool_arr] = self.n_sig2_lo[bool_arr] / n_Rdc[bool_arr]

            # get 'eta_m' based on imposed moment compared with moment resistence
            # NOTE: use a linear increase factor for resistance moment based on reference thickness (= minimum thickness)
            #
            eta_m2_lo = self.m_sig2_lo / (m_Rd_lo * self.thickness / min_thickness)
            eta_m2_up = self.m_sig2_up / (m_Rd_up * self.thickness / min_thickness)

            # get total 'eta_mn' based on imposed normal force and moment
            # NOTE: if eta_n is negative (caused by a compressive normal force) take the absolute value
            # NOTE: if eta_m is negative (caused by a negative moment) take the absolute value
            #
            eta_nm2_lo = np.abs(eta_n2_lo) + np.abs(eta_m2_lo)
            eta_nm2_up = np.abs(eta_n2_up) + np.abs(eta_m2_up)

            # get maximum 'eta_mn' of both principle directions of upper and lower side
            #
            eta_nm2_tot = np.max(np.hstack([ eta_nm2_up, eta_nm2_lo]), axis=1)[:, None]

            # overall maximum eta_nm for 1st and 2nd principle direction
            #
            eta_nm_tot = np.max(np.hstack([ eta_nm1_tot, eta_nm2_tot]), axis=1)[:, None]

            # overall maximum eta_n and eta_m distinguishing normal forces and bending moment influence:
            #
            eta_n_tot = np.max(np.hstack([ eta_n_lo, eta_n2_lo, eta_n_up, eta_n2_up]), axis=1)[:, None]
            eta_m_tot = np.max(np.hstack([ eta_m_lo, eta_m2_lo, eta_m_up, eta_m2_up]), axis=1)[:, None]

            #------------------------------------------------------------
            # construct a dictionary containing the return values
            #------------------------------------------------------------
            return { 'beta_l_up':beta_l_up_deg,
                     'beta_q_up':beta_q_up_deg,
                     'beta_l_lo':beta_l_lo_deg,
                     'beta_q_lo':beta_q_lo_deg,
                     'n_Rdt_up':n_Rdt_up,
                     'n_Rdt_lo':n_Rdt_lo,
                     'm_Rd_up':m_Rd_up,
                     'm_Rd_lo':m_Rd_lo,

                     'eta_n_up':eta_n_up,
                     'eta_m_up':eta_m_up,
                     'eta_nm_up':eta_nm_up,
                     'eta_n_lo':eta_n_lo,
                     'eta_m_lo':eta_m_lo,
                     'eta_nm_lo':eta_nm_lo,
                     'eta_nm_tot':eta_nm_tot,

                     'eta_n_tot':eta_n_tot,
                     'eta_m_tot':eta_m_tot,

                     'eta_n2_up':eta_n2_up,
                     'eta_m2_up':eta_m2_up,
                     'eta_nm2_up':eta_nm2_up,
                     'eta_n2_lo':eta_n2_lo,
                     'eta_m2_lo':eta_m2_lo,
                     'eta_nm2_lo':eta_nm2_lo,

                     'k_alpha_lo' : k_alpha_lo,
                     'k_alpha_up' : k_alpha_up}


    #-----------------------------------------------
    # LS_COLUMNS: specify the properties that are displayed in the view
    #-----------------------------------------------

    if eval_mode == 'massivbau':

        assess_name = 'max_n_tex'

        ls_columns = List(['d', 'zs', 'z',
                            'e', 'm_Eds',
                            'f_t_sig_up', 'f_t_sig_lo',
                            'beta_l_up', 'beta_q_up',
                            'beta_l_lo', 'beta_q_lo',
                            'f_Rtex_up', 'f_Rtex_lo',
                            'n_tex_up', 'n_tex_lo',
                            'n_tex' ])

        e = Property(Array)
        def _get_e(self):
            return self.ls_values['e']

        m_Eds = Property(Array)
        def _get_m_Eds(self):
            return self.ls_values['m_Eds']

        # specify the material properties for the view:
        #
        plot_item_mpl = Item(name='f_Rtex_0', label='reinforcement strength per layer [kN/m]:  f_Rtex_0 ', style='readonly', format_str="%.1f")
        plot_item_mpt = Item(name='f_Rtex_90', label='reinforcement strength per layer [kN/m]:  f_Rtex_90 ', style='readonly', format_str="%.1f")


    elif eval_mode == 'princ_sig_level_1':

        # choose the assess parameter used for sorting
        # defined by the property name 'assess_name'
        #
#        assess_name = 'max_eta_comp'
        assess_name = 'max_n_tex'

        max_eta_comp = Property(depends_on='+input')
        @cached_property
        def _get_max_eta_comp(self):
            return np.max(self.eta_comp)

        max_n_tex = Property(depends_on='+input')
        @cached_property
        def _get_max_n_tex(self):
            return np.max(self.n_tex)

        ls_columns = List(['f_t_sig_up', 'f_t_sig_lo',
                            'beta_l_up', 'beta_q_up',
                            'beta_l_lo', 'beta_q_lo',
                            'f_Rtex_up', 'f_Rtex_lo',
                            'k_fl_NM_up', 'k_fl_NM_lo',
                            'eta_comp_up', 'eta_comp_lo', 'eta_comp',
                            'cond_up_tb', 'cond_lo_tb',
                            'n_tex_up', 'n_tex_lo', 'n_tex'])

        k_fl_NM_lo = Property(Array)
        def _get_k_fl_NM_lo(self):
            return self.ls_values['k_fl_NM_lo']

        k_fl_NM_up = Property(Array)
        def _get_k_fl_NM_up(self):
            return self.ls_values['k_fl_NM_up']

        k_fl_NM = Property(Array)
        def _get_k_fl_NM(self):
            return self.ls_values['k_fl_NM']

        eta_comp_up = Property(Array)
        def _get_eta_comp_up(self):
            return self.ls_values['eta_comp_up']

        eta_comp_lo = Property(Array)
        def _get_eta_comp_lo(self):
            return self.ls_values['eta_comp_lo']

        eta_comp = Property(Array)
        def _get_eta_comp(self):
            return self.ls_values['eta_comp']

        # specify the material properties for the view:
        #
        plot_item_mpl = Item(name='f_Rtex_0', label='reinforcement strength per layer [kN/m]:  f_Rtex_0 ', style='readonly', format_str="%.1f"), \
                        Item(name='sig_comp_0_Rd', label='composit tensile strength [MPa]:  sig_comp_0_Rd ', style='readonly', format_str="%.1f")

        plot_item_mpt = Item(name='f_Rtex_90', label='reinforcement strength per layer [kN/m]:  f_Rtex_90 ', style='readonly', format_str="%.1f"), \
                        Item(name='sig_comp_90_Rd', label='composit tensile strength [MPa]:  sig_comp_90_Rd ', style='readonly', format_str="%.1f")


    elif eval_mode == 'eta_nm':

        # choose the assess parameter used for sorting
        # defined by the property name 'assess_name'
        #
        assess_name = 'max_eta_nm_tot'

        max_eta_nm_tot = Property(depends_on='+input')
        @cached_property
        def _get_max_eta_nm_tot(self):
            return np.max(self.eta_nm_tot)

        ls_columns = List([  # 'alpha_up', 'alpha_lo'
                           'beta_l_up', 'beta_q_up', 'k_alpha_up',
                           'beta_l_lo', 'beta_q_lo', 'k_alpha_lo',
                           'n_Rdt_up', 'n_Rdt_lo',
                           'm_Rd_up', 'm_Rd_lo',
                           'eta_n_up', 'eta_m_up', 'eta_nm_up',
                           'eta_n_lo', 'eta_m_lo', 'eta_nm_lo',
                           'eta_n2_up', 'eta_m2_up', 'eta_nm2_up',
                           'eta_n2_lo', 'eta_m2_lo', 'eta_nm2_lo',
                           'eta_nm_tot'])

        # specify the material properties for the view:
        #
        plot_item_mpl = Item(name='n_0_Rdt', label='normal tensile strength [kN/m]:  n_0_Rdt ', style='readonly', format_str="%.1f"), \
                        Item(name='n_Rdc', label='normal compressive strength [kN/m]:  n_0_Rdc ', style='readonly', format_str="%.1f"), \
                        Item(name='m_0_Rd', label='bending strength [kNm/m]:  m_0_Rd ', style='readonly', format_str="%.1f")

        plot_item_mpt = Item(name='n_90_Rdt', label='normal tensile strength [kN/m]:  n_90_Rd ', style='readonly', format_str="%.1f"), \
                        Item(name='n_Rdc', label='normal compressive strength [kN/m]:  n_0_Rdc ', style='readonly', format_str="%.1f"), \
                        Item(name='m_90_Rd', label='bending strength [kNm/m]:  m_90_Rd ', style='readonly', format_str="%.1f")

#     alpha_1_up = Property(Array)
#     def _get_alpha_1_up(self):
#         return self.ls_values['alpha_1_up']
# 
#     alpha_2_up = Property(Array)
#     def _get_alpha_2_up(self):
#         return self.ls_values['alpha_2_up']

    beta_l_up = Property(Array)
    def _get_beta_l_up(self):
        return self.ls_values['beta_l_up']

    beta_q_up = Property(Array)
    def _get_beta_q_up(self):
        return self.ls_values['beta_q_up']

    beta_l_lo = Property(Array)
    def _get_beta_l_lo(self):
        return self.ls_values['beta_l_lo']

    beta_q_lo = Property(Array)
    def _get_beta_q_lo(self):
        return self.ls_values['beta_q_lo']

    #------------------------------------
    # eval == 'princ_sig_1' or
    # eval == 'massivbau'
    #------------------------------------

    f_Rtex_up = Property(Array)
    def _get_f_Rtex_up(self):
        return self.ls_values['f_Rtex_up']

    f_Rtex_lo = Property(Array)
    def _get_f_Rtex_lo(self):
        return self.ls_values['f_Rtex_lo']

    n_tex_up = Property(Array)
    def _get_n_tex_up(self):
        return self.ls_values['n_tex_up']

    n_tex_lo = Property(Array)
    def _get_n_tex_lo(self):
        return self.ls_values['n_tex_lo']

    n_tex = Property(Array)
    def _get_n_tex(self):
        return self.ls_values['n_tex']

    #------------------------------------
    # eval == 'eta_nm'
    #------------------------------------

    n_Rdt_up = Property(Array)
    def _get_n_Rdt_up(self):
        return self.ls_values['n_Rdt_up']

    n_Rdt_lo = Property(Array)
    def _get_n_Rdt_lo(self):
        return self.ls_values['n_Rdt_lo']

    m_Rd_up = Property(Array)
    def _get_m_Rd_up(self):
        return self.ls_values['m_Rd_up']

    m_Rd_lo = Property(Array)
    def _get_m_Rd_lo(self):
        return self.ls_values['m_Rd_lo']

    k_alpha_up = Property(Array)
    def _get_k_alpha_up(self):
        return self.ls_values['k_alpha_up']

    k_alpha_lo = Property(Array)
    def _get_k_alpha_lo(self):
        return self.ls_values['k_alpha_lo']

    # 1st-principle direction
    #
    eta_n_up = Property(Array)
    def _get_eta_n_up(self):
        return self.ls_values['eta_n_up']

    eta_m_up = Property(Array)
    def _get_eta_m_up(self):
        return self.ls_values['eta_m_up']

    eta_nm_up = Property(Array)
    def _get_eta_nm_up(self):
        return self.ls_values['eta_nm_up']

    eta_n_lo = Property(Array)
    def _get_eta_n_lo(self):
        return self.ls_values['eta_n_lo']

    eta_m_lo = Property(Array)
    def _get_eta_m_lo(self):
        return self.ls_values['eta_m_lo']

    eta_nm_lo = Property(Array)
    def _get_eta_nm_lo(self):
        return self.ls_values['eta_nm_lo']

    # max from 1st and 2nd-principle direction
    #
    eta_nm_tot = Property(Array)
    def _get_eta_nm_tot(self):
        return self.ls_values['eta_nm_tot']

    # max from 1st and 2nd-principle direction only from normal forces
    #
    eta_n_tot = Property(Array)
    def _get_eta_n_tot(self):
        return self.ls_values['eta_n_tot']

    # max from 1st and 2nd-principle direction only from bending moments
    #
    eta_m_tot = Property(Array)
    def _get_eta_m_tot(self):
        return self.ls_values['eta_m_tot']

    # 2nd-principle direction
    #
    eta_n2_up = Property(Array)
    def _get_eta_n2_up(self):
        return self.ls_values['eta_n2_up']

    eta_m2_up = Property(Array)
    def _get_eta_m2_up(self):
        return self.ls_values['eta_m2_up']

    eta_nm2_up = Property(Array)
    def _get_eta_nm2_up(self):
        return self.ls_values['eta_nm2_up']

    eta_n2_lo = Property(Array)
    def _get_eta_n2_lo(self):
        return self.ls_values['eta_n2_lo']

    eta_m2_lo = Property(Array)
    def _get_eta_m2_lo(self):
        return self.ls_values['eta_m2_lo']

    eta_nm2_lo = Property(Array)
    def _get_eta_nm2_lo(self):
        return self.ls_values['eta_nm2_lo']

    # @todo: make an automatised function calle for asses_value_max
#    @on_trait_change( '+input' )
#    def set_assess_name_max( self, assess_name ):
#        print 'set asses'
#        asses_value = ndmax( getattr( self, assess_name ) )
#        assess_name_max = 'max_' + assess_name
#        setattr( self, assess_name_max, asses_value )


    #-------------------------------
    # ls view
    #-------------------------------

    # @todo: the dynamic selection of the columns to be displayed
    # does not work in connection with the LSArrayAdapter
    traits_view = View(
                       VGroup(
                        HGroup(
                            VGroup(
                                plot_item_mpl,
                                label='material Properties (longitudinal)'
                                  ),
                            VGroup(
                                plot_item_mpt,
                                label='material Properties (transversal)'
                                  ),
                              ),
                        VGroup(
                            Include('ls_group'),
                            Item('ls_array', show_label=False,
                                  editor=TabularEditor(adapter=LSArrayAdapter()))
                              ),
                            ),
                      resizable=True,
                      scrollable=True,
                      height=1000,
                      width=1100
                      )
