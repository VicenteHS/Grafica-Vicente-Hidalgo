# P3
# Extra: Time for FPS
# Extra: random radius, angleSpeed and colors!

from abc import ABC
import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys

import transformations as tr
import basic_shapes as bs
import local_shapes as loc_s
import easy_shaders as es
import lighting_shaders as ls


# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.showAxis = True


# we will use the global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_LEFT_CONTROL:
        controller.showAxis = not controller.showAxis

    elif key == glfw.KEY_ESCAPE:
        sys.exit()

    else:
        print('Unknown key')


def generateSphereShape(nTheta, nPhi, sun=False):
    vertices = []
    indices = []

    theta_angs = np.linspace(0, np.pi, nTheta, endpoint=True)
    phi_angs = np.linspace(0, 2 * np.pi, nPhi, endpoint=True)

    start_index = 0

    for theta_ind in range(len(theta_angs)-1): # vertical
        cos_theta = np.cos(theta_angs[theta_ind]) # z_top
        cos_theta_next = np.cos(theta_angs[theta_ind + 1]) # z_bottom

        sin_theta = np.sin(theta_angs[theta_ind])
        sin_theta_next = np.sin(theta_angs[theta_ind + 1])

        # d === c <---- z_top
        # |     |
        # |     |
        # a === b  <--- z_bottom
        # ^     ^
        # phi   phi + dphi
        for phi_ind in range(len(phi_angs)-1): # horizontal
            cos_phi = np.cos(phi_angs[phi_ind])
            cos_phi_next = np.cos(phi_angs[phi_ind + 1])
            sin_phi = np.sin(phi_angs[phi_ind])
            sin_phi_next = np.sin(phi_angs[phi_ind + 1])
            # we will asume radius = 1, so scaling should be enough.
            # x = cosφ sinθ
            # y = sinφ sinθ
            # z = cosθ

            #                     X                             Y                          Z
            a = np.array([cos_phi      * sin_theta_next, sin_phi * sin_theta_next     , cos_theta_next])
            b = np.array([cos_phi_next * sin_theta_next, sin_phi_next * sin_theta_next, cos_theta_next])
            c = np.array([cos_phi_next * sin_theta     , sin_phi_next * sin_theta     , cos_theta])
            d = np.array([cos_phi * sin_theta          , sin_phi * sin_theta          , cos_theta])

            if sun is False:
                _vertex, _indices = loc_s.createColorQuadIndexation(start_index, a, b, c, d, color=[0.3, 0.8, 0.2])
            else:
                _vertex, _indices = loc_s.createColorQuadIndexation(start_index, a, b, c, d, color=[0.9, 0.8, 0.1])

            vertices += _vertex
            indices  += _indices
            start_index += 4

    return bs.Shape(vertices, indices)



def generateSphereShapeNormals(nTheta, nPhi):
    vertices = []
    indices = []

    theta_angs = np.linspace(0, np.pi, nTheta, endpoint=True)
    phi_angs = np.linspace(0, 2 * np.pi, nPhi, endpoint=True)

    start_index = 0

    for theta_ind in range(len(theta_angs)-1): # vertical
        cos_theta = np.cos(theta_angs[theta_ind]) # z_top
        cos_theta_next = np.cos(theta_angs[theta_ind + 1]) # z_bottom

        sin_theta = np.sin(theta_angs[theta_ind])
        sin_theta_next = np.sin(theta_angs[theta_ind + 1])

        # d === c <---- z_top
        # |     |
        # |     |
        # a === b  <--- z_bottom
        # ^     ^
        # phi   phi + dphi
        for phi_ind in range(len(phi_angs)-1): # horizontal
            cos_phi = np.cos(phi_angs[phi_ind])
            cos_phi_next = np.cos(phi_angs[phi_ind + 1])
            sin_phi = np.sin(phi_angs[phi_ind])
            sin_phi_next = np.sin(phi_angs[phi_ind + 1])
            # we will asume radius = 1, so scaling should be enough.
            # x = cosφ sinθ
            # y = sinφ sinθ
            # z = cosθ

            #                     X                             Y                          Z
            a = np.array([cos_phi      * sin_theta_next, sin_phi * sin_theta_next     , cos_theta_next])
            b = np.array([cos_phi_next * sin_theta_next, sin_phi_next * sin_theta_next, cos_theta_next])
            c = np.array([cos_phi_next * sin_theta     , sin_phi_next * sin_theta     , cos_theta])
            d = np.array([cos_phi * sin_theta          , sin_phi * sin_theta          , cos_theta])

            a_n = 2*np.array([cos_phi      * sin_theta_next, sin_phi * sin_theta_next     , cos_theta_next])
            b_n = 2*np.array([cos_phi_next * sin_theta_next, sin_phi_next * sin_theta_next, cos_theta_next])
            c_n = 2*np.array([cos_phi_next * sin_theta     , sin_phi_next * sin_theta     , cos_theta])
            d_n = 2*np.array([cos_phi * sin_theta          , sin_phi * sin_theta          , cos_theta])

            mu = 0.5
            sigma = 0.1
            color = np.random.normal(mu, sigma, 3)
            _vertex, _indices = loc_s.createColorSpecificNormals(start_index, a, b, c, d, a_n, b_n, c_n, d_n, color=color)

            vertices += _vertex
            indices  += _indices
            start_index += 4

    return bs.Shape(vertices, indices)


class AbstractSphere(ABC):
    # Class Atributes, these variables will be the same for every Sphere.
    time = 0  # Time will be the same for every Sphere.

    def __init__(self, posX, posY, R, angleSpeed):
        self.posX = posX
        self.posY = posY
        self.R = R
        self.angleSpeed = angleSpeed
        # stored values
        self.angle = 0.0
        self.gpuSphere = es.toGPUShape(self.shape)

    def updateAngle(self):
        self.angle = self.time * self.angleSpeed # theta = w * t

    # This is a class method, it is not called with self (the object)
    # But with the class cls
    @classmethod
    def updateTime(cls, dt):
        cls.time += dt
    
    def draw(self, pipeline):
        z = np.sin(self.angle)
        # Scaling by R and translating in z = sin(theta)
        transform = tr.matmul([tr.translate(self.posX, self.posY, z), tr.uniformScale(self.R)])
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, transform)
        pipeline.drawShape(self.gpuSphere)

    def updateAndDraw(self, pipeline):
        self.updateAngle()
        self.draw(pipeline)

class Sphere(AbstractSphere):
    shape = generateSphereShape(20, 20)

class SphereWithNormals(AbstractSphere):
    #Class attribute
    shape = generateSphereShapeNormals(20, 20)


#P3
def getIJ(index, N, M):
    # we are inside the grid.
    assert(index < N * M)
    col = 0
    while index >= N:
        col += 1
        index -= N
    row = index % N
    return row, col


def createSpheres():
    N = int(input('tamaño N?'))
    M = int(input('tamaño M?'))
    D = float(input('distancia D entre las esferas?'))
    mu, sigma = D * 0.5, D * 0.1 # mean and standard deviation
    radios = np.random.normal(mu, sigma, N*M)
    angleSpeeds = np.random.normal(mu, sigma * 2, N*M)
    spheres = []

    # Hacemos un plano y ubicamos cada esfera a una distancia D de la próxima    
    x = np.arange(-D * N, 0, D)
    y = np.arange(-D * M, 0, D)

    for index in range(N*M):
        i, j = getIJ(index, N, M)
        posX, posY = x[i], y[j]
        spheres.append(Sphere(posX, posY, radios[index], angleSpeeds[index]))
    
    return spheres

def createSpheresWithNormals():
    N = int(input('tamaño N?'))
    M = int(input('tamaño M?'))
    D = float(input('distancia D entre las esferas?'))
    mu, sigma = D * 0.5, D * 0.1 # mean and standard deviation
    radios = np.random.normal(mu, sigma, N*M)
    angleSpeeds = np.random.normal(mu, sigma * 2, N*M)
    spheres = []

    # Hacemos un plano y ubicamos cada esfera a una distancia D de la próxima    
    x = np.arange(0, D * N, D)
    y = np.arange(0, D * M, D)

    for index in range(N*M):
        i, j = getIJ(index, N, M)
        posX, posY = x[i], y[j]
        spheres.append(SphereWithNormals(posX, posY, radios[index], angleSpeeds[index]))
    
    return spheres



if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Cuma Sphere", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Assembling the shader program (pipeline) with both shaders
    mvpPipeline = es.SimpleModelViewProjectionShaderProgram()
    lightingPipeline = ls.SimplePhongShaderProgram()
    # Telling OpenGL to use our shader program
    glUseProgram(mvpPipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory
    gpuAxis = es.toGPUShape(bs.createAxis(7))

    # Using the same view and projection matrices in the whole application
    projection = tr.perspective(45, float(width)/float(height), 0.1, 100)
    glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
    
    Spheres = createSpheres()
    SpheresWithNormals = createSpheresWithNormals()
    GPUSun = es.toGPUShape(generateSphereShape(30, 30, sun=True))

    t0 = glfw.get_time()
    camera_theta = np.pi/4
    frame_counter = 0
    time_until_30 = 0

    sun_position = [0.0, 0.0]

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()
        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        glUseProgram(mvpPipeline.shaderProgram)

        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
            sun_position[0] -= 2 * dt

        if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
            sun_position[0] += 2* dt

        if (glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS):
            sun_position[1] -= 2 * dt

        if (glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS):
            sun_position[1] += 2* dt
    
        # Setting up the view transform

        camX = 15 * np.sin(camera_theta)
        camY = 15 * np.cos(camera_theta)

        viewPos = np.array([camX, camY, 10])
        
        view = tr.lookAt(
                viewPos,
                np.array([0, 0, 0]),
                np.array([0, 0, 1])
            )
        # Increasing time for the whole class Sphere.
        AbstractSphere.updateTime(dt)

        glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "view"), 1, GL_TRUE, view)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        if controller.showAxis:
            glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
            mvpPipeline.drawShape(gpuAxis, GL_LINES)

        for sphere in Spheres:
            sphere.updateAngle()
            sphere.draw(mvpPipeline)

        # Drawing Sun
        sun_translation = tr.translate(sun_position[0], sun_position[1], 0)
        glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "model"), 1, GL_TRUE, sun_translation)
        mvpPipeline.drawShape(GPUSun)

        # Drawing Spheres with normals
        # Setting lighting Pipeline and its variables
        glUseProgram(lightingPipeline.shaderProgram)

        # White light in all components: ambient, diffuse and specular.
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "La"), 0.2, .2, .2)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ka"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Kd"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)


        # TO DO: Explore different parameter combinations to understand their effect!

        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "lightPosition"), sun_position[0], sun_position[1], 0.0)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1], viewPos[2])
        glUniform1ui(glGetUniformLocation(lightingPipeline.shaderProgram, "shininess"), 10)

        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "constantAttenuation"), 0.0004)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "linearAttenuation"), 0.024)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "quadraticAttenuation"), 0.03)

        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())

        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())

        for sphere in SpheresWithNormals:
            sphere.updateAngle()
            sphere.draw(lightingPipeline)

        
        time_until_30 += dt
        frame_counter += 1
        if frame_counter == 30:
            frame_counter = 0
            print(f'time for 30 frames == {time_until_30}')
            time_until_30 = 0
        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)
    
    glfw.terminate()
