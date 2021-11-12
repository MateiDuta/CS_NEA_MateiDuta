import vpython as vp
from random import choice

class Particle:
    def __init__(self, position, radius, mass, velocity, color, texture, emissive):

        self.velocity = velocity
        self.momentum = mass * self.velocity
        self.position = position
        self.radius = radius
        self.mass = mass
        self.color = color
        self.particle_model = vp.sphere(pos=self.position,
                                        radius=self.radius,
                                        mass=self.mass,
                                        momentum=self.momentum,
                                        color=self.color,
                                        texture={'file': texture},
                                        emissive=emissive,
                                        shininess=0,
                                        )
        vp.attach_trail(self.particle_model,
                        radius=self.particle_model.radius/5,
                        color=vp.color.white,
                        retain=100
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
        vals = [self.particle_model.pos.x,
                self.particle_model.pos.y,
                self.particle_model.pos.z,
                self.velocity.x,
                self.velocity.y,
                self.velocity.z,
                self.particle_model.radius,
                self.particle_model.mass
               ]
        return vals

class Sun(Particle):
    def __init__(self, position, radius, mass, velocity, color, texture):
        super().__init__(position, radius, mass, velocity, color, texture, True)

class Planet(Particle):
    def __init__(self, position, radius, mass, velocity, color, texture, name):
        self.name = name
        super().__init__(position, radius, mass, velocity, color, texture, False)
        print("Created", self.name)

        # self.lamp = vp.local_light(pos=self.particle_model.pos, colour=vp.color.white)
        #
        # self.is_emissive()
    def get_valstext(self):
        valstext = ' pos: (' + str(self.particle_model.pos.x) + \
                           ', ' + str(self.particle_model.pos.y) + \
                           ', ' + str(self.particle_model.pos.z) + ') ' + \
                   ' vel: (' + str(self.velocity.x) + \
                           ', ' + str(self.velocity.y) + \
                           ', ' + str(self.velocity.z) + ') ' + \
                    'radius: ' + str(self.particle_model.radius) + ', ' + \
                    'mass: ' + str(self.particle_model.mass)
        return valstext
