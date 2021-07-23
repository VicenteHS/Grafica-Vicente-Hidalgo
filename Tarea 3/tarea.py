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

    

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory
    table = objr.readOBJ(getAssetPath('table.obj'))
    gpuTable = createGPUShape(phongTexturePipeline, table)
    gpuTable.texture = es.textureSimpleSetup(
        getAssetPath("texturaRed.jpg"), GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)

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
        print(controller.viewTop)

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
            camX = R * np.sin(0)
            camY = R * np.cos(0)
            viewPos = np.array([camX, camY, 170])
            view = tr.lookAt(
                viewPos,
                np.array([0,0,1]),
                np.array([0,0,1])
            )
        if not controller.viewTop: 
            # Setting up the projection transform
            projection = tr.perspective(60, float(width)/float(height), 0.1, 200)

            # Setting up the view transform
            R = 0.00001
            camX = R * np.sin(0)
            camY = R * np.cos(0)
            viewPos = np.array([camX, camY, 170])
            view = tr.lookAt(
                viewPos,
                np.array([0,0,1]),
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
        glUseProgram(phongTexturePipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(phongTexturePipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(phongTexturePipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(phongTexturePipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

        glUniform3f(glGetUniformLocation(phongTexturePipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(phongTexturePipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
        glUniform3f(glGetUniformLocation(phongTexturePipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        glUniform3f(glGetUniformLocation(phongTexturePipeline.shaderProgram, "lightPosition"), 0, 0, 170)
        
        glUniform1ui(glGetUniformLocation(phongTexturePipeline.shaderProgram, "shininess"), 100)
        glUniform1f(glGetUniformLocation(phongTexturePipeline.shaderProgram, "constantAttenuation"), 0.001)
        glUniform1f(glGetUniformLocation(phongTexturePipeline.shaderProgram, "linearAttenuation"), 0.1)
        glUniform1f(glGetUniformLocation(phongTexturePipeline.shaderProgram, "quadraticAttenuation"), 0.01)

        glUniformMatrix4fv(glGetUniformLocation(phongTexturePipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniform3f(glGetUniformLocation(phongTexturePipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1], viewPos[2])
        glUniformMatrix4fv(glGetUniformLocation(phongTexturePipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(phongTexturePipeline.shaderProgram, "model"), 1, GL_TRUE, tr.uniformScale(1))
        phongTexturePipeline.drawCall(gpuTable)

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)
    
    gpuTable.clear()
    glfw.terminate()