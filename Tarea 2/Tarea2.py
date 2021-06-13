# coding=utf-8
"""Showing lighting effects over two textured objects: Flat, Gauraud and Phong"""

import glfw
import copy
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.lighting_shaders as ls
from grafica.assets_path import getAssetPath
import grafica.scene_graph as sg
import grafica.ex_curves as cv

__author__ = "Daniel Calderon"
__license__ = "MIT"


LIGHT_FLAT    = 0
LIGHT_GOURAUD = 1
LIGHT_PHONG   = 2


# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.showAxis = True
        self.lightingModel = LIGHT_FLAT


# We will use the global controller as communication with the callback function
controller = Controller()

def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_LEFT_CONTROL:
        controller.showAxis = not controller.showAxis

    elif key == glfw.KEY_Q:
        controller.lightingModel = LIGHT_FLAT

    elif key == glfw.KEY_W:
        controller.lightingModel = LIGHT_GOURAUD

    elif key == glfw.KEY_E:
        controller.lightingModel = LIGHT_PHONG

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)


################################################################
################################################################
#Creating a boat for the tobogan.

def createBoat():
    # Defining locations and texture coordinates for each vertex of the shape  
    vertices = [
    #   positions         tex coords   normals
    # Down Face of the boat
        -0.5, -0.5, -0.5, 1/2, 1,      0,0,-1,
         0.5, -0.5, -0.5, 1, 1,        0,0,-1,
         0.5,  0.5, -0.5, 1, 2/3,      0,0,-1,
        -0.5,  0.5, -0.5, 1/2, 2/3,    0,0,-1,
        
    # Rigth Face of the boat
         0.5, -0.5, -0.5,   0,   1,   1,0,0,
         0.5,  0.5, -0.5, 1/2,   1,   1,0,0,
         0.5,  0.5,  0.5, 1/2, 2/3,   1,0,0,
         0.5, -0.5,  0.5,   0, 2/3,   1,0,0,
 
    # Left Face of the boat
        -0.5, -0.5, -0.5, 1/2, 1/3,   -1,0,0,
        -0.5,  0.5, -0.5,   1, 1/3,   -1,0,0,
        -0.5,  0.5,  0.5,   1,   0,   -1,0,0,
        -0.5, -0.5,  0.5, 1/2,   0,   -1,0,0,

    # Front face of the boat
        -0.5,  0.5, -0.5, 1/2, 2/3,   0,1,0,
         0.5,  0.5, -0.5,   1, 2/3,   0,1,0,
         0.5,  0.5,  0.5,   1, 1/3,   0,1,0,
        -0.5,  0.5,  0.5, 1/2, 1/3,   0,1,0,

    # Back Face of the boat
        -0.5, -0.5, -0.5,   0, 2/3,   0,-1,0,
         0.5, -0.5, -0.5, 1/2, 2/3,   0,-1,0,
         0.5, -0.5,  0.5, 1/2, 1/3,   0,-1,0,
        -0.5, -0.5,  0.5,   0, 1/3,   0,-1,0,]

    # Defining Indices
    indices = [
          0, 1, 2, 2, 3, 0, 
          7, 6, 5, 5, 4, 7, 
          8, 9,10,10,11, 8, 
         15,14,13,13,12,15, 
         19,18,17,17,16,19]
        
    return bs.Shape(vertices, indices)
    

def createStick():
    # Defining locations and texture coordinates for each vertex of the shape  
    vertices = [
    #   positions         tex coords   normals
    # Up face Stick
        -0.1, -0.1,  1.0, 0,   1/3,    0,0,1,
         0.1, -0.1,  1.0, 1/2, 1,    0,0,1,
         0.1,  0.1,  1.0, 1,   0,    0,0,1,
        -0.1,  0.1,  1.0, 0,     0,    0,0,1,
    # Down face stick
        -0.1, -0.1, 0.0, 1/2, 1,      0,0,-1,
         0.1, -0.1, 0.0, 1, 1,        0,0,-1,
         0.1,  0.1, 0.0, 1, 2/3,      0,0,-1,
        -0.1,  0.1, 0.0, 1/2, 2/3,    0,0,-1,
    # Right face stick
         0.1, -0.1, 0.0,   0,   1,   1,0,0,
         0.1,  0.1, 0.0, 1/2,   1,   1,0,0,
         0.1,  0.1, 1.0, 1/2, 2/3,   1,0,0,
         0.1, -0.1, 1.0,   0, 2/3,   1,0,0,

    # Left face stick
         -0.1, -0.1, 0.0,   0,   1,   1,0,0,
         -0.1,  0.1, 0.0, 1/2,   1,   1,0,0,
         -0.1,  0.1, 1.0, 1/2, 2/3,   1,0,0,
         -0.1, -0.1, 1.0,   0, 2/3,   1,0,0,

    # Front face stick
         -0.1,  0.1,  0.0, 1/2, 2/3,   0,1,0,
          0.1,  0.1,  0.0,   1, 2/3,   0,1,0,
          0.1,  0.1,  1.0,   1, 1/3,   0,1,0,
         -0.1,  0.1,  1.0, 1/2, 1/3,   0,1,0,

    # Back face stick
        -0.1, -0.1,  0.0,   0, 2/3,   0,-1,0,
         0.1, -0.1,  0.0, 1/2, 2/3,   0,-1,0,
         0.1, -0.1,  1.0, 1/2, 1/3,   0,-1,0,
        -0.1, -0.1,  1.0,   0, 1/3,   0,-1,0,]
    
    # Defining Indices
    indices = [
          0, 1, 2, 2, 3, 0, # Z+
          7, 6, 5, 5, 4, 7, # Z-
          8, 9,10,10,11, 8, # X+
         15,14,13,13,12,15, # X-
         19,18,17,17,16,19, # Y+
         20,21,22,22,23,20] # Y-

    return bs.Shape(vertices, indices)


def createFlag():
    # Defining locations and texture coordinates for each vertex of the shape  
    vertices = [
    #   positions         tex coords   normals
    # Up face Stick
         0.0,  0.0,  0.3, 0.5,   0,    1,1,1,
        -0.3, -0.3,  0.0, 0,     1,    0,0,1,
         0.3, -0.3,  0.0, 1,     1,    0,0,1,
         0.3,  0.3,  0.0, 0,     1,    0,0,1,
        -0.3,  0.3,  0.0, 1,     1,    0,0,1]

    # Defining Indices
    indices = [
          0,1,2,
          0,2,3,
          0,3,4,
          0,4,1,
          1,2,3,
          2,3,4] 

    return bs.Shape(vertices, indices)

def CompleteBoat():
    def createGPUShape(pipeline, shape):
        gpuShape = es.GPUShape().initBuffers()
        pipeline.setupVAO(gpuShape)
        gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
        return gpuShape
    
    # gpuBoat
    shapeBoat = createBoat()
    gpuBoat = createGPUShape(textureGouraudPipeline, shapeBoat)
    gpuBoat.texture = es.textureSimpleSetup(
        getAssetPath("madera.jpg"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)
    

    # gpuStick
    shapeStick = createStick()
    gpuStick = createGPUShape(textureGouraudPipeline, shapeStick)
    gpuStick.texture = es.textureSimpleSetup(
        getAssetPath("madera2.jpg"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)

    # gpuFlag
    shapeStick = createFlag()
    gpuFlag = createGPUShape(textureGouraudPipeline, shapeStick)
    gpuFlag.texture = es.textureSimpleSetup(
        getAssetPath("bandera.jpg"), GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_LINEAR, GL_LINEAR)
    
    # SceneGraph
    # ScaleBase
    base = sg.SceneGraphNode("Base")
    base.transform = tr.scale(1.5, 0.8, 0.7)
    base.childs = [gpuBoat]

    # ScaleMastil
    mastil = sg.SceneGraphNode("Mastil")
    mastil.transform = tr.scale(1, 0.8, 1)
    mastil.childs = [gpuStick]

    # ScaleFlag
    flag = sg.SceneGraphNode("Flag")
    flag.transform = tr.scale(1.4, 1.4, 1)
    flag.childs = [gpuFlag]

    #RotatedFlag
    RotatedFlag = sg.SceneGraphNode("RotatedFlag")
    RotatedFlag.transform = tr.rotationZ(0)
    RotatedFlag.childs = [flag]

    # TranslatedFlag
    TranslatedFlag = sg.SceneGraphNode("TranslatedFlag")
    TranslatedFlag.transform = tr.translate(0, 0, 1)
    TranslatedFlag.childs = [RotatedFlag]

    # DefBoat
    DefBoat = sg.SceneGraphNode("DefBoat")
    DefBoat.transform = tr.scale(0.5, 0.5, 0.5)
    DefBoat.childs = [base, mastil, TranslatedFlag]

    return DefBoat





################################################################
################################################################
#Curves before tobogan



def createCurve(r,g,b):
    vertices = []
    indices = []
    M = cv.CatmullRomMatrix(
        np.array([[0, 0, 1]]).T,
        np.array([[0, 1, 0]]).T,
        np.array([[1, 0, 1]]).T,
        np.array([[1, 1, 0]]).T
    )
    curve = cv.evalCurve(M,20)
    delta = 1 / len(curve)
    x_0 = -0.5 # Posicion x inicial de la recta inferior
    y_0 = -0.2 # Posicion y inicial de la recta inferior
    counter = 0 # Contador de vertices, para indicar los indices

    # Se generan los vertices
    for i in range(len(curve)-1):
        c_0 = curve[i] # punto i de la curva
        r_0 = [x_0 + i*delta, y_0] # punto i de la recta
        c_1 = curve[i + 1] # punto i + 1 de la curva
        r_1 = [x_0 + (i+1)*delta, y_0] # punto i + 1 de la recta
        vertices += [c_0[0], c_0[1], 0, r + 0.3, g + 0.3, b + 0.3]
        vertices += [r_0[0], r_0[1], 0, r, g, b]
        vertices += [c_1[0], c_1[1], 0, r + 0.3, g + 0.3, b + 0.3]
        vertices += [r_1[0], r_1[1], 0, r, g, b]
        indices += [counter + 0, counter +1, counter + 2]
        indices += [counter + 2, counter + 3, counter + 1]
        counter += 4

    return bs.Shape(vertices, indices)

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 1500
    height = 900

    window = glfw.create_window(width, height, "Tobogan", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Different shader programs for different lighting strategies
    textureFlatPipeline = ls.SimpleTextureFlatShaderProgram()
    textureGouraudPipeline = ls.SimpleTextureGouraudShaderProgram()
    texturePhongPipeline = ls.SimpleTexturePhongShaderProgram()

    # This shader program does not consider lighting
    colorPipeline = es.SimpleModelViewProjectionShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Convenience function to ease initialization
    def createGPUShape(pipeline, shape):
        gpuShape = es.GPUShape().initBuffers()
        pipeline.setupVAO(gpuShape)
        gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
        return gpuShape

    # Creating shapes on GPU memory
    gpuAxis = createGPUShape(colorPipeline, bs.createAxis(4))
    gpuCurve = createGPUShape(colorPipeline, createCurve(1,0.5,0.7))

    # Creating Scenegraph of a CompleteBoat
    CompleteBoat = CompleteBoat()

    t0 = glfw.get_time()
    camera_theta = np.pi/4

    while not glfw.window_should_close(window):

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
            
        projection = tr.perspective(45, float(width)/float(height), 0.1, 100)

        camX = 1 * np.sin(camera_theta)
        camY = 1 * np.cos(camera_theta)

        viewPos = np.array([camX,camY,2])

        view = tr.lookAt(
            viewPos,
            np.array([0,0,0]),
            np.array([0,0,1])
        )

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # The axis is drawn without lighting effects
        if controller.showAxis:
            glUseProgram(colorPipeline.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(colorPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
            glUniformMatrix4fv(glGetUniformLocation(colorPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
            glUniformMatrix4fv(glGetUniformLocation(colorPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
            colorPipeline.drawCall(gpuCurve, GL_LINES)
        
        # Selecting the lighting shader program
        if controller.lightingModel == LIGHT_FLAT:
            lightingPipeline = textureFlatPipeline
        elif controller.lightingModel == LIGHT_GOURAUD:
            lightingPipeline = textureGouraudPipeline
        elif controller.lightingModel == LIGHT_PHONG:
            lightingPipeline = texturePhongPipeline
        else:
            raise Exception()
        
        glUseProgram(lightingPipeline.shaderProgram)

        # Setting all uniform shader variables
        
        # White light in all components: ambient, diffuse and specular.
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

        # Object is barely visible at only ambient. Bright white for diffuse and specular components.
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        # TO DO: Explore different parameter combinations to understand their effect!
        
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "lightPosition"), -5, -5, 5)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1], viewPos[2])
        glUniform1ui(glGetUniformLocation(lightingPipeline.shaderProgram, "shininess"), 100)

        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "quadraticAttenuation"), 0.01)

        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "view"), 1, GL_TRUE, view)

        # Drawing
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.translate(0.75,0,0))
        sg.drawSceneGraphNode(CompleteBoat, lightingPipeline, "model")

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuAxis.clear()
    gpuDice.clear()
    gpuDiceBlue.clear()

    glfw.terminate()
