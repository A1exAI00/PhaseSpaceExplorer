from scipy.optimize import fsolve
from scipy.differentiate import jacobian
from scipy.linalg import eig

from numpy import mean, array, ndarray


def solve(ODEs, x0, pars):
    res = fsolve(lambda x: ODEs(x, pars, 0.0), x0, full_output=True)
    return (res[0], res[2] == 1)


def eigenvalues_and_eigenvectors(ODEs, x0, pars):
    _jacobian = jacobian(lambda x: ODEs(x, pars, 0.0), x0).df
    res = eig(_jacobian)
    return (res[0], res[1])


def translate_value_to_periodic_segment(
    value: int | float,
    offset: int | float,
    period: int | float
) -> int | float:
    """
    Translate any real value to periodic segment [offset, offset+period]
    so that value + period = value.

    Args:
        value: any real number
        offset: left (minimum) value of the segment, can be any real number
        period: length of the periodic segment, must be positive

    Returns:
        Translated value ∈ [offset, offset+period]
    """
    translated_value = (value-offset) % period + offset
    return translated_value


def translate_array_to_periodic_segment(
    vec: ndarray,
    offset: int | float,
    period: int | float
) -> int | float:
    """
    Translate vector as a whole to periodic segment [offset, offset+period]

    Args:
        vec: numpy 1D array
        offset: left (minimum) value of the segment, can be any real number
        period: length of the periodic segment, must be positive

    Returns:
        Translated vector
    """
    avg = mean(vec)
    n_periods = (avg-offset) // period
    translated_vector = vec.copy() - n_periods*period
    return translated_vector


def flatten(to_flatten):
    return [x for to_flatten_sub in to_flatten for x in to_flatten_sub]


################################################################################
# Tests

def test_translate_value_to_periodic_segment():
    assert translate_value_to_periodic_segment(10, 5, 2) == 6
    assert translate_value_to_periodic_segment(-10, 5, 2) == 6
    assert translate_value_to_periodic_segment(10, -5, 2) == -4
    assert translate_value_to_periodic_segment(-10, -5, 2) == -4


def test_translate_vector_to_periodic_segment():
    # Refactor to better compare arrays
    assert max(abs(translate_array_to_periodic_segment(
        array([7.5, 8.3, 8.9]), 5, 2) - array([5.5, 6.3, 6.9]))) < 1e-3
    assert max(abs(translate_array_to_periodic_segment(
        array([-7.5, -8.3, -8.9]), 5, 2) - array([6.5, 5.7, 5.1]))) < 1e-3
    assert max(abs(translate_array_to_periodic_segment(
        array([8.5, 9.5, 14.5]), 5, 2) - array([4.5, 5.5, 10.5]))) < 1e-3
    assert max(abs(translate_array_to_periodic_segment(
        array([8.5, 9.5, 11.5]), -5, 2) - array([-5.5, -4.5, -2.5]))) < 1e-3

def test_flatten():
    to_flatten = [[1,2,3], [4,5]]
    flattened = flatten(to_flatten)
    # print(flattened)
    assert flattened[0] == 1
    assert flattened[1] == 2
    assert flattened[2] == 3
    assert flattened[3] == 4
    assert flattened[4] == 5

    to_flatten = [[], [1,2,3]]
    flattened = flatten(to_flatten)
    # print(flattened)
    assert flattened[0] == 1
    assert flattened[1] == 2
    assert flattened[2] == 3

################################################################################
if __name__ == "__main__":
    test_translate_value_to_periodic_segment()
    test_translate_vector_to_periodic_segment()
    test_flatten()