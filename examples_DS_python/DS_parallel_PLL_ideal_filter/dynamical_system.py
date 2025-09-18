from numpy import sin, pi

variable_names = ["p1", "p2"]
parameter_names = ["g1", "g2", "k", "d"]
time = "t"

periodic_data={
    0:(-pi, 2*pi),
    1:(-pi, 2*pi)
}

def periodic_p1(t, y):
    i = 0
    x = y[i]
    offset, period = periodic_data[i]
    return sin(pi*(x-offset)/period)

def periodic_p2(t, y):
    i = 1
    x = y[i]
    offset, period = periodic_data[i]
    return sin(pi*(x-offset)/period)

periodic_events = [periodic_p1,
                   periodic_p2]

def ODEs(U, p, t):
    p1, p2 = U
    g1, g2, k, d = p
    return [g1 - sin(p1) - k * sin(p2), 
            g2 - sin(p2) - d * sin(p1)]