variable_names = ["u", "y", "z"]
parameter_names = ["E", "delta", "eps", "c"]
time = "t"

a0 = -0.0014491777067221945
a1 = 0.4047903610420292
a2 = -8.814345521066247
a3 = 94.05841173048864
a4 = -593.8071165028581
a5 = 2362.6810193881056
a6 = -5964.114570853057
a7 = 9209.238555278202
a8 = -7889.603353342613
a9 = 2861.212170878973

an = [a0, a1, a2, a3, a4, a5, a6, a7, a8, a9]

f = lambda x: sum([an[i]*x**(i) for i in range(len(an))])

def ODEs(U, p, t):
    u, y, z = U
    E, delta, eps, c = p
    return [y, 
            eps*c*y - E - z + delta*u + f(u),
            z/c + delta*y]