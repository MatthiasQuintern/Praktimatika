import numpy as np
import functions as fun

# Todo: eps0, u0, c, h, h_, ...
class Constant:
    def __init__(self, name, value, unit=None, latex=None, source=None):
        self.name = name
        self._value = value
        self.v = value
        self._unit = unit
        self._source = source

    def __repr__(self):
        if self._unit:
            return f"{self._value} {self._unit}"
        else:
            return str(self._value)

    def latex(self):
        if self.latex:
            return self.latex
        else:
            return f"No latex given for {self.name}"

    def get_source(self):
        if self._source:
            return self._source
        else:
            return f"No source given for {self.name}"

    def get_latex_source(self):
        """
        @online{self.name,
            % title={]
            % subtitle={}
            % organization = {}
            url = {self._source}
        }
        :return:
        """
        if self._source:
            return "@online{self.name,\n% title={}\n% subtitle={}\n% organization = {}\nurl = {self._source}\n}"


m_e = Constant("electron mass",
               9.1093837015e-31,
               unit="kg",
               latex=r"9.1093837015\cdot10^{-31}\,\si{\kg}",
               source="https://physics.nist.gov/cgi-bin/cuu/Value?me|search_for=electron+mass")






