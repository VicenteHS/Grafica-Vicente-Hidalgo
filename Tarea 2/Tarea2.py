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



LIGHT_FLAT    = 0
LIGHT_GOURAUD = 1
LIGHT_PHONG   = 2


# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.showAxis = True
        self.lightingModel = LIGHT_PHONG
        self.Camera2 = False
        self.leftClickOn = False
        self.rightClickOn = False
        self.mousePos = (0.0, 0.0)
        self.ITR = 0
        self.ITR2 = 0

################################################################
################################################################
################################################################
#SHADER MODIFICADO PARA CREAR LINEAS
class CurveShader:

    def __init__(self):

        vertex_shader = """
            #version 130

            uniform mat4 projection;
            uniform mat4 view;
            uniform mat4 model;

            in vec3 position;

            out vec3 newColor;
            void main()
            {
                gl_Position = projection * view * model * vec4(position, 1.0f);
                newColor = vec3(0,0,1);
            }
            """

        fragment_shader = """
            #version 130
            in vec3 newColor;

            out vec4 outColor;
            void main()
            {
                outColor = vec4(newColor, 1.0f);
            }
            """

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + rgb color specification => 3*4  = 12 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        # Binding the VAO and executing the draw call
        glBindVertexArray(gpuShape.vao)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)


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

    elif key == glfw.KEY_C:
        controller.Camera2 = not controller.Camera2

################################################################
################################################################
################################################################
# Mouse definition

# Aca se define la posicion del mouse
def cursor_pos_callback(window, x, y):
    global controller
    controller.mousePos = (x,y)

# Aca se definen los botones del mouse
def mouse_button_callback(window, button, action, mods):

    global controller
    
    """
    glfw.MOUSE_BUTTON_1: left click
    glfw.MOUSE_BUTTON_2: right click
    """

    if (action == glfw.PRESS or action == glfw.REPEAT):
        if (button == glfw.MOUSE_BUTTON_1):
            controller.leftClickOn = True


        if (button == glfw.MOUSE_BUTTON_2):
            controller.rightClickOn = True

    elif (action ==glfw.RELEASE):
        if (button == glfw.MOUSE_BUTTON_1):
            controller.leftClickOn = False

        if (button == glfw.MOUSE_BUTTON_2):
            controller.rightClickOn = False


################################################################
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

    # TranslatedDefBoat
    TranslatedDefBoat = sg.SceneGraphNode("TranslatedDefBoat")
    TranslatedDefBoat.transform = tr.translate(0,0,0)
    TranslatedDefBoat.childs += [DefBoat]

    return TranslatedDefBoat





################################################################
################################################################
################################################################
#Curves before tobogan
Lista = [np.array([[-1, -1, 10]]).T,       #P0
        np.array([[3, 3, 10]]).T,          #P1
        np.array([[-3, 3, 9]]).T,          #P2
        np.array([[-3, -3, 8]]).T,         #P3
        np.array([[3, -3, 7]]).T,          #P4
        np.array([[5, 5, 6]]).T,           #P5
        np.array([[1, 4, 5]]).T,           #P6
        np.array([[-3,-2,4]]).T,           #P7
        np.array([[1,-2,3]]).T,            #P8
        np.array([[3,3,2]]).T,             #P9
        np.array([[-3,3,1]]).T,            #P10
        np.array([[0,0,0]]).T,             #P11
        np.array([[-1, -1, 0]]).T]         #P12

def createLine(N,Lista):
    


    CRcurve = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[0], N).tolist()    #C1
    CRcurve2 = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[1], N).tolist()   #C2
    CRcurve3 = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[2], N).tolist()   #C3
    CRcurve4 = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[3], N).tolist()   #C4
    CRcurve5 = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[4], N).tolist()   #C5
    CRcurve6 = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[5], N).tolist()   #C6
    CRcurve7 = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[6], N).tolist()   #C7
    CRcurve8 = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[7], N).tolist()   #C8
    CRcurve9 = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[8], N).tolist()   #C9
    CRcurve10 = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[9], N).tolist()  #C10
    ver = [CRcurve, CRcurve2, CRcurve3, CRcurve4, CRcurve5, 
            CRcurve6, CRcurve7, CRcurve8, CRcurve9, CRcurve10]

    vertices = []
    indices = []
    for i in range(10*N-9):
        indices.append(i)
    print(indices)

    for i in range(len(CRcurve)):
        for j in range(len(CRcurve[0])):
            vertices.append(CRcurve[i][j])
    for i in range(len(CRcurve)):
        for j in range(len(CRcurve[0])):
            vertices.append(CRcurve2[i][j])
    for i in range(len(CRcurve)):
        for j in range(len(CRcurve[0])):
            vertices.append(CRcurve3[i][j])
    for i in range(len(CRcurve)):
        for j in range(len(CRcurve[0])):
            vertices.append(CRcurve4[i][j])
    for i in range(len(CRcurve)):
        for j in range(len(CRcurve[0])):
            vertices.append(CRcurve5[i][j])
    for i in range(len(CRcurve)):
        for j in range(len(CRcurve[0])):
            vertices.append(CRcurve6[i][j])
    for i in range(len(CRcurve)):
        for j in range(len(CRcurve[0])):
            vertices.append(CRcurve7[i][j])
    for i in range(len(CRcurve)):
        for j in range(len(CRcurve[0])):
            vertices.append(CRcurve8[i][j])
    for i in range(len(CRcurve)):
        for j in range(len(CRcurve[0])):
            vertices.append(CRcurve9[i][j])
    for i in range(len(CRcurve)):
        for j in range(len(CRcurve[0])):
            vertices.append(CRcurve10[i][j])

    return bs.Shape(vertices, indices), ver

curve = createLine(100,Lista)[0]
vertex = []
#List of List of List, but vertex has 1 less, it has the posicions.
ver = createLine(50,Lista)[1]
for i in range(len(ver)):
        for j in range(len(ver[0])):
            vertex.append(ver[i][j])
# So vertex has the positions of our curve









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
    # Mouse a glfw.
    glfw.set_cursor_pos_callback(window, cursor_pos_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)

    ###########################################################################
    ###########################################################################
    ###########################################################################
    # Pipelines
    # Different shader programs for different lighting strategies
    textureFlatPipeline = ls.SimpleTextureFlatShaderProgram()
    textureGouraudPipeline = ls.SimpleTextureGouraudShaderProgram()
    texturePhongPipeline = ls.SimpleTexturePhongShaderProgram()

    # This shader program does not consider lighting
    colorPipeline = es.SimpleModelViewProjectionShaderProgram()

    # This shader program is used for drawing a line
    curvePipeline = CurveShader()

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
    gpuCurve = createGPUShape(curvePipeline, curve)

    # Creating Scenegraph of a CompleteBoat
    CompleteBoat = CompleteBoat()

    t0 = glfw.get_time()
    camera_theta = np.pi/4



    ###########################################################################
    ###########################################################################
    ###########################################################################
    #Star while
    ###########################################################################
    ###########################################################################
    ###########################################################################


    while not glfw.window_should_close(window):

        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the mouse location in opengl coordinates
        mousePosX = 2 * (controller.mousePos[0] - width/2) / width
        mousePosY = 2 * (height/2 - controller.mousePos[1]) / height

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        #Rotate Flag from the boat
        rotatedflag = sg.findNode(CompleteBoat, "RotatedFlag")
        rotatedflag.transform = tr.rotationZ(t1)

        #CKECK THIS !!!!!---------------------------------------------------------------------
        #Translate Boat
        translatedboat = sg.findNode(CompleteBoat, "TranslatedDefBoat")


        if controller.ITR <= len(vertex)-1:
            translatedboat.transform = tr.translate(vertex[controller.ITR][0], vertex[controller.ITR][1], vertex[controller.ITR][2])
            controller.ITR +=1
        if controller.ITR > (len(vertex)-1)/10:
            controller.ITR2 = controller.ITR -40



        # Initial Camera
        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
            camera_theta -= 2 * dt

        if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
            camera_theta += 2* dt
            
        projection = tr.perspective(40, float(width)/float(height), 0.1, 100)

        camX = 10 * np.sin(camera_theta)
        camY = 10 * np.cos(camera_theta)

        # First case of Camera
        if not controller.Camera2:


            viewPos = np.array([camX,camY,5])

            view = tr.lookAt(
                viewPos,
                np.array([0,0,0]),
                np.array([0,0,1])
            )
        
        # Second case of Camera
        if controller.Camera2:
            projection = tr.perspective(40, float(width)/float(height), 0.1, 100)

            view = tr.lookAt(
                np.array([vertex[controller.ITR2][0], vertex[controller.ITR2][1], vertex[controller.ITR2][2]+3]),
                np.array([translatedboat.transform[0][3], translatedboat.transform[1][3], translatedboat.transform[2][3]]),
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
            glUseProgram(curvePipeline.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(curvePipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
            glUniformMatrix4fv(glGetUniformLocation(curvePipeline.shaderProgram, "view"), 1, GL_TRUE, view)
            glUniformMatrix4fv(glGetUniformLocation(curvePipeline.shaderProgram, "model"), 1, GL_TRUE, tr.uniformScale(1.0))
            colorPipeline.drawCall(gpuCurve, GL_LINE_STRIP)

            glUseProgram(colorPipeline.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(colorPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
            glUniformMatrix4fv(glGetUniformLocation(colorPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
            glUniformMatrix4fv(glGetUniformLocation(colorPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.uniformScale(1.0))
            colorPipeline.drawCall(gpuAxis, GL_LINES)
        
        
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
