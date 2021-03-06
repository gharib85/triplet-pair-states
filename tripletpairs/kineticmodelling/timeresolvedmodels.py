from ._base import TimeResolvedModel
import numpy as np


class MerrifieldExplicit1TT(TimeResolvedModel):
    r"""
    A class for time-resolved simulations using a modified version of Merrifield's model.
    
    The model explicity includes the :math:`^1(TT)` state, and allows for decay
    of a single triplet in a :math:`(T..T)` state.
    
    Attributes
    ----------
    states : list of str
        The names of the excited state species.
    rates : list of str
        The names of the different rate constants in the model.
    model_name : str
        The name of the model.
    initial_state : str
        The name of the photoexcited state.
    G : float
        The exciton generation rate for :attr:`MerrifieldExplicit1TT.initial_state`. Units of per volume per time.
    t : numpy.ndarray
        1D array of time points for which to solve the rate equations.
    kGEN : float
        The rate at which :attr:`MerrifieldExplicit1TT.initial_state` is populated. Units of per time.
    kSF : float
        Rate constant for :math:`S_1\rightarrow ^1(TT)`. Units of per time.
    k_SF : float
        Rate constant for :math:`^1(TT)\rightarrow S_1`. Units of per time.
    kHOP : float
        Rate constant for :math:`^1(TT)\rightarrow (T..T)`. Units of per time.
    k_HOP : float
        Rate constant for :math:`(T..T)\rightarrow ^1(TT)`. Units of per time.
    kHOP2 : float
        Rate constant for :math:`(T..T)\rightarrow2\times T_1`. Units of per time.
    kTTA : float
        Rate constant for :math:`2\times T_1\rightarrow (T..T) or ^1(TT) or S_1`. See :attr:`MerrifieldExplicit1TT.TTA_channel`. Units of volume per time.
    kRELAX : float
        Rate constant for mixing between the :math:`(T..T)` states. Units of per time.
    kSSA : float
        Singlet-singlet annihilation rate constant. Units of volume per time.
    kSNR : float
        Rate constant for the decay of :math:`S_1`. Units of per time.
    kTTNR : float
        Rate constant for the decay of :math:`^1(TT)`. Units of per time.
    kTNR : float
        Rate constant for the decay of :math:`T_1`, or one of the triplets in :math:`(T..T)`. Units of per time.
    cslsq : numpy.ndarray
        1D array containing the overlap factors between the 9 :math:`(T..T)` states and the singlet.
    TTA_channel : int
        Index determining the fate of free triplets. 1 gives :math:`2\times T_1\rightarrow (T..T)`. 2 gives :math:`2\times T_1\rightarrow ^1(TT)`. 3 gives :math:`2\times T_1\rightarrow S_1`.
    simulation_results : dict
        Produced by :meth:`simulate`. Keys are the excited-state names (str), values the simulated populations (numpy.ndarray).
        
    """
    
    def __init__(self):
        super().__init__()
        # metadata
        self.model_name = 'MerrifieldExplicit1TT'
        self._number_of_states = 12
        self.states = ['S1', 'TT', 'T_T_total', 'T1']
        self.rates = ['kGEN', 'kSF', 'k_SF', 'kHOP', 'k_HOP', 'kHOP2', 'KTTA', 'kRELAX', 'kSNR', 'kSSA', 'kTTNR', 'kTNR']
        # rates between excited states
        self.kSF = 20.0
        self.k_SF = 0.03
        self.kHOP = 0.067
        self.k_HOP = 2.5e-4
        self.kHOP2 = 1e-5
        self.kTTA = 1e-18
        # spin relaxation
        self.kRELAX = 0
        # rates of decay
        self.kSNR = 0.1
        self.kSSA = 0
        self.kTTNR = 0.067
        self.kTNR = 1e-5
        # TTA channel
        self.TTA_channel = 1
        # cslsq values
        self.cslsq = (1/9)*np.ones(9)

    def _rate_equations(self, y, t):
        GS, S1, TT, T_T_1, T_T_2, T_T_3, T_T_4, T_T_5, T_T_6, T_T_7, T_T_8, T_T_9, T1 = y
        dydt = np.zeros(self._number_of_states+1)
        # GS
        dydt[0] = -(self._kGENS+self._kGENT)*GS
        # S1
        dydt[1] = self._kGENS*GS - (self.kSNR+self.kSF)*S1 - self.kSSA*S1*S1 + self.k_SF*TT + self._kTTA_3*T1**2
        # TT
        dydt[2] = self.kSF*S1 - (self.k_SF+self.kTTNR+self.kHOP*np.sum(self.cslsq))*TT + self.k_HOP*(self.cslsq[0]*T_T_1+self.cslsq[1]*T_T_2+self.cslsq[2]*T_T_3+self.cslsq[3]*T_T_4+self.cslsq[4]*T_T_5+self.cslsq[5]*T_T_6+self.cslsq[6]*T_T_7+self.cslsq[7]*T_T_8+self.cslsq[8]*T_T_9) + self._kTTA_2*T1**2
        # T_T_1
        dydt[3] = self.kHOP*self.cslsq[0]*TT - (self.k_HOP*self.cslsq[0]+self.kTNR+self.kHOP2+self.kRELAX)*T_T_1 + (1/9)*self._kTTA_1*T1**2 + (1/8)*self.kRELAX*(T_T_2+T_T_3+T_T_4+T_T_5+T_T_6+T_T_7+T_T_8+T_T_9)
        # T_T_2
        dydt[4] = self.kHOP*self.cslsq[1]*TT - (self.k_HOP*self.cslsq[1]+self.kTNR+self.kHOP2+self.kRELAX)*T_T_2 + (1/9)*self._kTTA_1*T1**2 + (1/8)*self.kRELAX*(T_T_1+T_T_3+T_T_4+T_T_5+T_T_6+T_T_7+T_T_8+T_T_9)
        # T_T_3
        dydt[5] = self.kHOP*self.cslsq[2]*TT - (self.k_HOP*self.cslsq[2]+self.kTNR+self.kHOP2+self.kRELAX)*T_T_3 + (1/9)*self._kTTA_1*T1**2 + (1/8)*self.kRELAX*(T_T_1+T_T_2+T_T_4+T_T_5+T_T_6+T_T_7+T_T_8+T_T_9)
        # T_T_4
        dydt[6] = self.kHOP*self.cslsq[3]*TT - (self.k_HOP*self.cslsq[3]+self.kTNR+self.kHOP2+self.kRELAX)*T_T_4 + (1/9)*self._kTTA_1*T1**2 + (1/8)*self.kRELAX*(T_T_1+T_T_2+T_T_3+T_T_5+T_T_6+T_T_7+T_T_8+T_T_9)
        # T_T_5
        dydt[7] = self.kHOP*self.cslsq[4]*TT - (self.k_HOP*self.cslsq[4]+self.kTNR+self.kHOP2+self.kRELAX)*T_T_5 + (1/9)*self._kTTA_1*T1**2 + (1/8)*self.kRELAX*(T_T_1+T_T_2+T_T_3+T_T_4+T_T_6+T_T_7+T_T_8+T_T_9)
        # T_T_6
        dydt[8] = self.kHOP*self.cslsq[5]*TT - (self.k_HOP*self.cslsq[5]+self.kTNR+self.kHOP2+self.kRELAX)*T_T_6 + (1/9)*self._kTTA_1*T1**2 + (1/8)*self.kRELAX*(T_T_1+T_T_2+T_T_3+T_T_4+T_T_5+T_T_7+T_T_8+T_T_9)
        # T_T_7
        dydt[9] = self.kHOP*self.cslsq[6]*TT - (self.k_HOP*self.cslsq[6]+self.kTNR+self.kHOP2+self.kRELAX)*T_T_7 + (1/9)*self._kTTA_1*T1**2 + (1/8)*self.kRELAX*(T_T_1+T_T_2+T_T_3+T_T_4+T_T_5+T_T_6+T_T_8+T_T_9)
        # T_T_8
        dydt[10] = self.kHOP*self.cslsq[7]*TT - (self.k_HOP*self.cslsq[7]+self.kTNR+self.kHOP2+self.kRELAX)*T_T_8 + (1/9)*self._kTTA_1*T1**2 + (1/8)*self.kRELAX*(T_T_1+T_T_2+T_T_3+T_T_4+T_T_5+T_T_6+T_T_7+T_T_9)
        # T_T_9
        dydt[11] = self.kHOP*self.cslsq[8]*TT - (self.k_HOP*self.cslsq[8]+self.kTNR+self.kHOP2+self.kRELAX)*T_T_9 + (1/9)*self._kTTA_1*T1**2 + (1/8)*self.kRELAX*(T_T_1+T_T_2+T_T_3+T_T_4+T_T_5+T_T_6+T_T_7+T_T_8)
        # T1
        dydt[12] = self._kGENT*GS + (self.kTNR+(2.0*self.kHOP2))*(T_T_1+T_T_2+T_T_3+T_T_4+T_T_5+T_T_6+T_T_7+T_T_8+T_T_9) - 2*self._kTTA_1*T1**2 - 2*self._kTTA_2*T1**2 - 2*self._kTTA_3*T1**2 - self.kTNR*T1
        #
        return dydt
    
    def _set_tta_rates(self):
        if self.TTA_channel == 1:  # this is T1 + T1 -> (T..T)
            self._kTTA_1 = self.kTTA
            self._kTTA_2 = 0
            self._kTTA_3 = 0
        elif self.TTA_channel == 2:  # this is T1 + T1 -> (TT)
            self._kTTA_1 = 0
            self._kTTA_2 = self.kTTA
            self._kTTA_3 = 0
        elif self.TTA_channel == 3:  # this is T1 + T1 -> S1
            self._kTTA_1 = 0
            self._kTTA_2 = 0
            self._kTTA_3 = self.kTTA
        else:
            raise ValueError('TTA channel must be either 1, 2 or 3')
        return
            
    def _initialise_simulation(self):
        self._set_tta_rates()
        self._set_initial_condition()
        self._set_generation_rates()
        return

    def _unpack_simulation(self, y):
        self.S1 = y[:, 1]
        self.TT = y[:, 2]
        self.T_T_total = np.sum(y[:, 3:12], axis=1)
        self.T1 = y[:, -1]
        self._wrap_simulation_results()
        return
    
    def _wrap_simulation_results(self):
        self.simulation_results = dict(zip(self.states, [self.S1, self.TT, self.T_T_total, self.T1]))
        return
      

class Merrifield(TimeResolvedModel):
    r"""
    A class for steady-state simulations using Merrifield's model.
    
    Attributes
    ----------
    states : list of str
        The names of the excited state species.
    rates : list of str
        The names of the different rate constants in the model.
    model_name : str
        The name of the model.
    initial_state : str
        The name of the photoexcited state.
    G : float
        The exciton generation rate for :attr:`Merrifield.initial_state`. Units of per volume per time.
    t : numpy.ndarray
        1D array of time points for which to solve the rate equations.
    kGEN : float
        The rate at which :attr:`Merrifield.initial_state` is populated. Units of per time.
    kSF : float
        Rate constant for :math:`S_1\rightarrow (TT)`. Units of per time.
    k_SF : float
        Rate constant for :math:`(TT)\rightarrow S_1`. Units of per time.
    kDISS : float
        Rate constant for :math:`(TT)\rightarrow2\times T_1`. Units of per time.
    kTTA : float
        Rate constant for :math:`2\times T_1\rightarrow (TT)`. Units of volume per time.
    kRELAX : float
        Rate constant for mixing between the :math:`(T..T)` states. Units of per time.
    kSSA : float
        Singlet-singlet annihilation rate constant. Units of volume per time.
    kSNR : float
        Rate constant for the decay of :math:`S_1`. Units of per time.
    kTTNR : float
        Rate constant for the decay of :math:`(TT)`. Units of per time.
    kTNR : float
        Rate constant for the decay of :math:`T_1`. Units of per time.
    cslsq : numpy.ndarray
        1D array containing the overlap factors between the 9 :math:`(T..T)` states and the singlet.
    simulation_results : dict
        Produced by :meth:`simulate`. Keys are the excited-state names (str), values the simulated populations (numpy.ndarray).
        
    """
    
    def __init__(self):
        super().__init__()
        # metadata
        self.model_name = 'Merrifield'
        self._number_of_states = 11
        self.states = ['S1', 'TT_bright', 'TT_total', 'T1']
        self.rates = ['kGEN', 'kSF', 'k_SF', 'kDISS', 'KTTA', 'kRELAX', 'kSNR', 'kSSA', 'kTTNR', 'kTNR']
        # rates between excited states
        self.kSF = 20.0
        self.k_SF = 0.03
        self.kDISS = 0.067
        self.kTTA = 1e-18
        # spin relaxation (Bardeen addition - not in original Merrifield)
        self.kRELAX = 0
        # rates of decay
        self.kSNR = 0.1
        self.kSSA = 0
        self.kTTNR = 0.067
        self.kTNR = 1e-5
        # cslsq values
        self.cslsq = (1/9)*np.ones(9)

    def _rate_equations(self, y, t):
        GS, S1, TT_1, TT_2, TT_3, TT_4, TT_5, TT_6, TT_7, TT_8, TT_9, T1 = y
        dydt = np.zeros(self._number_of_states+1)
        # GS
        dydt[0] = -(self._kGENS+self._kGENT)*GS
        # S1
        dydt[1] = self._kGENS*GS - (self.kSNR+self.kSF*np.sum(self.cslsq))*S1 -self.kSSA*S1*S1+ self.k_SF*(self.cslsq[0]*TT_1+self.cslsq[1]*TT_2+self.cslsq[2]*TT_3+self.cslsq[3]*TT_4+self.cslsq[4]*TT_5+self.cslsq[5]*TT_6+self.cslsq[6]*TT_7+self.cslsq[7]*TT_8+self.cslsq[8]*TT_9)
        # TT_1
        dydt[2] = self.kSF*self.cslsq[0]*S1 - (self.k_SF*self.cslsq[0]+self.kDISS+self.kTTNR+self.kRELAX)*TT_1 + (1/9)*self.kTTA*T1*T1 + (1/8)*self.kRELAX*(TT_2+TT_3+TT_4+TT_5+TT_6+TT_7+TT_8+TT_9)
        # TT_2
        dydt[3] = self.kSF*self.cslsq[1]*S1 - (self.k_SF*self.cslsq[1]+self.kDISS+self.kTTNR+self.kRELAX)*TT_2 + (1/9)*self.kTTA*T1*T1 + (1/8)*self.kRELAX*(TT_1+TT_3+TT_4+TT_5+TT_6+TT_7+TT_8+TT_9)
        # TT_3
        dydt[4] = self.kSF*self.cslsq[2]*S1 - (self.k_SF*self.cslsq[2]+self.kDISS+self.kTTNR+self.kRELAX)*TT_3 + (1/9)*self.kTTA*T1*T1 + (1/8)*self.kRELAX*(TT_1+TT_2+TT_4+TT_5+TT_6+TT_7+TT_8+TT_9)
        # TT_4
        dydt[5] = self.kSF*self.cslsq[3]*S1 - (self.k_SF*self.cslsq[3]+self.kDISS+self.kTTNR+self.kRELAX)*TT_4 + (1/9)*self.kTTA*T1*T1 + (1/8)*self.kRELAX*(TT_1+TT_2+TT_3+TT_5+TT_6+TT_7+TT_8+TT_9)
        # TT_5
        dydt[6] = self.kSF*self.cslsq[4]*S1 - (self.k_SF*self.cslsq[4]+self.kDISS+self.kTTNR+self.kRELAX)*TT_5 + (1/9)*self.kTTA*T1*T1 + (1/8)*self.kRELAX*(TT_1+TT_2+TT_3+TT_4+TT_6+TT_7+TT_8+TT_9)
        # TT_6
        dydt[7] = self.kSF*self.cslsq[5]*S1 - (self.k_SF*self.cslsq[5]+self.kDISS+self.kTTNR+self.kRELAX)*TT_6 + (1/9)*self.kTTA*T1*T1 + (1/8)*self.kRELAX*(TT_1+TT_2+TT_3+TT_4+TT_5+TT_7+TT_8+TT_9)
        # TT_7
        dydt[8] = self.kSF*self.cslsq[6]*S1 - (self.k_SF*self.cslsq[6]+self.kDISS+self.kTTNR+self.kRELAX)*TT_7 + (1/9)*self.kTTA*T1*T1 + (1/8)*self.kRELAX*(TT_1+TT_2+TT_3+TT_4+TT_5+TT_6+TT_8+TT_9)
        # TT_8
        dydt[9] = self.kSF*self.cslsq[7]*S1 - (self.k_SF*self.cslsq[7]+self.kDISS+self.kTTNR+self.kRELAX)*TT_8 + (1/9)*self.kTTA*T1*T1 + (1/8)*self.kRELAX*(TT_1+TT_2+TT_3+TT_4+TT_5+TT_6+TT_7+TT_9)
        # TT_9
        dydt[10] = self.kSF*self.cslsq[8]*S1 - (self.k_SF*self.cslsq[8]+self.kDISS+self.kTTNR+self.kRELAX)*TT_9 + (1/9)*self.kTTA*T1*T1 + (1/8)*self.kRELAX*(TT_1+TT_2+TT_3+TT_4+TT_5+TT_6+TT_7+TT_8)
        # T1
        dydt[11] = self._kGENT*GS + 2.0*self.kDISS*(TT_1+TT_2+TT_3+TT_4+TT_5+TT_6+TT_7+TT_8+TT_9) - 2.0*self.kTTA*T1*T1 - self.kTNR*T1
        #
        return dydt

    def _unpack_simulation(self, y):
        self.S1 = y[:, 1]
        self.TT_bright = self.cslsq[0]*y[:, 2] + self.cslsq[1]*y[:, 3] + self.cslsq[2]*y[:, 4] + self.cslsq[3]*y[:, 5] + self.cslsq[4]*y[:, 6] + self.cslsq[5]*y[:, 7] + self.cslsq[6]*y[:, 8] + self.cslsq[7]*y[:, 9] + self.cslsq[8]*y[:, 10]
        self.TT_total = np.sum(y[:, 2:11], axis=1)
        self.T1 = y[:, -1]
        self._wrap_simulation_results()
        return
    
    def _wrap_simulation_results(self):
        self.simulation_results = dict(zip(self.states, [self.S1, self.TT_bright, self.TT_total, self.T1]))
        return
        

class Bardeen(TimeResolvedModel):
    r"""
    A class for steady-state simulations using a modified version of Merrifield's model.
    
    The model does not include free triplets. Instead Merrifield's :math:`(TT)`
    states can separate to form 9 :math:`(T..T)` states which can undergo spin
    relaxation. This is an approximation to triplet-diffusion in the limit of
    low excitation density.
    
    Attributes
    ----------
    states : list of str
        The names of the excited state species.
    rates : list of str
        The names of the different rate constants in the model.
    model_name : str
        The name of the model.
    initial_state : str
        The name of the photoexcited state.
    G : float
        The exciton generation rate for :attr:`Bardeen.initial_state`. Units of per volume per time.
    t : numpy.ndarray
        1D array of time points for which to solve the rate equations.
    kGEN : float
        The rate at which :attr:`Bardeen.initial_state` is populated. Units of per time.
    kSF : float
        Rate constant for :math:`S_1\rightarrow (TT)`. Units of per time.
    k_SF : float
        Rate constant for :math:`(TT)\rightarrow S_1`. Units of per time.
    kHOP : float
        Rate constant for :math:`(TT)\rightarrow (T..T)`. Units of per time.
    k_HOP : float
        Rate constant for :math:`(T..T)\rightarrow (TT)`. Units of per time.
    kRELAX : float
        Rate constant for mixing between the :math:`(T..T)` states. Units of per time.
    kSSA : float
        Singlet-singlet annihilation rate constant. Units of volume per time.
    kSNR : float
        Rate constant for the decay of :math:`S_1`. Units of per time.
    kTTNR : float
        Rate constant for the decay of :math:`(TT)`. Units of per time.
    kSPIN : float
        Rate constant for the decay of :math:`(T..T)`. Units of per time.
    cslsq : numpy.ndarray
        1D array containing the overlap factors between the 9 :math:`(T..T)` states and the singlet.
    simulation_results : dict
        Produced by :meth:`simulate`. Keys are the excited-state names (str), values the simulated populations (numpy.ndarray).
        
    """
    
    def __init__(self):
        super().__init__()
        # metadata
        self.model_name = 'Bardeen'
        self._number_of_states = 19
        self.states = ['S1', 'TT_bright', 'TT_total', 'T_T_total']
        self.rates = ['kGEN', 'kSF', 'k_SF', 'kHOP', 'k_HOP', 'kRELAX', 'kSNR', 'kSSA', 'kTTNR', 'kSPIN']
        self._allowed_initial_states = {'S1'}
        # rates between excited states
        self.kSF = 20.0
        self.k_SF = 0.03
        self.kHOP = 0.067
        self.k_HOP = 2.5e-4
        # spin relaxation
        self.kRELAX = 0.033
        # rates of decay
        self.kSNR = 0.1
        self.kSSA =0
        self.kTTNR = 0.067
        self.kSPIN = 2.5e-4
        # cslsq values
        self.cslsq = (1/9)*np.ones(9)

    def _rate_equations(self, y, t):
        GS, S1, TT_1, TT_2, TT_3, TT_4, TT_5, TT_6, TT_7, TT_8, TT_9, T_T_1, T_T_2, T_T_3, T_T_4, T_T_5, T_T_6, T_T_7, T_T_8, T_T_9 = y
        dydt = np.zeros(self._number_of_states+1)
        # GS
        dydt[0] = -self._kGEN*GS
        # S1
        dydt[1] = self._kGEN*GS - (self.kSNR+self.kSF*np.sum(self.cslsq))*S1 -self.kSSA*S1*S1 + self.k_SF*(self.cslsq[0]*TT_1+self.cslsq[1]*TT_2+self.cslsq[2]*TT_3+self.cslsq[3]*TT_4+self.cslsq[4]*TT_5+self.cslsq[5]*TT_6+self.cslsq[6]*TT_7+self.cslsq[7]*TT_8+self.cslsq[8]*TT_9)
        # TT_1
        dydt[2] = self.kSF*self.cslsq[0]*S1 - (self.k_SF+self.kTTNR)*self.cslsq[0]*TT_1 - self.kHOP*TT_1 + self.k_HOP*T_T_1
        # TT_2
        dydt[3] = self.kSF*self.cslsq[1]*S1 - (self.k_SF+self.kTTNR)*self.cslsq[1]*TT_2 - self.kHOP*TT_2 + self.k_HOP*T_T_2
        # TT_3
        dydt[4] = self.kSF*self.cslsq[2]*S1 - (self.k_SF+self.kTTNR)*self.cslsq[2]*TT_3 - self.kHOP*TT_3 + self.k_HOP*T_T_3
        # TT_4
        dydt[5] = self.kSF*self.cslsq[3]*S1 - (self.k_SF+self.kTTNR)*self.cslsq[3]*TT_4 - self.kHOP*TT_4 + self.k_HOP*T_T_4
        # TT_5
        dydt[6] = self.kSF*self.cslsq[4]*S1 - (self.k_SF+self.kTTNR)*self.cslsq[4]*TT_5 - self.kHOP*TT_5 + self.k_HOP*T_T_5
        # TT_6
        dydt[7] = self.kSF*self.cslsq[5]*S1 - (self.k_SF+self.kTTNR)*self.cslsq[5]*TT_6 - self.kHOP*TT_6 + self.k_HOP*T_T_6
        # TT_7
        dydt[8] = self.kSF*self.cslsq[6]*S1 - (self.k_SF+self.kTTNR)*self.cslsq[6]*TT_7 - self.kHOP*TT_7 + self.k_HOP*T_T_7
        # TT_8
        dydt[9] = self.kSF*self.cslsq[7]*S1 - (self.k_SF+self.kTTNR)*self.cslsq[7]*TT_8 - self.kHOP*TT_8 + self.k_HOP*T_T_8
        # TT_9
        dydt[10] = self.kSF*self.cslsq[8]*S1 - (self.k_SF+self.kTTNR)*self.cslsq[8]*TT_9 - self.kHOP*TT_9 + self.k_HOP*T_T_9
        # T_T_1
        dydt[11] = self.kHOP*TT_1 - (self.k_HOP+self.kSPIN+self.kRELAX)*T_T_1 + (1/8)*self.kRELAX*(T_T_2+T_T_3+T_T_4+T_T_5+T_T_6+T_T_7+T_T_8+T_T_9)
        # T_T_2
        dydt[12] = self.kHOP*TT_2 - (self.k_HOP+self.kSPIN+self.kRELAX)*T_T_2 + (1/8)*self.kRELAX*(T_T_1+T_T_3+T_T_4+T_T_5+T_T_6+T_T_7+T_T_8+T_T_9)
        # T_T_3
        dydt[13] = self.kHOP*TT_3 - (self.k_HOP+self.kSPIN+self.kRELAX)*T_T_3 + (1/8)*self.kRELAX*(T_T_1+T_T_2+T_T_4+T_T_5+T_T_6+T_T_7+T_T_8+T_T_9)
        # T_T_4
        dydt[14] = self.kHOP*TT_4 - (self.k_HOP+self.kSPIN+self.kRELAX)*T_T_4 + (1/8)*self.kRELAX*(T_T_1+T_T_2+T_T_3+T_T_5+T_T_6+T_T_7+T_T_8+T_T_9)
        # T_T_5
        dydt[15] = self.kHOP*TT_5 - (self.k_HOP+self.kSPIN+self.kRELAX)*T_T_5 + (1/8)*self.kRELAX*(T_T_1+T_T_2+T_T_3+T_T_4+T_T_6+T_T_7+T_T_8+T_T_9)
        # T_T_6
        dydt[16] = self.kHOP*TT_6 - (self.k_HOP+self.kSPIN+self.kRELAX)*T_T_6 + (1/8)*self.kRELAX*(T_T_1+T_T_2+T_T_3+T_T_4+T_T_5+T_T_7+T_T_8+T_T_9)
        # T_T_7
        dydt[17] = self.kHOP*TT_7 - (self.k_HOP+self.kSPIN+self.kRELAX)*T_T_7 + (1/8)*self.kRELAX*(T_T_1+T_T_2+T_T_3+T_T_4+T_T_5+T_T_6+T_T_8+T_T_9)
        # T_T_8
        dydt[18] = self.kHOP*TT_8 - (self.k_HOP+self.kSPIN+self.kRELAX)*T_T_8 + (1/8)*self.kRELAX*(T_T_1+T_T_2+T_T_3+T_T_4+T_T_5+T_T_6+T_T_7+T_T_9)
        # T_T_9
        dydt[19] = self.kHOP*TT_9 - (self.k_HOP+self.kSPIN+self.kRELAX)*T_T_9 + (1/8)*self.kRELAX*(T_T_1+T_T_2+T_T_3+T_T_4+T_T_5+T_T_6+T_T_7+T_T_8)
        #
        return dydt

    def _unpack_simulation(self, y):
        self.GS = y[:, 0]
        self.S1 = y[:, 1]
        self.TT_bright = self.cslsq[0]*y[:, 2] + self.cslsq[1]*y[:, 3] + self.cslsq[2]*y[:, 4] + self.cslsq[3]*y[:, 5] + self.cslsq[4]*y[:, 6] + self.cslsq[5]*y[:, 7] + self.cslsq[6]*y[:, 8] + self.cslsq[7]*y[:, 9] + self.cslsq[8]*y[:, 10]
        self.TT_total = np.sum(y[:, 2:11], axis=1)
        self.T_T_total = np.sum(y[:, 11:], axis=1)
        self._wrap_simulation_results()
        return
    
    def _wrap_simulation_results(self):
        self.simulation_results = dict(zip(self.states, [self.S1, self.TT_bright, self.TT_total, self.T_T_total]))
        return
