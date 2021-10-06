from vpython import *


# GlowScript 2.7 VPython


# global variables to be used by the widgets
running = True
t = 0
m_s = 2000  # mass of the star
r_s = 2  # radius of the star
m_p = 1  # mass of the planet
r_p = 0.5  # radius of the planet
dt = 0.001  # time increment

"""class particle:
    def __init__(self, o_x, o_y, o_z, o_r, color, m_o):
        self.pos = vector(o_x, o_y, o_z)
        self.radius = o_r
        self.color = color,
        self.mass = m_o
        self.momentum = vector(0, 0, 0)
        self.make_trail = True"""


def initialise_objects():
    global star, planet, force_arrow_p, force_arrow_s

    star = sphere(pos=vector(0, 0, 0), radius=r_s, color=color.yellow,
                  mass=m_s, momentum=vector(0, 0, 0), make_trail=True, emissive=True, texture={'file':textures.metal})

    planet = sphere(pos=vector(0, 0, 10), radius=r_p,
                    mass=m_p, momentum=vector(10, 10, 0), make_trail=True, texture={'file':textures.earth})

    force_arrow_p = arrow(pos=planet.pos, color=color.green, axis=vector(0, 0, 0), emissive=True)
    force_arrow_s = arrow(pos=star.pos, color=color.red, axis=vector(0, 0, 0), emissive=True)

    local_light(pos=star.pos, color=color.white)

    scene.ambient = color.gray(0)

def restart_objects(b):
    global star, planet, m_s, r_s, m_p, r_p

    star.clear_trail()
    star.pos = vector(0, 0, 0)
    star.momentum = vector(0, 0, 0)
    m_s = 2000  # mass of the star
    r_s = 2
    scene.camera.follow(planet)
    planet.clear_trail()
    planet.pos = vector(0, 0, 10)
    planet.momentum = vector(10, 10, 0)
    m_p = 1
    r_p = 0.5




def button_startstop(b):
    global running
    if running:
        running = False
    else:
        running = True

    """if running:
        running = False
        b.text = 'RE-START'
        e_rstar.disabled = False
        e_mstar.disabled = False
        e_rplanet.disabled = False
        e_mplanet.disabled = False
    else:
        t = 0
        running = True
        b.text = 'STOP'
        e_rstar.disabled = True
        e_mstar.disabled = True
        e_rplanet.disabled = True
        e_mplanet.disabled = True"""


def edit_rstar(s):
    global r_s
    r_s = s.value
    star.radius = r_s



def edit_mstar(s):
    global m_s
    m_s = s.value
    star.mass = m_s


def edit_rplanet(s):
    global r_p
    r_p = s.value
    planet.radius = r_p


def edit_mplanet(s):
    global m_p
    m_p = s.value
    planet.mass = m_p


b_startstop = button(bind=button_startstop, text='STOP')
b_restart = button(bind=restart_objects, text='RESTART')
scene.append_to_caption('\nStar radius\n ')
e_rstar = slider(bind=edit_rstar, min=0, max=10)

# winput(bind=edit_rstar, disabled=True)

scene.append_to_caption('\nStar mass\n ')
e_mstar = slider(bind=edit_mstar, min=1000, max=10000)

scene.append_to_caption('\nPlanet radius\n ')
e_rplanet = slider(bind=edit_rplanet, min=0, max=10)
scene.append_to_caption('\nPlanet mass\n ')
e_mplanet = slider(bind=edit_mplanet, min=1, max=10)


# Started off initial code from
# Example vpython widgets
# https://www.glowscript.org/#/user/GlowScriptDemos/folder/Examples/program/ButtonsSlidersMenus-VPython
# https://www.glowscript.org/docs/VPythonDocs/controls.html
def gforce(p1, p2):
    global force_arrow_p, force_arrow_s
    # Modelled using euler cromer method
    # Calculate the gravitational force exerted on p1 by p2.
    G = 1  # Change to 6.67e-11 to use real-world values.
    # Calculate distance vector between p1 and p2.
    r_vec = p1.pos - p2.pos
    # Calculate magnitude of distance vector.
    r_mag = mag(r_vec)
    # Calcualte unit vector of distance vector.
    r_hat = r_vec / r_mag
    # Calculate force magnitude.
    force_mag = G * p1.mass * p2.mass / r_mag ** 2
    # Calculate force vector.
    force_vec = -force_mag * r_hat
    if p1 == planet:
        force_arrow_p.axis = -log(force_mag,4) * r_hat
    else:
        force_arrow_s.axis = -log(force_mag,4) * r_hat

    return force_vec


# Calculates the positions of the planet and star in the gravitational field
# We only have the formula to calculate the gravitational force and from that we
# need to derive the position of the objects at each time
# To do that we need the formulae to link the force to position, which we get via the momentum
#
# For PLANET
# p_planet = m_planet * v_planet = m_planet * Delta_d_planet/Delta_t
# this then gives the position of the planet that we want to draw:
# Delta_d_planet = (p_planet * Delta_t ) / m_planet
# d_planet_next - d_planet_current = (p_planet * Delta_t ) / m_planet
# this gives
# d_planet_next = d_planet_current = (p_planet * Delta_t ) / m_planet  (equation 1)
#
# To get the momentum we now that
# Delta_p_planet = f_planet * Delta_t
# p_planet_next - p_planet_current = f_planet * Delta_t
# p_planet_next = p_planet_current + f_planet * Delta_t     (equation 2)
#
# the same for STAR
def run1():
    global running, star, planet, t, m_s, r_s, m_p, r_p, dt

    initialise_objects()

    # init_objects()
    running = True
    # infinite loop for the planet movement
    while True:
        if running:
            # limit the animation rate
            rate(64)

            # Calculate forces.
            star.force = gforce(star, planet)
            planet.force = gforce(planet, star)

            # Update momenta using (equation 2)
            star.momentum = star.momentum + star.force * dt
            planet.momentum = planet.momentum + planet.force * dt

            # Update positions using (equation 1)
            star.pos = star.pos + (star.momentum * dt) / star.mass
            planet.pos = planet.pos + (planet.momentum * dt) / planet.mass
            force_arrow_p.pos = planet.pos
            force_arrow_s.pos = star.pos

            planet.rotate(angle=10 * dt, axis=vector(0, 1, 0))

            # increment time
            t = t + dt
