import vpython as vp
import numpy as np
import particles

class SolarSystem:
    DELTA_TIME = 1.0E-1
    G = 0.1  # newtons gravitational constant, 6.67e-11 to use real-world value
    NUM_PLANETS = 10  # maximum number of planets
    # skybox
    SKY = {}
    SKY['TEXTURE'] = 'https://images.unsplash.com/' \
                  'photo-1475274047050-1d0c0975c63e?ixid=' \
                  'MnwxMjA3fDB8MHxzZWFyY2h8MXx8bm' \
                  'lnaHQlMjBza3l8ZW58MHx8MHx8&ixlib=rb-1.2.1&w=1000&q=80'
    SKY['SHININESS'] = 1000
    SKY['RADIUS'] = 200
    # scene
    SCENE = {}
    SCENE['WIDTH'] = 1000
    SCENE['HEIGHT'] = 400
    SCENE['RANGE'] = 40
    # sun
    SUN = {}
    SUN['RADIUS'] = 10
    SUN['MASS'] = 10000
    # symbols for the buttons
    SYMBOLS = {'START': '▶️', 'STOP': '⏸️'}
    # texts for the controls
    TEXTS = {}
    TEXTS['CAMERA'] = 'SWITCH CAMERA FOCUS'
    TEXTS['TRAILS'] = 'TOGGLE TRAILS'
    TEXTS['FORCES'] = 'HIDE FORCES'
    TEXTS['VELOCITIES'] = 'HIDE VELOCITIES'
    TEXTS['SAVE'] = 'SAVE SYSTEM'
    TEXTS['LOAD'] = 'LOAD SYSTEM'
    TEXTS['ADD'] = 'ADD PLANET'
    TEXTS['RESET'] = 'RESET SIMULATION'
    TEXTS['CLEAR'] = 'CLEAR SYSTEM'
    TEXTS['CONSTANT'] = '  Gravitational constant G: '
    TEXTS['CONSTANTREAL'] = ', real value: 6.67e-11 '
    TEXTS['SUN'] = ' Mass of the sun: '
    TEXTS['LIGHT'] = 'Ambient light'
    TEXTS['CHOOSE'] = 'Choose what to edit for '
    TEXTS['ERROREDIT'] = 'first choose the variable'
    TEXTS['ERRORPLANET'] = 'Maximum number of planets in the system'
    TEXTS['NOERROR'] = ' Error: none'
    TEXTS["SYSTEMSAVED"] = ' System saved'
    TEXTS['PLANET'] = 'Planet '
    TEXTS['ONELINE'] = '\n'
    TEXTS['TWOLINES'] = '\n\n'
    TEXTS['SPACES'] = '  '
    TEXTS['XPOS'] = 'xpos '
    TEXTS['YPOS'] = 'ypos '
    TEXTS['ZPOS'] = 'zpos '
    TEXTS['XVEL'] = 'xvel '
    TEXTS['YVEL'] = 'yvel '
    TEXTS['ZVEL'] = 'zvel '
    TEXTS['RAD'] = 'rad  '
    TEXTS['MASS'] = 'mass  '
    TEXTS['VAR_XPOS'] = 'xpos'
    TEXTS['VAR_YPOS'] = 'ypos'
    TEXTS['VAR_ZPOS'] = 'zpos'
    TEXTS['VAR_XVEL'] = 'xvel'
    TEXTS['VAR_YVEL'] = 'yvel'
    TEXTS['VAR_ZVEL'] = 'zvel'
    TEXTS['VAR_RAD'] = 'rad '
    TEXTS['VAR_MASS'] = 'mass'
    # file to save/load the solar system
    SYSTEM_FILE = 'solar_system.csv'

    def __init__(self):
        self.time = 0

        self.focus = 0  # index of the followed planet
        self.running = False  # whether simulations runing or not
        self.particlelist = []  # list of bodies in the system
        self.veditlist = []
        self.valslist = []

        # assign the scene settings
        vp.scene.width = self.SCENE['WIDTH']
        vp.scene.height = self.SCENE['HEIGHT']
        vp.scene.range = self.SCENE['RANGE']
        vp.scene.lights = []

        # add the sun to scene
        self.add_sun()

        # create the graphs for the force and momentum of the first planet
        graph_force = vp.graph(scroll=True, fast=True, xmin=0, xmax=40, ymin=0, align='left',
                               width=self.SCENE['WIDTH']/2, height=self.SCENE['HEIGHT']/2,
                               foreground=vp.vector(0.5, 0.5, 0.5), background=vp.color.white,
                               xtitle='Time',
                               title='Planet 1: force_mag')
        graph_distance = vp.graph(scroll=True, fast=True, xmin=0, xmax=40, ymin=0, align='right',
                                  width=self.SCENE['WIDTH']/2, height=self.SCENE['HEIGHT']/2,
                                  foreground=vp.vector(0.5, 0.5, 0.5), background=vp.color.white,
                                  xtitle='Time',
                                  title='Planet 1: distance from the sun')
        self.plot_force = vp.gcurve(graph=graph_force, color=vp.color.blue)
        self.plot_distance = vp.gcurve(graph=graph_distance, color=vp.color.blue)

        vp.scene.append_to_caption(self.TEXTS['ONELINE'])

        # button to start/stop the simulation
        self.b_startstop = vp.button(bind=self.button_startstop,
                                     text=self.SYMBOLS['START'])
        vp.scene.append_to_caption(self.TEXTS['SPACES'])

        # button to cycle through the planet that the camera follows
        self.b_camera = vp.button(bind=self.camera_follow,
                                  text=self.TEXTS['CAMERA'])
        vp.scene.append_to_caption(self.TEXTS['SPACES'])

        # button to toggle the visibility of the trails
        self.b_trails = vp.button(bind=self.button_trails,
                                  text=self.TEXTS['TRAILS'])
        vp.scene.append_to_caption(self.TEXTS['SPACES'])

        # button to toggle the drawing of gravitational force vectors
        self.c_force = vp.checkbox(bind=self.checkbox_force_arrows,
                                   text=self.TEXTS['FORCES'])
        vp.scene.append_to_caption('  ')

        # button to toggle the drawing of velocity vectors
        self.c_velocity = vp.checkbox(bind=self.checkbox_velocity_arrows,
                                      text=self.TEXTS['VELOCITIES'])
        vp.scene.append_to_caption(self.TEXTS['ONELINE'])

        # slider to set the level of ambient light
        vp.scene.append_to_caption(self.TEXTS['LIGHT'])
        self.s_ambientlight = vp.slider(bind=self.slider_ambient_lights,
                                        min=0,
                                        max=1,
                                        left=0,
                                        length=200,
                                        value=0.5)


        # text input to set the value of G
        self.w_big_g_text = vp.wtext(text=self.TEXTS['CONSTANT'] + str(self.G))
        vp.scene.append_to_caption(self.TEXTS['CONSTANTREAL'])
        self.w_big_g_value = vp.winput(bind=self.winput_g,
                                       text=self.G)

        #  display the mass of the sun
        vp.scene.append_to_caption(self.TEXTS['SUN'] + str(self.particlelist[0].particle_model.mass))

        vp.scene.append_to_caption(self.TEXTS['ONELINE'])

        # button to reset the simulation
        self.b_reset = vp.button(bind=self.button_reset,
                                   text=self.TEXTS['RESET'])

        # button to save the solar system
        self.b_save = vp.button(bind=self.button_save,
                                text=self.TEXTS['SAVE'])

        # button to load the solar system
        self.b_load = vp.button(bind=self.button_load,
                                text=self.TEXTS['LOAD'])

        self.t_error = vp.wtext(text=self.TEXTS['NOERROR'])
        vp.scene.append_to_caption(self.TEXTS['ONELINE'])


        #  button to add a planet
        self.b_add = vp.button(bind=self.button_add,
                               text=self.TEXTS['ADD'])

        vp.scene.append_to_caption(self.TEXTS['ONELINE'])

    def add_sun(self):
        """Adds the sun to the solar system"""

        sun = particles.Sun(position=vp.vector(0, 0, 0),
                            radius=self.SUN['RADIUS'], mass=self.SUN['MASS'],
                            velocity=vp.vector(0, 0, 0),
                            color=vp.color.yellow,
                            texture=vp.textures.metal
                            )
        self.particlelist.append(sun)

    def button_startstop(self, b):
        """Callback for the button to start/stop the simulation"""

        if len(self.particlelist) > 1:
            # toggles the running state
            self.running = not self.running
            if self.running:
                self.b_startstop.text = self.SYMBOLS['STOP']
            else:
                self.b_startstop.text = self.SYMBOLS['START']

    def camera_follow(self, b):
        """
            Callback to the button to set focus to the
            next particle on the list (circular)
        """

        if self.focus + 1 < len(self.particlelist):
            self.focus += 1
        else:
            self.focus = 0

    def update_velocity_arrow(self, particle):
        """Function to update the velocity arrow"""

        if ((not particle.particle_model.mass == 0) and
           (not vp.mag(particle.particle_model.momentum) == 0)):
            mass = particle.particle_model.mass
            radius = particle.particle_model.radius
            momentum = particle.particle_model.momentum
            momentum_mag = vp.mag(momentum)
            velocity_log = vp.log(momentum_mag / mass, 10)
            particle.velocity_arrow.axis = (velocity_log + radius) * \
                                           (momentum / momentum_mag)
        particle.velocity_arrow.pos = particle.particle_model.pos

    def button_trails(self, b):
        """Callback to the button that toggles the drawing of the trails"""

        for p in self.particlelist:
            p.particle_model.make_trail = not p.particle_model.make_trail
            p.particle_model.clear_trail()

    def checkbox_force_arrows(self, b):
        """
            Callback to the button that toggles
            the drawing of the force vectors
        """

        for p in self.particlelist:
            p.force_arrow.visible = not p.force_arrow.visible

    def checkbox_velocity_arrows(self, b):
        """
            Callback to the button that toggles
            the drawing of the velocity vectors
        """

        for p in self.particlelist:
            p.velocity_arrow.visible = not p.velocity_arrow.visible

    def slider_ambient_lights(self, s):
        """
            Callback to the slider that sets
            the value of the ambient light
        """

        vp.scene.ambient = vp.color.gray(s.value)

    def winput_g(self, w):
        """
            Callback to the text input that sets
            the value of G to the user input only if integer or float
        """

        if (type(w.number) == int) or (type(w.number) == float):
            self.G = w.number
            self.w_big_g_text.text = self.TEXTS['CONSTANT'] + str(self.G)
            self.t_error.text = self.TEXTS['NOERROR']
        else:
            self.t_error.text = 'G has to be integer or float'

    def stop_simulation(self):
        """Callback to the button that stops the simulation"""

        self.running = False
        self.b_startstop.text = self.SYMBOLS['START']

    def button_reset(self, b):
        """Callback to the button to reset the simulation"""

        if len(self.particlelist) > 1:
            for p in self.particlelist:
                p.reset_model()
                p.particle_model.clear_trail()
            self.plot_force.delete()
            self.plot_distance.delete()
            # toggles the running state
            self.running = False
            self.b_startstop.text = self.SYMBOLS['START']

    def button_add(self, b):
        """
            Callback to the button that adds
            a planet up to a maximum of 9 planets
        """

        if len(self.particlelist) < self.NUM_PLANETS:

            self.button_reset(0)
            self.b_load.delete()

            # get the number of current, minus 1
            # because the first particle is the sun
            nplanets = len(self.particlelist) - 1
            sunradius = self.particlelist[0].radius
            sunmass = self.particlelist[0].mass
            # initial x position one more star radius away
            # from the star than previous planet
            xpos = sunradius*(nplanets + 2)
            position = vp.vector(xpos, 0, 0)
            # initial y velocity
            print(f"G:{self.G}")
            zvelocity = np.sqrt((self.G * sunmass)/vp.mag(position))
            velocity = vp.vector(0, 0, zvelocity)
            # the name of the planet always has the
            # last character the planet index
            indexplanet = nplanets + 1
            radius = 1
            mass = 0.01
            self.add_planet(indexplanet, position, velocity,
                            radius, mass)
            self.t_error.text = self.TEXTS['NOERROR']
        else:
            # deletes button if there are 9 planets
            # already in the system
            self.t_error.text = self.TEXTS['ERRORPLANET']
            b.delete()

    def add_planet(self, index, position, velocity, radius, mass):
        """Function that adds a planet to the system"""

        # creates the planet object
        name = self.TEXTS['PLANET'] + str(index)
        planet = particles.Planet(position=position,
                                  radius=radius, mass=mass,
                                  velocity=velocity,
                                  color=vp.color.white,
                                  texture=vp.textures.earth,
                                  name=name)

        self.particlelist.append(planet)
        vp.scene.append_to_caption('\n' + name + ' ')
        # sets the text for the edit values controls
        # each choice has the first 4 characters
        # the variable and the last character the planet index
        self.m_edit = vp.menu(choices=[self.TEXTS['CHOOSE'] + name,
                                       self.TEXTS['XPOS'] + name,
                                       self.TEXTS['YPOS'] + name,
                                       self.TEXTS['ZPOS'] + name,
                                       self.TEXTS['XVEL'] + name,
                                       self.TEXTS['YVEL'] + name,
                                       self.TEXTS['ZVEL'] + name,
                                       self.TEXTS['RAD'] + name,
                                       self.TEXTS['MASS'] + name,
                                       ],
                              bind=self.menu_edit)
        v_edit = vp.winput(bind=self.set_value,
                           prompt='',
                           text='first choose the variable',
                           disabled=True, visible=False)
        self.veditlist.append(v_edit)
        valstext = self.particlelist[index].get_valstext()
        v_text = vp.wtext(text=valstext)
        self.valslist.append(v_text)

    def set_value(self, i):
        """
            Set the value of a planet feature from the text input
        """

        # only set value if integer or float
        if (type(i.number) == int) or (type(i.number) == float):
            # the variable to set is given by
            # the first characters of the prompt
            var = i.prompt[:4]
            # the index of the planet is given by
            # the last character of the prompt
            index = int(i.prompt[-1])
            # determines which value to set
            if var == self.TEXTS['VAR_XPOS']:
                pos = vp.vector(i.number,
                       self.particlelist[index].position0.y,
                       self.particlelist[index].position0.z)
                if vp.mag(pos) > 0:
                    self.particlelist[index].position0.x = i.number
            elif var == self.TEXTS['VAR_YPOS']:
                pos = vp.vector(self.particlelist[index].position0.x,
                       i.number,
                       self.particlelist[index].position0.z)
                if vp.mag(pos) > 0:
                    self.particlelist[index].position0.y = i.number
            elif var == self.TEXTS['VAR_ZPOS']:
                pos = vp.vector(self.particlelist[index].position0.x,
                       self.particlelist[index].position0.y,
                       i.number)
                if vp.mag(pos) > 0:
                    self.particlelist[index].position0.z = i.number
            if var == self.TEXTS['VAR_XVEL']:
                self.particlelist[index].velocity0.x = i.number
            elif var == self.TEXTS['VAR_YVEL']:
                self.particlelist[index].velocity0.y = i.number
            elif var == self.TEXTS['VAR_ZVEL']:
                self.particlelist[index].velocity0.z = i.number
            elif var == self.TEXTS['VAR_RAD']:
                self.particlelist[index].radius = i.number
            elif var == self.TEXTS['VAR_MASS']:
                if i.number > 0:
                    self.particlelist[index].mass = i.number
            # reset simulation
            self.button_reset(0)

            valstext = self.particlelist[index].get_valstext()
            self.valslist[index - 1].text = valstext

    def menu_edit(self, m):
        """Sets the variable to edit with the text input"""

        # the index of the planet is given by
        # the last character of the selection
        index = int(m.selected[-1])
        if m.index > 0:
            # the variable to set is given by
            # the first 4 characters of the selection
            var = m.selected[:4]
            # set the prompt for the corresponding vedit to the selection
            # the prompt[:4] then gives the variable to set
            # and prompt[-1] then gives the planet index
            self.veditlist[index - 1].prompt = m.selected
            particle = self.particlelist[index]
            if var == self.TEXTS['VAR_XPOS']:
                self.veditlist[index - 1].text = particle.position0.x
            elif var == self.TEXTS['VAR_YPOS']:
                self.veditlist[index - 1].text = particle.position0.y
            elif var == self.TEXTS['VAR_ZPOS']:
                self.veditlist[index - 1].text = particle.position0.z
            elif var == self.TEXTS['VAR_XVEL']:
                self.veditlist[index - 1].text = particle.velocity0.x
            elif var == self.TEXTS['VAR_YVEL']:
                self.veditlist[index - 1].text = particle.velocity0.y
            elif var == self.TEXTS['VAR_ZVEL']:
                self.veditlist[index - 1].text = particle.velocity0.z
            elif var == self.TEXTS['VAR_RAD']:
                self.veditlist[index - 1].text = particle.radius
            elif var == self.TEXTS['VAR_MASS']:
                self.veditlist[index - 1].text = particle.mass
            self.veditlist[index - 1].visible = True
        else:
            self.veditlist[index - 1].text = self.TEXTS['ERROREDIT']

    def button_save(self, b):
        """Callback to the button to save the solar system"""

        vals = []
        for p in self.particlelist[1:]:
            vals.append(p.get_vals())

        try:
            np.savetxt(self.SYSTEM_FILE, vals, delimiter=',')
            self.t_error.text = self.TEXTS['SYSTEMSAVED']
        except:
            self.t_error.text = ' ERROR: could not save system to ' + \
                                self.SYSTEM_FILE

    def button_load(self, b):
        """Callback to the button to load the solar system"""

        try:
            allvals = np.genfromtxt(self.SYSTEM_FILE, delimiter=',')
        except:
            self.t_error.text = ' ERROR: Could not load system from ' + \
                                self.SYSTEM_FILE

        else:
            # only load the system once
            b.delete()
            # reset the text error if we had one
            self.t_error.text = self.TEXTS['NOERROR']

            for index, vals in enumerate(allvals):
                position = vp.vector(vals[0], vals[1], vals[2])
                velocity = vp.vector(vals[3], vals[4], vals[5])
                radius = vals[6]
                mass = vals[7]
                self.add_planet(index + 1, position,
                                velocity, radius, mass)

    def calculate_gforce(self, p1, p2):
        """
            Function that calculates the gravitational force
            exerted on p1 by p2.
            Modelled using euler cromer method.
            Based on https://www.youtube.com/watch?v=4ycpvtIio-o
            and https://www.glowscript.org/#/user/wlane/folder/Let'sCodePhysics/program/Solar-System-1/edit

            Returns:
            force vector
        """
        # Calculate the distance vectors between the two objects
        r_vec = p1.particle_model.pos - p2.particle_model.pos
        # Calculate magnitude of distance vector.
        r_mag = vp.mag(r_vec)
        # Calculate unit vector of distance vector.
        r_hat = r_vec / r_mag
        # Calculate force magnitude.
        p1_mass = p1.particle_model.mass
        p2_mass = p2.particle_model.mass
        force_mag = self.G * p1_mass * p2_mass / r_mag ** 2
        # Calculate force vector.
        force_vec = -force_mag * r_hat
        return force_vec

    def run(self):
        """Function to run the simulation"""

        vp.scene.camera.axis = vp.vector(0, -1, -1)
        vp.scene.ambient = vp.color.gray(0.5)
        vp.scene.autoscale = False
        vp.scene.range = 20

        self.skybox = vp.sphere(pos=vp.vector(0, 0, 0),
                                radius=self.SKY['RADIUS'],
                                shininess=self.SKY['SHININESS'],
                                emissive=True,
                                texture=self.SKY['TEXTURE'])
        vp.scene.camera.follow(self.skybox)

        # infinite loop
        while True:
            # if there are particles in the system set the skybox
            if len(self.particlelist) > 0:
                p_model = self.particlelist[self.focus].particle_model
                self.skybox.pos = p_model.pos
            self.skybox.radius = vp.mag(vp.scene.camera.axis) * 8

            if self.running:
                if len(self.particlelist) == 0:
                    pass
                else:
                    for p1 in self.particlelist:
                        p1.totforce = vp.vector(0, 0, 0)
                        for p2 in self.particlelist:
                            if p1 != p2:
                                p1.totforce += self.calculate_gforce(p1, p2)

                        p1.particle_model.momentum += p1.totforce * self.DELTA_TIME

                        p1.particle_model.pos += (p1.particle_model.momentum * self.DELTA_TIME) / p1.particle_model.mass

                        p1.force_arrow.axis = (100*vp.mag(p1.totforce) + p1.particle_model.radius) * \
                                              (p1.totforce / vp.mag(p1.totforce))
                        p1.force_arrow.pos = p1.particle_model.pos

                        self.update_velocity_arrow(p1)

                    displacement = self.particlelist[1].particle_model.pos - self.particlelist[0].particle_model.pos
                    self.plot_force.plot(self.time,
                                         vp.mag(self.particlelist[1].totforce))
                    self.plot_distance.plot(self.time,
                                            vp.mag(displacement))


                self.time += self.DELTA_TIME
            vp.rate(24)
