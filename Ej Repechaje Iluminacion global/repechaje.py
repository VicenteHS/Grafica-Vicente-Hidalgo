# coding=utf-8
"""Textures and transformations in 3D"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
from grafica.assets_path import getAssetPath

__author__ = "Daniel Calderon"
__license__ = "MIT"


# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.x = 0
        self.y = 9.75


# global controller as communication with the callback function
controller = Controller()

def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)


def createFondo():
    # Creating the end by a shape that is a cube with normals and textures
    # Defining locations,texture coordinates and normals for each vertex of the shape  
    vertices = [
    #   positions            tex coords   normals
    # Z+
        -0.5, -0.5,  0.5,    0, 1,
         0.5, -0.5,  0.5,    1, 1,
         0.5,  0.5,  0.5,    1, 0, 
        -0.5,  0.5,  0.5,    0, 0, 
    # Z-          
        -0.5, -0.5, -0.5,    0, 1,
         0.5, -0.5, -0.5,    1, 1,
         0.5,  0.5, -0.5,    1, 0, 
        -0.5,  0.5, -0.5,    0, 0, 
       
    # X+          
         0.5, -0.5, -0.5,    0, 1, 
         0.5,  0.5, -0.5,    1, 1, 
         0.5,  0.5,  0.5,    1, 0,
         0.5, -0.5,  0.5,    0, 0,   
    # X-          
        -0.5, -0.5, -0.5,    0, 1, 
        -0.5,  0.5, -0.5,    1, 1,
        -0.5,  0.5,  0.5,    1, 0,
        -0.5, -0.5,  0.5,    0, 0, 
    # Y+          
        -0.5,  0.5, -0.5,    0, 1, 
         0.5,  0.5, -0.5,    1, 1, 
         0.5,  0.5,  0.5,    1, 0, 
        -0.5,  0.5,  0.5,    0, 0,  
    # Y-          
        -0.5, -0.5, -0.5,    0, 1,
         0.5, -0.5, -0.5,    1, 1,
         0.5, -0.5,  0.5,    1, 0, 
        -0.5, -0.5,  0.5,    0, 0
        ]   

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
          0, 1, 2, 2, 3, 0, # Z+
          7, 6, 5, 5, 4, 7, # Z-
          8, 9,10,10,11, 8, # X+
         15,14,13,13,12,15, # X-
         19,18,17,17,16,19, # Y+
         20,21,22,22,23,20] # Y-

    
    return bs.Shape(vertices, indices)


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 800
    height = 800

    window = glfw.create_window(width, height, "Dice", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Creating shader programs for textures and for colors
    textureShaderProgram = es.SimpleTextureModelViewProjectionShaderProgram()
    colorShaderProgram = es.SimpleModelViewProjectionShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)
    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Creating shapes on GPU memory
    def createGPUShape(pipeline, shape, draw = GL_STATIC_DRAW):
        gpuShape = es.GPUShape().initBuffers()
        pipeline.setupVAO(gpuShape)
        gpuShape.fillBuffers(shape.vertices, shape.indices, draw)
        return gpuShape

    gpuFondo = createGPUShape(textureShaderProgram, createFondo())
    gpuFondo.texture = es.textureSimpleSetup(
        getAssetPath("Fondo 2.png"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)
    
    gpuQuad = createGPUShape(textureShaderProgram, createFondo())
    gpuQuad.texture = es.textureSimpleSetup(
        getAssetPath("boo.png"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)
    
    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        #Movimiento
        if (glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS) :
            controller.y -= 0.001
        if (glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS) and  controller.y < 9.75:
            controller.y += 0.001
        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS) and controller.x < 0.0005:
            controller.x += 0.000005
        if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS) and  controller.x > -0.0005:
            controller.x -= 0.000005

        projection = tr.perspective(np.pi/6,float(width)/float(height),0.1,100)

        view = tr.lookAt(
            np.array([0,10,0]),
            np.array([0,-1,0]),
            np.array([0,0,1])
        )

        theta = glfw.get_time()
        axis = np.array([1,-1,1])
        axis = axis / np.linalg.norm(axis)
        model = tr.identity()

        #Drawing Fondo
        glUseProgram(textureShaderProgram.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "model"), 1, GL_TRUE, tr.matmul([
            tr.translate(0, -1, 0),
            tr.uniformScale(0.1)]))
        textureShaderProgram.drawCall(gpuFondo)

        #Drawing Quad
        glUseProgram(textureShaderProgram.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "model"), 1, GL_TRUE, tr.matmul([
            tr.translate(controller.x, controller.y, -0.0009),
            tr.uniformScale(0.0005)]))
        textureShaderProgram.drawCall(gpuQuad)
       
        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuAxis.clear()
    gpuDice.clear()

    glfw.terminate()








