import numpy as np
import functions as fun

# Todo: eps0, u0, c, h, h_, ...
from tools import tool, latex


class Constant:
    def __init__(self, name, value, unit=None, latex=None, source=None):
        self.name = name
        self._value = value
        self.v = value
        self._unit = unit
        self._source = source
        self._tex = latex

    def __repr__(self):
        if self._unit:
            return f"{self._value} {self._unit}"
        else:
            return str(self._value)

    def latex(self, dec_sep=","):
        if self._tex:
            return self._tex
        else:
            unit = ""
            if self._unit:
                unit = "\\,\\si{" + self._unit.replace("/", "\\per\\") + "}"
            return latex.number_to_latex(self._value, dec_sep) + unit

    def get_source(self):
        if self._source:
            return self._source
        else:
            return f"No source given for {self.name}"

    def get_latex_source(self):
        """
        @online{self.name,
            % title={}
            % subtitle={}
            % organization = {}
            url = {self._source}
        }
        :return:
        """
        if self._source:
            return "@online{+" + self.name.repalce(" ", "_") + \
                   "\n% title={}\n% subtitle={}\n% organization = {}" \
                   "\nurl = {" + self._source + "}\n}"


# MASSES

m_e = Constant("electron mass",
               9.1093837015e-31,
               unit="kg",
               latex=r"9.1093837015\cdot10^{-31}\,\si{\kg}",
               source="https://physics.nist.gov/cgi-bin/cuu/Value?me")

m_p = Constant("proton mass",
               1.67262192369e-27,
               unit="kg",
               source="https://physics.nist.gov/cgi-bin/cuu/Value?mp")

m_n = Constant("neutron mass",
               1.67492749804e-27,
               unit="kg",
               source="https://physics.nist.gov/cgi-bin/cuu/Value?mn")
#
# ELECTROMAGNETIC
#
mu_0 = Constant("vacuum magnetic permeability",
                1.25663706212e-6,
                unit="N/A^2",
                source="https://physics.nist.gov/cgi-bin/cuu/Value?mu0")

ep_0 = Constant("vacuum electric permittivity",
                8.8541878128e-12,
                unit="F/m^-1",
                source="https://www.physics.nist.gov/cgi-bin/cuu/Value?ep0")

e = Constant("elemtary charge",
             1.602176634e-27,
             unit="C",
             source="https://physics.nist.gov/cgi-bin/cuu/Value?e")

#
# UNIVERSAL
#
h = Constant("Planck constant",
             6.62607015e-34,
             unit="Js",
             source="https://physics.nist.gov/cgi-bin/cuu/Value?h")

h_eV = Constant("Planck constant",
                4.135667696e-15,
                unit="eVs",
                source="https://physics.nist.gov/cgi-bin/cuu/Value?hev")

c_0 = Constant("standard acceleration of gravity",
               299792458,
               unit="m/s",
               source="https://physics.nist.gov/cgi-bin/cuu/Value?c")

g_n = Constant("standard acceleration of gravity",
               9.80665,
               unit="m/s^2",
               source="https://physics.nist.gov/cgi-bin/cuu/Value?gn")

const_d = {
    # MASS
    "m_e": m_e,
    "m_p": m_p,
    "m_n": m_n,
    # ELECTROMAGNETIC
    "mu_0": mu_0,
    "ep_0": ep_0,
    "e": e,
    # UNIVERSAL
    "h": h,
    "h_eV": h_eV,
    "c_0": c_0,
    "g_n": g_n,
}
