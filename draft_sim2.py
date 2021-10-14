import vpython as vp
from random import choice


class Particle:
    def __init__(self, position, radius, mass, velocity, color, texture, emissive):
        momentum = mass * velocity

        self.particle_model = vp.sphere(pos=position, radius=radius,
                                        mass=mass, momentum=momentum,
                                        color=color, make_trail=True,
                                        texture={'file': texture}, emissive=emissive, shininess=0)

        self.force_arrow = vp.cone(pos=self.particle_model.pos, radius=radius / 5, color=vp.color.red,
                                   axis=vp.vector(0, 0, 0), emissive=True, shininess=0)
        self.velocity_arrow = vp.cone(pos=self.particle_model.pos, radius=radius / 5, color=vp.color.green,
                                      axis=vp.vector(0, 0, 0), emissive=True, shininess=0)

        self.lamp = vp.local_light(pos=self.particle_model.pos, colour=vp.color.white)

        self.is_emissive()


    def is_emissive(self):
        if self.particle_model.emissive:
            self.lamp.visible = True
        else:
            self.lamp.visible = False

    def make_widgets(self):
        self.m_type = vp.menu(bind=self.menu_type, choices=['Choose a type', 'Star', 'Earth', 'Planet', 'Moon'])

        vp.scene.append_to_caption('   Pos: X')
        self.w_posx = vp.winput(bind=self.change_posx, text=0)
        vp.scene.append_to_caption('Y')
        self.w_posy = vp.winput(bind=self.change_posy, text=0)
        vp.scene.append_to_caption('Z')
        self.w_posz = vp.winput(bind=self.change_posz, text=0)

        vp.scene.append_to_caption('   Vel: X')
        self.w_velx = vp.winput(bind=self.change_velx, text=0)
        vp.scene.append_to_caption('Y')
        self.w_vely = vp.winput(bind=self.change_vely, text=0)
        vp.scene.append_to_caption('Z')
        self.w_velz = vp.winput(bind=self.change_velz, text=0)

        vp.scene.append_to_caption('   Mass:')
        self.w_mass = vp.winput(bind=self.change_mass, text=self.particle_model.mass)

    def delete_widgets(self):
        self.m_type.delete()

    def menu_type(self, m):
        val = m.selected
        if val == "Star":
            self.particle_model.color = vp.color.yellow
            self.particle_model.emissive = True
            self.is_emissive()
            self.particle_model.texture = {'file': vp.textures.metal}

        elif val == "Earth":
            self.particle_model.color = vp.color.white
            self.particle_model.emissive = False
            self.is_emissive()
            self.particle_model.texture = {'file':vp.textures.earth}

        elif val == "Planet":
            self.particle_model.color = choice([vp.color.red, vp.color.green, vp.color.cyan, vp.color.orange, vp.color.cyan])
            self.particle_model.emissive = False
            self.is_emissive()
            self.particle_model.texture = {'file': vp.textures.wood}

        elif val == "Moon":
            self.particle_model.color = vp.color.white
            self.particle_model.emissive = False
            self.is_emissive()
            self.particle_model.texture = {'file': vp.textures.rough}

    def change_posx(self, w):
        if type(w.number) == int:
            self.particle_model.pos.x = w.number

    def change_posy(self, w):
        if type(w.number) == int:
            self.particle_model.pos.y = w.number

    def change_posz(self, w):
        if type(w.number) == int:
            self.particle_model.pos.z = w.number

    def change_velx(self, w):
        if type(w.number) == int:
            self.particle_model.momentum.x = w.number * self.particle_model.mass

    def change_vely(self, w):
        if type(w.number) == int:
            self.particle_model.momentum.y = w.number * self.particle_model.mass

    def change_velz(self, w):
        if type(w.number) == int:
            self.particle_model.momentum.z = w.number * self.particle_model.mass

    def change_mass(self, w):
        if type(w.number) == int:
            self.particle_model.mass = w.number

class Simulation:
    def __init__(self):
        self.time = 0
        self.delta_time = 1.0E-5

        # Initialised value of newtons gravitational constant, 6.67e-11 to use real-world value.
        self.G = 1

        self.focus = 0  # index in particlelist to the planet that the planet follows
        self.running = None
        self.particlelist = []
        self.shininess = 1000
        self.radius = 100
        self.rate = 100
        self.texture = "https://images.unsplash.com/photo-1475274047050-1d0c0975c63e?ixid=MnwxMjA3fDB8MHxzZWFyY2h8MXx8bm" \
                       "lnaHQlMjBza3l8ZW58MHx8MHx8&ixlib=rb-1.2.1&w=1000&q=80"

        # Controls for the user interface
        # TODO: add description to each button for clarity
        vp.scene.append_to_caption('\n\n')

        # - start/stop the simulation
        self.b_startstop = vp.button(bind=self.button_startstop, text='⏸')
        vp.scene.append_to_caption('  ')

        # - restart the simulation, does not work; TODO: implement
        self.b_restart = vp.button(bind=self.button_restart, text='RESTART')
        vp.scene.append_to_caption('  ')

        # - cycle through the planet that the camera follows
        self.b_camera = vp.button(bind=self.camera_follow, text='SWITCH CAMERA FOCUS')
        vp.scene.append_to_caption('  ')

        # - toggle the visibility of the trails
        self.b_trails = vp.checkbox(bind=self.button_trails, text='HIDE TRAILS')
        vp.scene.append_to_caption('  ')

        # - toggle the drawing of gravitational force vectors
        self.b_force = vp.checkbox(bind=self.button_force_arrows, text='HIDE FORCES')
        vp.scene.append_to_caption('  ')

        # - toggles the drawing of velocity vectors
        self.b_velocity = vp.checkbox(bind=self.button_velocity_arrows, text='HIDE VELOCITIES')
        vp.scene.append_to_caption('\n\n')

        # - sets the level of ambient light
        self.s_ambientlight = vp.slider(bind=self.slider_ambient_lights, min=0, max=1, left=0, length=200, value=0.5)
        vp.scene.append_to_caption('Ambient light   | ')

        # - allow to change the value for G
        self.w_big_g_value = vp.winput(bind=self.winput_g, text=1)
        vp.scene.append_to_caption("  Gravitational constant G; real value: 6.67e-11")

        vp.scene.append_to_caption('\n\n══════════════════════════════════════════════════════════════════════════\n\n')

        self.b_add = vp.button(bind=self.button_add, text='ADD PARTICLE')




    def button_startstop(self, b):
        # toggles the running state
        self.running = not self.running
        if self.running:
            self.b_startstop.text = '⏸️'
        else:
            self.b_startstop.text = "▶️"

    def button_restart(self, b):
        # TODO: implement
        pass

    def camera_follow(self, b):
        # set focus to the next particle on the list (circular)
        if self.focus + 1 < len(self.particlelist):
            self.focus += 1
        else:
            self.focus = 0

    def button_trails(self, b):
        # toggles the drawing of the trails
        for p in self.particlelist:
            p.particle_model.clear_trail()
            p.particle_model.make_trail = not p.particle_model.make_trail

    def button_force_arrows(self, b):
        # toggles the drawing of the force vectors
        for p in self.particlelist:
            p.force_arrow.visible = not p.force_arrow.visible

    def button_velocity_arrows(self, b):
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

    def button_add(self, b):
        self.running = False
        self.b_startstop.text = "▶️"

        self.b_add.delete()

        new_particle = Particle(vp.vector(0, 0, 0), 1, 1000, vp.vector(0, 0, 0), vp.color.yellow, vp.textures.metal, True)

        self.particlelist.append(new_particle)

        vp.wtext(text=f'Particle {len(self.particlelist)}:')
        new_particle.make_widgets()
        vp.scene.append_to_caption('\n')

        self.b_add = vp.button(bind=self.button_add, text='ADD PARTICLE')








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

        vp.scene.ambient = vp.color.gray(0.5)
        vp.scene.autoscale = False
        vp.scene.range = 10

        self.skybox = vp.sphere(pos=vp.vector(0, 0, 0), radius=self.radius, shininess=self.shininess,
                                emissive=True, texture=self.texture)
        vp.scene.camera.follow(self.skybox)

        while True:
            if len(self.particlelist) > 0:
                self.skybox.pos = self.particlelist[self.focus].particle_model.pos
            self.skybox.radius = vp.mag(vp.scene.camera.axis) * 8

            if self.running:
                vp.rate = (self.rate)
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

                        particle1.velocity_arrow.axis = (vp.log(
                            vp.mag(particle1.particle_model.momentum) / particle1.particle_model.mass,
                            10) + particle1.particle_model.radius) * (particle1.particle_model.momentum / vp.mag(
                            particle1.particle_model.momentum))
                        particle1.velocity_arrow.pos = particle1.particle_model.pos

            self.time += self.delta_time


my_simulation = Simulation()
vp.scene.width = 1000
vp.scene.height = 400
vp.scene.range = 12
vp.scene.lights = []


my_simulation.running = True

my_simulation.run()

