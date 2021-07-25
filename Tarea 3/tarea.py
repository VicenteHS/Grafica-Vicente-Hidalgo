# coding=utf-8

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import random
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.transformations as tr
import grafica.performance_monitor as pm
import ex_obj_reader as objr
from grafica.assets_path import getAssetPath
import grafica.lighting_shaders as ls


NUMBER_OF_CIRCLES = 10
CIRCLE_DISCRETIZATION = 20
RADIUS = 0.08
COEF_FRICTION = 0.5
COEF_RESTITUCION = 1

# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.viewTop = True

# We will use the global controller as communication with the callback function
controller = Controller()

# Convenience function to ease initialization
def createGPUShape(pipeline, shape):
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuShape

def createTextureNormalSphere(N):
    # Funcion para crear una esfera con normales y texturizada

    vertices = []           # lista para almacenar los verices
    indices = []            # lista para almacenar los indices
    dTheta = 2 * np.pi /N   # angulo que hay entre cada iteracion de la coordenada theta
    dPhi = 2 * np.pi /N     # angulo que hay entre cada iteracion de la coordenada phi
    rho = 0.5               # radio de la esfera
    c = 0                   # contador de vertices, para ayudar a indicar los indices

    # Se recorre la coordenada theta
    for i in range(N - 1):
        theta = i * dTheta # angulo theta en esta iteracion
        theta1 = (i + 1) * dTheta # angulo theta en la iteracion siguiente
         # Se recorre la coordenada phi
        for j in range(N):
            phi = j*dPhi # angulo phi en esta iteracion
            phi1 = (j+1)*dPhi # angulo phi en la iteracion siguiente

            # Se crean los vertices necesarios son coordenadas esfericas para cada iteracion

            # Vertice para las iteraciones actuales de theta (i) y phi (j) 
            v0 = [rho*np.sin(theta)*np.cos(phi), rho*np.sin(theta)*np.sin(phi), rho*np.cos(theta)]
            # Vertice para las iteraciones siguiente de theta (i + 1) y actual de phi (j) 
            v1 = [rho*np.sin(theta1)*np.cos(phi), rho*np.sin(theta1)*np.sin(phi), rho*np.cos(theta1)]
            # Vertice para las iteraciones actual de theta (i) y siguiente de phi (j + 1) 
            v2 = [rho*np.sin(theta1)*np.cos(phi1), rho*np.sin(theta1)*np.sin(phi1), rho*np.cos(theta1)]
            # Vertice para las iteraciones siguientes de theta (i + 1) y phi (j + 1) 
            v3 = [rho*np.sin(theta)*np.cos(phi1), rho*np.sin(theta)*np.sin(phi1), rho*np.cos(theta)]

            # Se crean los vectores normales para cada vertice segun los valores de rho tongo 
            n0 = [np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)]
            n1 = [np.sin(theta1)*np.cos(phi), np.sin(theta1)*np.sin(phi), np.cos(theta1)]
            n2 = [np.sin(theta1)*np.cos(phi1), np.sin(theta1)*np.sin(phi1), np.cos(theta1)]
            n3 = [np.sin(theta)*np.cos(phi1), np.sin(theta)*np.sin(phi1), np.cos(theta)]


            # Creamos los triangulos superiores
            #        v0
            #       /  \
            #      /    \
            #     /      \
            #    /        \
            #   /          \
            # v1 ---------- v2
            if i == 0:
                #           vertices           UV coord    normales
                vertices += [v0[0], v0[1], v0[2], 0, 1, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], 1, 1, n1[0], n1[1], n1[2]]
                vertices += [v2[0], v2[1], v2[2], 0.5, 0, n2[0], n2[1], n2[2]]
                indices += [ c + 0, c + 1, c +2 ]
                c += 3
            
            # Creamos los triangulos inferiores
            # v0 ---------- v3
            #   \          /
            #    \        /
            #     \      /
            #      \    /
            #       \  /
            #        v1
            elif i == (N-2):
                #           vertices           UV coord    normales
                vertices += [v0[0], v0[1], v0[2], 0, 0, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], 0.5, 1, n1[0], n1[1], n1[2]]
                vertices += [v3[0], v3[1], v3[2], 1, 0, n3[0], n3[1], n3[2]]
                indices += [ c + 0, c + 1, c +2 ]
                c += 3
            
            # Creamos los quads intermedios
            #  v0 -------------- v3
            #  | \                |
            #  |    \             |
            #  |       \          |
            #  |          \       |
            #  |             \    |
            #  |                \ |
            #  v1 -------------- v2
            else: 
                #           vertices           UV coord    normales
                vertices += [v0[0], v0[1], v0[2], 0, 0, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], 0, 1, n1[0], n1[1], n1[2]]
                vertices += [v2[0], v2[1], v2[2], 1, 1, n2[0], n2[1], n2[2]]
                vertices += [v3[0], v3[1], v3[2], 0, 1, n3[0], n3[1], n3[2]]
                indices += [ c + 0, c + 1, c +2 ]
                indices += [ c + 2, c + 3, c + 0 ]
                c += 4
    return bs.Shape(vertices, indices)

class Ball:
    def __init__(self, pipeline, position, velocity):
        shape = bs.createTextureNormalSphere(20)
        # addapting the size of the circle's vertices to have a circle
        # with the desired radius
        scaleFactor = 2 * RADIUS
        bs.scaleVertices(shape, 6, (scaleFactor, scaleFactor, scaleFactor))
        self.pipeline = pipeline
        self.gpuShape = createGPUShape(self.pipeline, shape)
        # Add texture *****
        self.position = position
        self.radius = RADIUS
        self.velocity = velocity

    def action(self, deltaTime):
        # Euler integration
        normaVelocidad = np.linalg.norm(self.velocity)
        if normaVelocidad<0.1:
            self.velocity = np.array([0.0,0.0,0.0])
        if normaVelocidad == 0:
            friccion = COEF_FRICTION *self.velocity
        else:
            friccion = COEF_FRICTION * np.linalg.norm(self.velocity)
        self.velocity += deltaTime * friccion
        self.position += self.velocity * deltaTime

    def draw(self):
        glUniformMatrix4fv(glGetUniformLocation(self.pipeline.shaderProgram, "model"), 1, GL_TRUE,
            tr.translate(self.position[0], self.position[1], self.position[2])
        )
        self.pipeline.drawCall(self.gpuShape)

def rotate2D(vector, theta):
    """
    Direct application of a 2D rotation
    """
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)

    return np.array([
        cos_theta * vector[0] - sin_theta * vector[1],
        sin_theta * vector[0] + cos_theta * vector[1]
    ], dtype = np.float32)

def collide(circle1, circle2):
    """
    If there are a collision between the circles, it modifies the velocity of
    both circles in a way that preserves energy and momentum.
    """
    
    assert isinstance(circle1, Ball)
    assert isinstance(circle2, Ball)

    normal = circle2.position - circle1.position
    normal /= np.linalg.norm(normal)

    circle1MovingToNormal = np.dot(circle2.velocity, normal) > 0.0
    circle2MovingToNormal = np.dot(circle1.velocity, normal) < 0.0

    if not (circle1MovingToNormal and circle2MovingToNormal):

        # obtaining the tangent direction
        tangent = rotate2D(normal, np.pi/2.0)

        # Projecting the velocity vector over the normal and tangent directions
        # for both circles, 1 and 2.
        v1n = np.dot(circle1.velocity, normal) * normal
        v1t = np.dot(circle1.velocity, tangent) * tangent

        v2n = np.dot(circle2.velocity, normal) * normal
        v2t = np.dot(circle2.velocity, tangent) * tangent

        # swaping the normal components...
        # this means that we applying energy and momentum conservation
        circle1.velocity = (v2n + v1t) * COEF_RESTITUCION
        circle2.velocity = (v1n + v2t) * COEF_RESTITUCION

def areColliding(circle1, circle2):
    assert isinstance(circle1, Circle)
    assert isinstance(circle2, Circle)

    difference = circle2.position - circle1.position
    distance = np.linalg.norm(difference)
    collisionDistance = circle2.radius + circle1.radius
    return distance < collisionDistance

def collideWithBorder(circle):

    # Right
    if circle.position[0] + circle.radius > 110.0:
        circle.velocity[0] = -abs(circle.velocity[0])

    # Left
    if circle.position[0] < -110.0 + circle.radius:
        circle.velocity[0] = abs(circle.velocity[0])

    # Top
    if circle.position[1] > 50.0 - circle.radius:
        circle.velocity[1] = -abs(circle.velocity[1])

    # Bottom
    if circle.position[1] < -50.0 + circle.radius:
        circle.velocity[1] = abs(circle.velocity[1])

def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

    elif key == glfw.KEY_1:
        controller.viewTop = not controller.viewTop



if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 1800
    height = 1000
    title = "PoolParty"
    window = glfw.create_window(width, height, title, None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Defining shader programs
    phongTexturePipeline = ls.SimpleTexturePhongShaderProgram()
    gouraudTexturePipeline = ls.SimpleTextureGouraudShaderProgram()
    lightingPipeline = ls.MultipleTexturePhongShaderProgram()

    

    # Setting up the clear screen color
    glClearColor(0.5, 0.5, 0.5, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory
    #Mesa
    table = objr.readOBJ(getAssetPath('table.obj'))
    gpuTable = createGPUShape(gouraudTexturePipeline, table)
    gpuTable.texture = es.textureSimpleSetup(
        getAssetPath("texturaRed.jpg"), GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)
    
    #Bolas
    

    #Lighting uniforms
    
    t0 = glfw.get_time()
    camera_theta = 0

    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)

    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0)


    while not glfw.window_should_close(window):

        # Measuring performance
        perfMonitor.update(glfw.get_time())
        glfw.set_window_title(window, title + str(perfMonitor))

        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
            camera_theta -= 2 * dt

        if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
            camera_theta += 2* dt

        
        if controller.viewTop:
            # Setting up the projection transform
            projection = tr.ortho(-125, 125, -65, 65, 0.1, 200)

            # Setting up the view transform
            R = 0.00001
            camX = R * np.sin(np.pi)
            camY = R * np.cos(np.pi)
            viewPos = np.array([camX, camY, 170])
            view = tr.lookAt(
                viewPos,
                np.array([0,0,1]),
                np.array([0,0,1])
            )
        if not controller.viewTop: 
            # Setting up the projection transform
            projection = tr.perspective(60, float(width)/float(height), 0.1, 400)

            # Setting up the view transform
            R = 2
            camX = R * np.sin(camera_theta)
            camY = R * np.cos(camera_theta)
            viewPos = np.array([0, 0, 71])
            view = tr.lookAt(
                viewPos,
                np.array([camX,camY,71.5]),
                np.array([0,0,1])
            )


        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Drawing shapes
        #lightingPipeline = gouraudTexturePipeline
        glUseProgram(lightingPipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ld"), 0.5, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ls"), 0.5, 0.5, 0.5)

        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "lightPosition"), 0, 0, 80)
        
        glUniform1ui(glGetUniformLocation(lightingPipeline.shaderProgram, "shininess"), 1000)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "constantAttenuation"), 0.001)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "linearAttenuation"), 0.1)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "quadraticAttenuation"), 0.01)

        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1], viewPos[2])
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.uniformScale(1))
        lightingPipeline.drawCall(gpuTable)

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)
    
    gpuTable.clear()
    glfw.terminate()