#P5 controller
import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys

import grafica.transformations as tr
import grafica.basic_shapes as bs
import local_shapes as loc_s
import grafica.easy_shaders as es
import grafica.performance_monitor as pm
import grafica.lighting_shaders as ls
from grafica.assets_path import getAssetPath
import ex_obj_reader as objr

#######################################
#######################################
#Este ejercicio cambie la clase sphere para implementar el obj, el verdadero problema fue que 
#Que los archivos importados en el auxiliar eran los de años anteriores, por lo que tuve que cambiar
#Muchas partes del codigo para que funcionara. La parte del ejercicio que especifica que se debe escalar
#En un cubo de arista 1, deje fijo en 1 la distancia de los circulos, pues asi dejo fijo el escalado del obj.
#######################################
#######################################



# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.showAxis = True
        self.x_clipping = 0.0
        self.y_clipping = 0.0


# we will use the global controller as communication with the callback function
controller = Controller()

def createGPUShape(pipeline, shape):
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuShape

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
        pass

def generateSphereShape(nTheta, nPhi):
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

            _vertex, _indices = loc_s.createColorQuadIndexation(start_index, a, b, c, d, color=[0.3, 0.8, 0.2])

            vertices += _vertex
            indices  += _indices
            start_index += 4

    return bs.Shape(vertices, indices)

# defining the obj
class Sphere:
    # class atributes, these gpuShapes will be the same for every sphere.
    shape = objr.readOBJ(getAssetPath('suzanne.obj'), (0.5, 0.2, 0.7))
    time = 0  # time will be the same for every Sphere.

    def __init__(self, posX, posY, R, angleSpeed):
        self.posX = posX
        self.posY = posY
        self.R = R
        self.angleSpeed = angleSpeed
        # stored values
        self.angle = 0.0
        self.gpuSphere = createGPUShape(ls.SimpleGouraudShaderProgram(),self.shape)

    def updateAngle(self):
        self.angle = self.time * self.angleSpeed # theta = w * t

    def draw(self, pipeline):
        z = np.sin(self.angle)
        # Scaling by R and translating in z = sin(theta)
        transform = tr.matmul([tr.translate(self.posX, self.posY, z), tr.uniformScale(self.R)])
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, transform)
        pipeline.drawCall(self.gpuSphere)

    def updateAndDraw(self, pipeline):
        self.updateAngle()
        self.draw(pipeline)

    # This is a class method, it is not called with self (the object)
    # But with the class cls
    @classmethod
    def updateTime(cls, dt):
        cls.time += dt

    # P4 y P5 (clipping from controller)
    def clipping(self, xmin, ymin, xmax, ymax):
        global controller
        xmin += controller.x_clipping
        xmax += controller.x_clipping
        ymin += controller.y_clipping
        ymax += controller.y_clipping
        if xmin <= self.posX <= xmax and ymin <= self.posY <= ymax:
            return True
        else:
            return False

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
    #D = float(input('distancia D entre las esferas?'))
    # En la parte que especifican escalar para contener en cubo de arista 1 se deberia fijar este valor en 1
    # De haber entendido mal, y no ser importante esto, se vuelve a dejar como imput
    
    D = 1.0
    mu, sigma = D * 0.5, D * 0.1 # mean and standard deviation
    radios = np.random.normal(mu, sigma, N*M)
    angleSpeeds = np.random.normal(mu, sigma * 2, N*M)
    spheres = []

    # Hacemos un plano y ubicamos cada esfera a una distancia D de la próxima    
    x = np.arange(-D * N / 2, D * N / 2, D)
    y = np.arange(-D * M / 2, D * M / 2, D)

    for index in range(N*M):
        i, j = getIJ(index, N, M)
        posX, posY = x[i], y[j]
        spheres.append(Sphere(posX, posY, radios[index], angleSpeeds[index]))
    
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
    #mvpPipeline = es.SimpleModelViewProjectionShaderProgram()
    #changing the pipeline
    pipeline = ls.SimpleGouraudShaderProgram()
    
    # Telling OpenGL to use our shader program
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)


    # Using the same view and projection matrices in the whole application
    projection = tr.perspective(45, float(width)/float(height), 0.1, 100)
    glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition"), -3, 0, 3)
    
    glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 100)
    glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), 0.001)
    glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), 0.1)
    glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), 0.01)
    
    Spheres = createSpheres()

    # Creating a filtered list
    filteredSpheresList = [sphere for sphere in Spheres if sphere.clipping(-4, -4, 4, 4)]

    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)

    t0 = glfw.get_time()
    camera_theta = np.pi/4
    frame_counter = 0
    time_until_30 = 0

    while not glfw.window_should_close(window):

        # Measuring performance
        perfMonitor.update(glfw.get_time())
        glfw.set_window_title(window, "Ejercicio obj" + str(perfMonitor))


        # Using GLFW to check for input events
        glfw.poll_events()
        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1
        
        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
            controller.x_clipping -= 5 * dt

        if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
            controller.x_clipping += 5 * dt

        if (glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS):
            controller.y_clipping += 5 * dt

        if (glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS):
            controller.y_clipping -= 5 * dt

        # Setting up the view transform

        camX = 10 * np.sin(camera_theta)
        camY = 10 * np.cos(camera_theta)

        viewPos = np.array([camX, camY, 10])
        
        view = tr.lookAt(
                viewPos,
                np.array([0, 0, 0]),
                np.array([0, 0, 1])
            )
        # Increasing time for the whole class Sphere.
        Sphere.updateTime(dt)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)


        for sphere in Spheres:
            if sphere.clipping(-4, -4, 4, 4):
                sphere.updateAngle()
                sphere.draw(pipeline)

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)
    
    glfw.terminate()
