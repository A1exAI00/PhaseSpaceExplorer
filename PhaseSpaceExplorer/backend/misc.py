from scipy.optimize import fsolve
from scipy.differentiate import jacobian
from scipy.linalg import eig

from numpy import mean

def solve(ODEs, x0, pars):
    res = fsolve(lambda x: ODEs(x, pars, 0.0), x0, full_output=True)
    return (res[0], res[2]==1)

def eigenvalues_and_eigenvectors(ODEs, x0, pars):
    _jacobian = jacobian(lambda x: ODEs(x, pars, 0.0), x0).df
    res = eig(_jacobian)
    return (res[0], res[1])

def bring_value_in_bounds(value, offset, period):
    n_periods = 0
    while value - n_periods*period > offset+period:
        n_periods += 1
    while value - n_periods*period < offset:
        n_periods -=1
    return value - n_periods*period

def bring_vector_in_bounds(vec, offset, period):
    n_periods = 0
    avg = mean(vec)
    while avg - n_periods*period > offset+period:
        n_periods += 1
    while avg - n_periods*period < offset:
        n_periods -=1
    return vec.copy() - n_periods*period

def flatten(to_flatten:list):
    return [x for to_flatten_sub in to_flatten for x in to_flatten_sub]