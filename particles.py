import vpython as vp


class Particle:
    def __init__(self, position, radius, mass,
                 velocity, color, texture, emissive):

        self.radius = radius
        self.mass = mass
        self.velocity0 = velocity
        self.position0 = position
        self.momentum0 = mass * self.velocity0
        self.color = color
        self.retain = 100
        self.particle_model = vp.sphere(pos=self.position0,
                                        radius=self.radius,
                                        mass=self.mass,
                                        momentum=self.momentum0,
                                        color=self.color,
                                        texture={'file': texture},
                                        emissive=emissive,
                                        shininess=0,
                                        make_trail=True,
                                        retain=self.retain,
                                        )

        self.force_arrow = vp.cone(pos=self.particle_model.pos,
                                   radius=radius / 5,
                                   color=vp.color.red,
                                   axis=vp.vector(0, 0, 0),
                                   emissive=True,
                                   shininess=0)

        self.velocity_arrow = vp.cone(pos=self.particle_model.pos,
                                      radius=radius / 5,
                                      color=vp.color.green,
                                      axis=vp.vector(0, 0, 0),
                                      emissive=True,
                                      shininess=0)

    def get_vals(self):
        """
            Returns the position, velocity, radius and mass for the particle

            Returns:
            list with parameter values

        """

        vals = [self.position0.x,
                self.position0.y,
                self.position0.z,
                self.velocity0.x,
                self.velocity0.y,
                self.velocity0.z,
                self.radius,
                self.mass
                ]
        return vals

    def reset_model(self):
        """
            Reset the values of the position, momentum,
            radius and mass for the particle
        """

        self.momentum0 = self.mass * self.velocity0
        self.particle_model.radius = self.radius
        self.particle_model.mass = self.mass
        self.particle_model.pos = self.position0
        self.particle_model.momentum = self.momentum0
        self.particle_model.clear_trail()


class Sun(Particle):
    def __init__(self, position, radius, mass, velocity, color, texture):
        super().__init__(position, radius, mass,
                         velocity, color, texture, True)
        print('Created sun')


class Planet(Particle):
    def __init__(self, position, radius, mass,
                 velocity, color, texture, name):
        self.name = name
        super().__init__(position, radius, mass,
                         velocity, color, texture, False)
        print('Created', self.name)

    def get_valstext(self):
        """
            Get the position, velocity,
            radius and mass for a planet in a string

            Returns:
            a readable string with the values
        """

        valstext = ' pos: (' + str(self.position0.x) + \
                   ', ' + str(self.position0.y) + \
                   ', ' + str(self.position0.z) + ') ' + \
                   ' vel: (' + str(self.velocity0.x) + \
                   ', ' + str(self.velocity0.y) + \
                   ', ' + str(self.velocity0.z) + ') ' + \
                   'radius: ' + str(self.radius) + ', ' + \
                   'mass: ' + str(self.mass)
        return valstext
