import pymineos_

"""
TODO: document this module
"""


class MineosOutput:
    """
    """

    def __init__(self, m_out):
        if(not isinstance(m_out, pymineos_.MineosOutput)):
            raise TypeError("m_out constructor argument must be"
                            " a pymineos_.MineosOutput instance.")
        self._m_out = m_out

    @property
    def g(self):
        return self._m_out.getG()

    @property
    def c(self):
        return self._m_out.getC()

    @property
    def t(self):
        return self._m_out.getT()

    def __str__(self):
        return self._m_out.__str__()


class MineosInput:
    """
    """

    def __init__(self):
        self._m_in = pymineos_.MineosInput()
        self.model_set = False

    @property
    def r(self):
        for i in range(self.n):
            yield self._m_in.get_r(i)

    @property
    def rho(self):
        for i in range(self.n):
            yield self._m_in.get_rho(i)

    @property
    def vpv(self):
        for i in range(self.n):
            yield self._m_in.get_vpv(i)

    @property
    def vsv(self):
        for i in range(self.n):
            yield self._m_in.get_vsv(i)

    @property
    def qkappa(self):
        for i in range(self.n):
            yield self._m_in.get_qkappa(i)

    @property
    def qshear(self):
        for i in range(self.n):
            yield self._m_in.get_qshear(i)

    @property
    def vph(self):
        for i in range(self.n):
            yield self._m_in.get_vph(i)

    @property
    def vsh(self):
        for i in range(self.n):
            yield self._m_in.get_vsh(i)

    @property
    def eta(self):
        for i in range(self.n):
            yield self._m_in.get_eta(i)

    @property
    def n(self):
        return self._m_in.n

    @property
    def nic(self):
        return self._m_in.nic

    @property
    def noc(self):
        return self._m_in.noc

    def read_model(self, filepath):
        self._m_in.read_mod(filepath)
        self.model_set = True

    def set_model(self, nic: int, noc: int,
                  r: list, rho: list, vpv: list, vsv: list, qkappa: list,
                  qshear: list, vph: list, vsh: list, eta: list):
        self.set_mod(nic, noc, r, rho, vpv, vsv, qkappa, qshear, vph, vsh, eta)
        self.model_set = True


class Mineos:

    def __init__(self, mineos_in: MineosInput = None):
        if(mineos_in is None):
            self.mineos_in = MineosInput()
        else:
            self.mineos_in = mineos_in
        self.configured = False
        self.model_set = False

    def config(self, ifreq: int, nmode1: int, nmode2: int, jcom: int,
               rhobar: float, lmin: int, lmax: int, fmin: float, fmax:
               float):
        self.mineos_in._m_in.set_params(ifreq, int(nmode1), int(nmode2), jcom, rhobar,
                                        int(lmin), int(lmax), fmin, fmax)
        self.configured = True

    def read_model(self, filepath):
        self.mineos_in.read_model(filepath)

    def set_model(self, nic: int, noc: int,
                  r: list, rho: list, vpv: list, vsv: list, qkappa: list,
                  qshear: list, vph: list, vsh: list, eta: list):
        self.mineos_in.set_model(nic, noc, r, rho, vpv, vsv, qkappa, qshear,
                                 vph, vsh, eta)

    def calc(self):
        self._check_calc_precond()
        m_out = self.mineos_in._m_in.mineos()
        return MineosOutput(m_out)

    def calc_timeout(self, timeout):
        self._check_calc_precond()
        m_out = self.mineos_in._m_in.mineos_timeout(timeout)
        return MineosOutput(m_out)

    def _check_calc_precond(self):
        if(not self.mineos_in.model_set):
            raise Exception("Can't launch mineos calculation because the "
                            "input model is"
                            " not set, call set_model or read_model.")
        if(not self.configured):
            raise Exception("Can't launch mineos calculation because the input"
                            " parameters are not set, call config.")


def mineos(filepath: str, ifreq: int, nmode1: int, nmode2: int, jcom: int,
           rhobar: float, lmin: int, lmax: int, fmin: float, fmax: float):
    t, g, c, ncall = pymineos_.mineos(filepath, ifreq, nmode1, nmode2, jcom,
                                      rhobar, lmin, lmax, fmin, fmax)
    return t, g, c
