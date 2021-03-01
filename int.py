import numpy as np

# a.bc in grad a=1°=0.50

def skt_to_deg(vec):
    """
    param: vec  numpy array/liste mit u,skt werten
    return:     numpy array in grad
    """
    out = np.zeros(len(vec))
    for i in range(len(vec)):
        nk = (vec[i] - int(vec[i])) * 2     # *2 da 50 skt = 1° und nicht 100 skt = 1 °
        out[i] = int(vec[i]) + nk
    return out
