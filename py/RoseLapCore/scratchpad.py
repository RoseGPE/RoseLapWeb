from sympy.solvers import solve
from sympy import Symbol, sqrt

a_drag = Symbol('a_drag')
v0 = Symbol('v0')
n_tires = Symbol('n_tires')
tire_mu_x = Symbol('tire_mu_x')
mass = Symbol('mass')
g = Symbol('g')
a_down = Symbol('a_down')
tire_offset_x = Symbol('tire_offset_x')
tire_mu_y = Symbol('tire_mu_y')
tire_offset_y = Symbol('tire_offset_y')

print(solve(sqrt(1-(a_drag*v0**2/n_tires)**2/(tire_mu_x*((mass*g+a_down*v0**2)/n_tires) + tire_offset_x)**2)*tire_mu_y*((mass*g+a_down*v0**2)/n_tires) + tire_offset_y - a_drag*v0**2 , v0, implicit=True))