from numpy import sin, pi

variable_names = ["phi", "y"]
parameter_names = ["g", "mu"]
time = "t"

periodic_data={
    0:[-pi, 2*pi]
}

def ODEs(U, p, t):
    phi, y = U
    g, mu = p
    return [y, g - mu*y - sin(phi)]