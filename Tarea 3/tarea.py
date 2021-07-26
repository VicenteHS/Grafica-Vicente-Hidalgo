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
import grafica.sphere as sp
import math


CIRCLE_DISCRETIZATION = 20
RADIUS = 0.6
COEF_FRICTION = 0.2
COEF_RESTITUCION = 1

# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.viewTop = True
        self.movimiento = False
        self.accurate = False
        self.temblor = False
        self.temblor2 = False

# We will use the global controller as communication with the callback function
controller = Controller()

# Convenience function to ease initialization
def createGPUShape(pipeline, shape):
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuShape



class Ball:
    def __init__(self, pipeline, position, velocity,r,g,b):
        shape = sp.createColorNormalSphere(20,r,g,b)
        # addapting the size of the circle's vertices to have a circle
        # with the desired radius
        scaleFactor = 2 * RADIUS
        bs.scaleVertices(shape, 9, (scaleFactor, scaleFactor, scaleFactor))
        self.pipeline = pipeline
        self.gpuShape = createGPUShape(self.pipeline, shape)
        self.position = position
        self.radius = RADIUS
        self.velocity = velocity

    def action(self, deltaTime):
        # Euler integration
        normaVelocidad = np.linalg.norm(self.velocity)
        if normaVelocidad<0.01:
            self.velocity = np.array([0.0,0.0,0.0])
            friccion = COEF_FRICTION *self.velocity

        else:
            friccion = COEF_FRICTION * (self.velocity/np.linalg.norm(self.velocity))*-10
        self.velocity += deltaTime * friccion
        self.position += self.velocity * deltaTime

    def draw(self):
        glUniformMatrix4fv(glGetUniformLocation(self.pipeline.shaderProgram, "model"), 1, GL_TRUE,tr.matmul([
            tr.translate(self.position[0], self.position[1], self.position[2]),
            tr.uniformScale(0.5)
        ])
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
        sin_theta * vector[0] + cos_theta * vector[1],
        0
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
        circle1.velocity = (v2n + v1t) 
        circle2.velocity = (v1n + v2t)

def areColliding(circle1, circle2):
    assert isinstance(circle1, Ball)
    assert isinstance(circle2, Ball)

    difference = circle2.position - circle1.position
    distance = np.linalg.norm(difference)
    collisionDistance = circle2.radius*0.5 + circle1.radius*0.5
    return distance < collisionDistance

def collideWithBorder(circle):

    # Right
    if circle.position[0] + circle.radius*0.5 > 11.0:
        circle.velocity[0] = -abs(circle.velocity[0])

    # Left
    if circle.position[0] < -11.0 + circle.radius*0.5:
        circle.velocity[0] = abs(circle.velocity[0])

    # Top
    if circle.position[1] > 5.0 - circle.radius*0.5:
        circle.velocity[1] = -abs(circle.velocity[1])

    # Bottom
    if circle.position[1] < -5.0 + circle.radius*0.5:
        circle.velocity[1] = abs(circle.velocity[1])

def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller


    if key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

    elif key == glfw.KEY_1:
        controller.viewTop = not controller.viewTop
    
    elif key == glfw.KEY_A:
        controller.accurate = not controller.accurate
    
    elif key == glfw.KEY_T:
        controller.temblor = True


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
    phongSimplePipeline = ls.SimplePhongShaderProgram()
    mvpTexturePipeline = es.SimpleTextureModelViewProjectionShaderProgram()
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
    table = objr.readOBJ(getAssetPath('mesa3.obj'))
    gpuTable = createGPUShape(gouraudTexturePipeline, table)
    gpuTable.texture = es.textureSimpleSetup(
        getAssetPath("texturaRed2.jpg"), GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)
    
    #Taco
    taco = objr.readOBJ2(getAssetPath('taco2.obj'))
    gpuTaco = createGPUShape(mvpTexturePipeline, taco)
    gpuTaco.texture = es.textureSimpleSetup(
        getAssetPath("madera4.jpg"), GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)
    
    #Bolas
    balls = []
    #You can form an equal side triangle and the distance will be sqrt of 3 R
    sqrt3 = math.sqrt(3)
    positionBalls = [
        np.array([6, 0, 6.8 + RADIUS]),
        np.array([-5.6, 0, 6.8 + RADIUS]),
        np.array([-5.6 - sqrt3*RADIUS*0.5, RADIUS*0.5, 6.8 + RADIUS]),
        np.array([-5.6 - sqrt3*RADIUS*0.5, -RADIUS*0.5, 6.8 + RADIUS]),
        np.array([-5.6 - sqrt3*RADIUS*1, RADIUS*0.5*2, 6.8 + RADIUS]),
        np.array([-5.6 - sqrt3*RADIUS*1, 0, 6.8 + RADIUS]),
        np.array([-5.6 - sqrt3*RADIUS*1, -RADIUS*0.5*2, 6.8 + RADIUS]),
        np.array([-5.6 - sqrt3*RADIUS*1.5, RADIUS*1.5, 6.8 + RADIUS]),
        np.array([-5.6 - sqrt3*RADIUS*1.5, RADIUS*0.5, 6.8 + RADIUS]),
        np.array([-5.6 - sqrt3*RADIUS*1.5, -RADIUS*0.5, 6.8 + RADIUS]),
        np.array([-5.6 - sqrt3*RADIUS*1.5, -RADIUS*1.5, 6.8 + RADIUS]),
        np.array([-5.6 - sqrt3*RADIUS*2,  RADIUS*2.0, 6.8 + RADIUS]),
        np.array([-5.6 - sqrt3*RADIUS*2,  RADIUS*1.0, 6.8 + RADIUS]),
        np.array([-5.6 - sqrt3*RADIUS*2,  0, 6.8 + RADIUS]),
        np.array([-5.6 - sqrt3*RADIUS*2,  -RADIUS*1.0, 6.8 + RADIUS]),
        np.array([-5.6 - sqrt3*RADIUS*2,  -RADIUS*2.0, 6.8 + RADIUS])
    ]

    colorBalls = [
        np.array([1,1,1]),
        np.array([1,1,0]),
        np.array([1,1,0]),
        np.array([0,0,1]),
        np.array([1,1,0]),
        np.array([0,0,0]),
        np.array([0,0,1]),
        np.array([0,0,1]),
        np.array([1,1,0]),
        np.array([0,0,1]),
        np.array([1,1,0]),
        np.array([1,1,0]),
        np.array([0,0,1]),
        np.array([1,1,0]),
        np.array([1,1,0]),
        np.array([0,0,1])
    ]

    velocityBall = [
        np.array([random.uniform(-3, 3),random.uniform(-3, 3),0],dtype= np.float64),
        np.array([random.uniform(-3, 3),random.uniform(-3, 3),0],dtype= np.float64),
        np.array([random.uniform(-3, 3),random.uniform(-3, 3),0],dtype= np.float64),
        np.array([random.uniform(-3, 3),random.uniform(-3, 3),0],dtype= np.float64),
        np.array([random.uniform(-3, 3),random.uniform(-3, 3),0],dtype= np.float64),
        np.array([random.uniform(-3, 3),random.uniform(-3, 3),0],dtype= np.float64),
        np.array([random.uniform(-3, 3),random.uniform(-3, 3),0],dtype= np.float64),
        np.array([random.uniform(-3, 3),random.uniform(-3, 3),0],dtype= np.float64),
        np.array([random.uniform(-3, 3),random.uniform(-3, 3),0],dtype= np.float64),
        np.array([random.uniform(-3, 3),random.uniform(-3, 3),0],dtype= np.float64),
        np.array([random.uniform(-3, 3),random.uniform(-3, 3),0],dtype= np.float64),
        np.array([random.uniform(-3, 3),random.uniform(-3, 3),0],dtype= np.float64),
        np.array([random.uniform(-3, 3),random.uniform(-3, 3),0],dtype= np.float64),
        np.array([random.uniform(-3, 3),random.uniform(-3, 3),0],dtype= np.float64),
        np.array([random.uniform(-3, 3),random.uniform(-3, 3),0],dtype= np.float64),
        np.array([random.uniform(-3, 3),random.uniform(-3, 3),0],dtype= np.float64)
    ]
    for i in range(16):
        bola = Ball(phongSimplePipeline, positionBalls[i], np.array([0.0, 0.0, 0.0]), colorBalls[i][0], colorBalls[i][1], colorBalls[i][2])
        balls.append(bola)

    

    #Lighting uniforms
    
    t0 = glfw.get_time()
    camera_theta = -np.pi/2

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
        deltaTime = perfMonitor.getDeltaTime()
        bolaBlanca = balls[0]
        posBolaBlanca = bolaBlanca.position
        controller.movimiento = False

        if not controller.accurate:

            if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
                camera_theta -= 2 * dt

            if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
                camera_theta += 2* dt

        else:

            if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
                camera_theta -= 0.5 * dt

            if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
                camera_theta += 0.5* dt
        
        if controller.viewTop:
            # Setting up the projection transform
            projection = tr.ortho(-12.5, 12.5, -6.5, 6.5, 0.1, 200)

            # Setting up the view transform
            R = 0.00001
            camX = R * np.sin(np.pi)
            camY = R * np.cos(np.pi)
            viewPos = np.array([camX, camY, 17])
            view = tr.lookAt(
                viewPos,
                np.array([0,0,1]),
                np.array([0,0,1])
            )
        if not controller.viewTop: 
            # Setting up the projection transform
            projection = tr.perspective(60, float(width)/float(height), 0.1, 400)

            # Setting up the view transform
            R = 5
            camX = -R * np.sin(camera_theta) + posBolaBlanca[0]
            camY = -R * np.cos(camera_theta) + posBolaBlanca[1]
            viewPos = np.array([camX, camY, 10])
            view = tr.lookAt(
                viewPos,
                posBolaBlanca,
                np.array([0,0,1])
            )

        if controller.temblor and not controller.temblor2:
            for i in range(1,len(balls)):
                balls[i].velocity = velocityBall[i]
                controller.temblor2 = True



        #Physics!
        for ball in balls:
            #Moving each sphere
            ball.action(deltaTime)

            # checking and processing collisions among spheres
            collideWithBorder(ball)

            if np.linalg.norm(ball.velocity) > 0:
                controller.movimiento = True

        # checking and processing collisions among spheres
        for i in range(len(balls)):
            for j in range(i+1, len(balls)):
                if areColliding(balls[i], balls[j]):
                    collide(balls[i], balls[j])

        # Golpe
        if (glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS) and  not controller.movimiento:
            bolaBlanca.velocity = np.array([np.sin(camera_theta),np.cos(camera_theta), 0.0])*10

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Drawing shapes
        glUseProgram(lightingPipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ld"), 0.5, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ls"), 0.5, 0.5, 0.5)

        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ks"), 0, 0, 0)

        glUniform1ui(glGetUniformLocation(lightingPipeline.shaderProgram, "shininess"), 1000)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "constantAttenuation"), 0.001)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "linearAttenuation"), 0.1)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "quadraticAttenuation"), 0.01)

        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1], viewPos[2])
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.uniformScale(0.1))
        lightingPipeline.drawCall(gpuTable)

        # Drawing Taco
        if not controller.movimiento:
            glUseProgram(mvpTexturePipeline.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(mvpTexturePipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
            glUniformMatrix4fv(glGetUniformLocation(mvpTexturePipeline.shaderProgram, "view"), 1, GL_TRUE, view)
            glUniformMatrix4fv(glGetUniformLocation(mvpTexturePipeline.shaderProgram, "model"), 1, GL_TRUE, tr.matmul([
                tr.translate(posBolaBlanca[0], posBolaBlanca[1], posBolaBlanca[2]),
                tr.rotationZ(-camera_theta),
                tr.rotationX(-np.pi/12),
                tr.uniformScale(3)
            ]))
            mvpTexturePipeline.drawCall(gpuTaco)

        # Drawing balls
        glUseProgram(phongSimplePipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(phongSimplePipeline.shaderProgram, "La"), 0.85, 0.85, 0.85)
        glUniform3f(glGetUniformLocation(phongSimplePipeline.shaderProgram, "Ld"), 0.8, 0.8, 0.8)
        glUniform3f(glGetUniformLocation(phongSimplePipeline.shaderProgram, "Ls"), 0.6, 0.6, 0.6)

        glUniform3f(glGetUniformLocation(phongSimplePipeline.shaderProgram, "Ka"), 0.8, 0.8, 0.8)
        glUniform3f(glGetUniformLocation(phongSimplePipeline.shaderProgram, "Kd"), 0.8, 0.8, 0.8)
        glUniform3f(glGetUniformLocation(phongSimplePipeline.shaderProgram, "Ks"), 0.5, 0.5, 0.5)

        glUniform1ui(glGetUniformLocation(phongSimplePipeline.shaderProgram, "shininess"), 10)
        glUniform1f(glGetUniformLocation(phongSimplePipeline.shaderProgram, "constantAttenuation"), 0.001)
        glUniform1f(glGetUniformLocation(phongSimplePipeline.shaderProgram, "linearAttenuation"), 0.1)
        glUniform1f(glGetUniformLocation(phongSimplePipeline.shaderProgram, "quadraticAttenuation"), 0.01)

        glUniform3f(glGetUniformLocation(phongSimplePipeline.shaderProgram, "lightPosition"), 0, 0, 15)
        glUniformMatrix4fv(glGetUniformLocation(phongSimplePipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniform3f(glGetUniformLocation(phongSimplePipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1], viewPos[2])
        glUniformMatrix4fv(glGetUniformLocation(phongSimplePipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        for i in range(len(balls)):
            balls[i].draw()
        
    
        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)
    
    gpuTable.clear()
    gpuTaco.clear()
    for i in range(len(balls)):
        balls[i].clear()
    glfw.terminate()