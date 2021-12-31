import vpython as vp
import numpy as np
import particles

class SolarSystem:
    def __init__(self):
        self.time = 0
        self.delta_time = 1.0E-1

        # Initialised value of newtons gravitational constant, 6.67e-11 to use real-world value.
        self.G = 1

        self.focus = 0  # index in particlelist to the planet that the planet follows
        self.running = False
        self.particlelist = []
        self.veditlist = []
        self.valslist = []
        self.shininess = 1000
        self.radius = 200

        self.texture = "https://images.unsplash.com/photo-1475274047050-1d0c0975c63e?ixid=MnwxMjA3fDB8MHxzZWFyY2h8MXx8bm" \
                       "lnaHQlMjBza3l8ZW58MHx8MHx8&ixlib=rb-1.2.1&w=1000&q=80"

        vp.scene.width = 1000
        vp.scene.height = 400
        vp.scene.range = 12
        vp.scene.lights = []

        # add the sun to scene
        self.add_sun()

        # Controls for the user interface
        # TODO: add description to each button for clarity
        vp.scene.append_to_caption('\n\n')

        # - start/stop the simulation
        self.b_startstop = vp.button(bind=self.button_startstop,
                                     text="▶️"
                                     )
        vp.scene.append_to_caption('  ')


        # - cycle through the planet that the camera follows
        self.b_camera = vp.button(bind=self.camera_follow,
                                  text='SWITCH CAMERA FOCUS'
                                  )
        vp.scene.append_to_caption('  ')

        # - toggle the visibility of the trails
        self.b_trails = vp.button(bind=self.button_trails,
                                    text='TOGGLE TRAILS'
                                    )
        vp.scene.append_to_caption('  ')

        # - toggle the drawing of gravitational force vectors
        self.c_force = vp.checkbox(bind=self.checkbox_force_arrows,
                                   text='HIDE FORCES'
                                   )
        vp.scene.append_to_caption('  ')

        # - toggles the drawing of velocity vectors
        self.c_velocity = vp.checkbox(bind=self.checkbox_velocity_arrows,
                                      text='HIDE VELOCITIES'
                                      )
        vp.scene.append_to_caption('\n\n')

        # - sets the level of ambient light
        self.s_ambientlight = vp.slider(bind=self.slider_ambient_lights,
                                        min=0,
                                        max=1,
                                        left=0,
                                        length=200,
                                        value=0.5
                                        )
        vp.scene.append_to_caption('Ambient light   | ')

        # - allow to change the value for G
        self.w_big_g_value = vp.winput(bind=self.winput_g,
                                       text=1
                                       )
        vp.scene.append_to_caption("  Gravitational constant G; real value: 6.67e-11")

        vp.scene.append_to_caption('\n\n══════════════════════════════════════════════════════════════════════════\n\n')

        self.b_save = vp.button(bind=self.button_save,
                                text='SAVE SYSTEM'
                                )
        self.b_load = vp.button(bind=self.button_load,
                                text='LOAD SYSTEM'
                                )
        self.b_restart = vp.button(bind=self.button_restart,
                                   text='RESTART'
                                   )

        vp.scene.append_to_caption('\n\n')

        self.b_add = vp.button(bind=self.button_add,
                               text='ADD PLANET')

        self.b_delete = vp.button(bind=self.button_delete,
                               text='DELETE PLANET')
        vp.scene.append_to_caption('\n\n')
        # vp.scene.append_to_caption('\n')
        # self.t_edit = vp.wtext(text='')
        # self.v_edit = vp.winput(bind=self.set_value, prompt='', text='', disabled=True, visible=False)
        # vp.scene.append_to_caption('\n')

    def add_sun(self):
        sun = particles.Sun(position=vp.vector(0, 0, 0),
                            radius=10, mass=10000,
                            velocity=vp.vector(0, 0, 0),
                            color=vp.color.yellow,
                            texture=vp.textures.metal
                            )
        self.particlelist.append(sun)


    def button_startstop(self, b):
        if len(self.particlelist) > 1:
            # toggles the running state
            self.running = not self.running
            if self.running:
                self.b_startstop.text = '⏸️'
            else:
                self.b_startstop.text = "▶️"


    def camera_follow(self, b):
        # set focus to the next particle on the list (circular)
        if self.focus + 1 < len(self.particlelist):
            self.focus += 1
        else:
            self.focus = 0

    def update_velocity_arrow(self, particle):
        if ( (not particle.particle_model.mass == 0)
              and (not vp.mag(particle.particle_model.momentum) == 0) ):
            particle.velocity_arrow.axis = (vp.log(
                vp.mag(particle.particle_model.momentum) / particle.particle_model.mass,
                10) + particle.particle_model.radius) * (particle.particle_model.momentum / vp.mag(
                particle.particle_model.momentum))
        particle.velocity_arrow.pos = particle.particle_model.pos

    def button_trails(self, b):
        # toggles the drawing of the trails
        for p in self.particlelist:
            p.particle_model.make_trail = not p.particle_model.make_trail
            p.particle_model.clear_trail()

    def checkbox_force_arrows(self, b):
        # toggles the drawing of the force vectors
        for p in self.particlelist:
            p.force_arrow.visible = not p.force_arrow.visible

    def checkbox_velocity_arrows(self, b):
        # toggles the drawing of the velocity vectors
        for p in self.particlelist:
            p.velocity_arrow.visible = not p.velocity_arrow.visible

    def slider_ambient_lights(self, s):
        # sets the value of the ambient light to the slider value
        vp.scene.ambient = vp.color.gray(s.value)

    def winput_g(self, w):
        # sets the value of G to the user input only is integer
        if type(w.number) == int:
            self.G = w.number

    def stop_simulation(self):
        self.running = False
        self.b_startstop.text = "▶️"

    def button_add(self, b):
        # only allow up to 9 planets
        if len(self.particlelist) < 10:

            self.button_restart(0)
            self.b_load.delete()

            # get the number of current, minus 1 because the first particle is the sun
            nplanets = len(self.particlelist) - 1
            sunradius = self.particlelist[0].radius
            sunmass = self.particlelist[0].mass
            # initial x position one more star radius away from the star than previous planet
            xpos = sunradius*(nplanets + 2)
            position = vp.vector(xpos, 0, 0)
            # initial y velocity
            zvelocity = np.sqrt((self.G * sunmass)/xpos)
            velocity = vp.vector(0, 0, zvelocity)
            # the name of the planet always has the last character the planet index
            indexplanet = nplanets + 1
            radius = 1
            mass = 1
            self.add_planet(indexplanet, position, velocity, radius, mass)
        else:
            b.delete()

    def add_planet(self, index, position, velocity, radius, mass):
        name = 'Planet ' + str(index)
        planet = particles.Planet(position=position,
                                  radius=1, mass=1,
                                  velocity=velocity,
                                  color=vp.color.white,
                                  texture=vp.textures.earth,
                                  name=name)

        self.particlelist.append(planet)
        vp.scene.append_to_caption('\n' + name + ' ')
        # each choice has the first 4 characters the variable and the last character the planet index
        self.m_edit = vp.menu(choices=['Choose what to edit for ' + name,
                                       'xpos ' + name,
                                       'ypos ' + name,
                                       'zpos ' + name,
                                       'xvel ' + name,
                                       'yvel ' + name,
                                       'zvel ' + name,
                                       'rad  ' + name,
                                       'mass ' + name,
                                       ],
                                       bind=self.menu_edit)
        t_edit = vp.wtext(text='')
        v_edit = vp.winput(bind=self.set_value, prompt='', text='first choose the variable', disabled=True, visible=False)
        self.veditlist.append(v_edit)
        valstext = self.particlelist[index].get_valstext()
        v_text = vp.wtext(text=valstext)
        self.valslist.append(v_text)

    def button_delete(self):
        if len(self.particlelist) > 1:
            d_particle = self.particlelist[-1]
            d_particle.particle_model.visible = False
            d_particle.force_arrow.visible = False
            d_particle.velocity_arrow.visible = False
            self.particlelist.pop()



    def set_value(self, i):
        if type(i.number) == int:
            # the variable to set is given by the first characters of the prompt
            var = i.prompt[:4]
            # the index of the planet is given by the last character of the prompt
            index = int(i.prompt[-1])
            if var == "xpos":
                self.particlelist[index].position0.x = i.number
            elif var == "ypos":
                self.particlelist[index].position0.y = i.number
            elif var == "zpos":
                self.particlelist[index].position0.z = i.number
            if var == "xvel":
                self.particlelist[index].velocity0.x = i.number
            elif var == "yvel":
                self.particlelist[index].velocity0.y = i.number
            elif var == "zvel":
                self.particlelist[index].velocity0.z = i.number
            elif var == "rad ":
                self.particlelist[index].radius = i.number
            elif var == "mass":
                self.particlelist[index].mass = i.number
            for p in self.particlelist:
                p.reset_model()
            # valstext = self.assign_valstext(index)
            valstext = self.particlelist[index].get_valstext()
            self.valslist[index - 1].text = valstext

    def menu_edit(self, m):
        # the index of the planet is given by the last character of the selection
        index = int(m.selected[-1])
        if m.index > 0:
            # the variable to set is given by the first 4 characters of the selection
            var = m.selected[:4]
            # set the prompt for the corresponding vedit to the selection
            # the prompt[:4] then gives the variable to set and prompt[-1] then gives the planet index
            self.veditlist[index - 1].prompt = m.selected
            if var == "xpos":
                self.veditlist[index - 1].text = self.particlelist[index].position0.x
            elif var == "ypos":
                self.veditlist[index - 1].text = self.particlelist[index].position0.y
            elif var == "zpos":
                self.veditlist[index - 1].text = self.particlelist[index].position0.z
            elif var == "xvel":
                self.veditlist[index - 1].text = self.particlelist[index].velocity0.x
            elif var == "yvel":
                self.veditlist[index - 1].text = self.particlelist[index].velocity0.y
            elif var == "zvel":
                self.veditlist[index - 1].text = self.particlelist[index].velocity0.z
            elif var == "rad ":
                self.veditlist[index - 1].text = self.particlelist[index].radius
            elif var == "mass":
                self.veditlist[index - 1].text = self.particlelist[index].mass
            self.veditlist[index - 1].visible = True
        else:
            self.veditlist[index - 1].text = 'first choose the variable'


    def button_save(self):
        vals = []
        for p in self.particlelist[1:]:
            vals.append(p.get_vals())
        np.savetxt("solar_system.csv", vals, delimiter=",")

    def button_load(self):
        allvals = np.genfromtxt("solar_system.csv", delimiter=",")

        for index, vals in enumerate(allvals):
            position = vp.vector(vals[0], vals[1], vals[2])
            velocity = vp.vector(vals[3], vals[4], vals[5])
            radius = vals[6]
            mass = vals[7]
            self.add_planet(index + 1, position, velocity, radius, mass)

    def button_restart(self, b):
        if len(self.particlelist) > 1:
            for p in self.particlelist:
                p.reset_model()
                p.particle_model.clear_trail()
            # toggles the running state
            self.running = False
            self.b_startstop.text = '⏸️'

    def gforce(self, p1, p2):
        # Modelled using euler cromer method
        # Calculate the gravitational force exerted on p1 by p2.
        # Calculate distance vector between p1 and p2.
        # TODO: credit the source of this code with a link to the github repo

        r_vec = p1.particle_model.pos - p2.particle_model.pos
        # Calculate magnitude of distance vector.
        r_mag = vp.mag(r_vec)
        # Calculate unit vector of distance vector.
        r_hat = r_vec / r_mag
        # Calculate force magnitude.
        force_mag = self.G * p1.particle_model.mass * p2.particle_model.mass / r_mag ** 2
        # Calculate force vector.
        force_vec = -force_mag * r_hat
        return force_vec


    def run(self):
        vp.scene.camera.axis = vp.vector(0, -1, -1)
        vp.scene.ambient = vp.color.gray(0.5)
        vp.scene.autoscale = False
        vp.scene.range = 20

        self.skybox = vp.sphere(pos=vp.vector(0, 0, 0),
                                radius=self.radius,
                                shininess=self.shininess,
                                emissive=True,
                                texture=self.texture)
        vp.scene.camera.follow(self.skybox)

        while True:
            if len(self.particlelist) > 0:
                self.skybox.pos = self.particlelist[self.focus].particle_model.pos
            self.skybox.radius = vp.mag(vp.scene.camera.axis) * 8

            if self.running:

                if len(self.particlelist) == 0:
                    pass
                else:
                    for particle1 in self.particlelist:
                        particle1.totforce = vp.vector(0, 0, 0)
                        for particle2 in self.particlelist:
                            if particle1 != particle2:
                                particle1.totforce += self.gforce(particle1, particle2)

                        particle1.particle_model.momentum = particle1.particle_model.momentum + particle1.totforce * self.delta_time

                        particle1.particle_model.pos = particle1.particle_model.pos + (
                                    particle1.particle_model.momentum * self.delta_time) / particle1.particle_model.mass

                        particle1.force_arrow.axis = (vp.log(vp.mag(particle1.totforce),
                                                             10) + particle1.particle_model.radius) * (
                                                                 particle1.totforce / vp.mag(particle1.totforce))
                        particle1.force_arrow.pos = particle1.particle_model.pos

                        self.update_velocity_arrow(particle1)

            self.time += self.delta_time
            vp.rate(24)

