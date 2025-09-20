from numpy import sin, pi

variable_names = ["x", "y", "z"]
parameter_names = ["σ", "r", "b"]
time = "t"

def ODEs(U, p, t):
    x, y, z = U
    sigma, r, b = p
    return [
        sigma*(y-x),
        x*(r-z) - y,
        x*y-b*z
    ]