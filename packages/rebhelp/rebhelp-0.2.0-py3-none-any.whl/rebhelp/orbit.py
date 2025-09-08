# rebhelp/orbits.py
import numpy as np

G = 6.6743e-20
period_const = 2 * np.pi / np.sqrt(G)
sma_const = np.cbrt(G / (4 * np.pi ** 2))

def sim_set(sim):
    G = sim.G
    period_const = 2 * np.pi / np.sqrt(G)
    sma_const = np.cbrt(G / (4 * np.pi ** 2))

def get_primary(particles):
    """Return the most massive particle (the primary)."""
    return max(particles, key=lambda p: p.m)

def dist(p1, p2):
    """Euclidean distance between two particles."""
    return np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)

def rel_vel(p1, p2):
    """Relative velocity of p2 w.r.t. p1."""
    return np.array([p2.vx - p1.vx, p2.vy - p1.vy, p2.vz - p1.vz])

def rel_speed(p1, p2):
    """Magnitude of relative velocity."""
    return np.linalg.norm(rel_vel(p1, p2))

def get_orbit(particles, obj):
    """
    Calculates an orbit based on a hierarchy tree.

    Assumptions:
    - One dominant primary body
    - S-type system: planets << star, moons << planets
    - Does not handle P-type circumbinary systems or equal-mass binaries

    Returns:
        (orbit, primary)
    """
    primary = get_primary(particles)

    # Remove primary, add object if needed
    particle_list = [p for p in particles if p != primary]
    if obj not in particle_list:
        particle_list.append(obj)

    # Hill radii relative to the primary
    hill_list = [
        p.orbit(primary).a * np.cbrt(p.m / (3*primary.m))
        for p in particle_list
    ]

    # Each particle starts as its own subsystem
    particle_subs = [[p] for p in particle_list]
    parents = particle_list[:]

    # Assign moons
    for i, p in enumerate(parents):
        if p is not None:  # not banned
            for j, q in enumerate(particle_list):
                if i != j and dist(p, q) < hill_list[i] and p.m > q.m:
                    particle_subs[i].append(q)
                    particle_subs[j] = [q]   # reset q's subsystem
                    parents[j] = None        # ban q from claiming moons

    # Case 1: obj still orbits the primary
    if obj in parents:
        return (obj.orbit(primary), primary)

    # Case 2: obj is inside a subsystem
    for sys in filter(lambda s: len(s) > 1, particle_subs):
        if obj in sys:
            return get_orbit(sys, obj)

def period(sma, primary):
    return period_const * np.sqrt(sma ** 3 / primary.m)

def period_no_const(sma, primary):
    return np.sqrt(sma ** 3 / primary.m)

def sma(period, primary):
    return sma_const * np.cbrt(period ** 2 * primary.m)

def sma_no_const(period, primary):
    return np.cbrt(period ** 2 * primary.m)

def periapsis(a, e):
    return a * (1 - e)

def apoapsis(a, e):
    return a * (1 + e)

def orbital_energy(p1, p2):
    """Return specific orbital energy of p2 relative to p1"""
    r = dist(p1, p2)
    v = rel_speed(p1, p2)
    return v ** 2 / 2 - G * p1.m / r

def v_esc(r, p):
    """Escape velocity at a distance r from a primary"""
    return np.sqrt(2 * G * p.m / r)

def v_circ(r, p):
    """Circular orbit velocity at a distance r from a primary"""
    return np.sqrt(G * p.m / r)

def vis_viva(a, r, p):
    """Calculates orbital speed using semi-major axis and distance from a primary"""
    return np.sqrt(G * p.m * (2 / r - 1 / a))

def v_peri(a, e, p):
    """Velocity at periapsis"""
    return vis_viva(a, periapsis(a, e), p)

def v_apo(a, e, p):
    """Velocity at apoapsis"""
    return vis_viva(a, apoapsis(a, e), p)