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
import displacement_view as dv



LIGHT_FLAT    = 0
LIGHT_GOURAUD = 1
LIGHT_PHONG   = 2


# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.showAxis = False             #Control for activate red line
        self.lightingModel = LIGHT_PHONG
        self.Camera2 = True
        self.CameraEnd = False
        self.ITR = 0
        self.ITR2 = 0
        self.theta = 0
        self.move = False



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
                newColor = vec3(1,0,0);
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

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

    elif key == glfw.KEY_C:
        controller.Camera2 = not controller.Camera2

    elif key == glfw.KEY_UP:
        controller.move = True
    
    elif key == glfw.KEY_R:         #R for reestart
        controller.move = False
    


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
        gpuShape.fillBuffers(shape.vertices, shape.indices, GL_DYNAMIC_DRAW)
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
    TranslatedDefBoat.transform = tr.translate(5,5,10)
    TranslatedDefBoat.childs += [DefBoat]

    return TranslatedDefBoat


def createEnd():
    # Creating the end by a shape that is a cube with normals and textures
    # Defining locations,texture coordinates and normals for each vertex of the shape  
    vertices = [
    #   positions            tex coords   normals
    # Z+
        -0.5, -0.5,  0.5,    0, 1,        0,0,1,
         0.5, -0.5,  0.5,    1, 1,        0,0,1,
         0.5,  0.5,  0.5,    1, 0,        0,0,1,
        -0.5,  0.5,  0.5,    0, 0,        0,0,1,   
    # Z-          
        -0.5, -0.5, -0.5,    0, 1,        0,0,-1,
         0.5, -0.5, -0.5,    1, 1,        0,0,-1,
         0.5,  0.5, -0.5,    1, 0,        0,0,-1,
        -0.5,  0.5, -0.5,    0, 0,        0,0,-1,
       
    # X+          
         0.5, -0.5, -0.5,    0, 1,        1,0,0,
         0.5,  0.5, -0.5,    1, 1,        1,0,0,
         0.5,  0.5,  0.5,    1, 0,        1,0,0,
         0.5, -0.5,  0.5,    0, 0,        1,0,0,   
    # X-          
        -0.5, -0.5, -0.5,    0, 1,        -1,0,0,
        -0.5,  0.5, -0.5,    1, 1,        -1,0,0,
        -0.5,  0.5,  0.5,    1, 0,        -1,0,0,
        -0.5, -0.5,  0.5,    0, 0,        -1,0,0,   
    # Y+          
        -0.5,  0.5, -0.5,    0, 1,        0,1,0,
         0.5,  0.5, -0.5,    1, 1,        0,1,0,
         0.5,  0.5,  0.5,    1, 0,        0,1,0,
        -0.5,  0.5,  0.5,    0, 0,        0,1,0,   
    # Y-          
        -0.5, -0.5, -0.5,    0, 1,        0,-1,0,
         0.5, -0.5, -0.5,    1, 1,        0,-1,0,
         0.5, -0.5,  0.5,    1, 0,        0,-1,0,
        -0.5, -0.5,  0.5,    0, 0,        0,-1,0
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



################################################################
################################################################
################################################################
#Curves before tobogan
Lista = [np.array([[0, 0, 10]]).T,       #P0
        np.array([[5, 5, 10]]).T,          #P1
        np.array([[10, 5, 9]]).T,          #P2
        np.array([[15, 8, 8]]).T,         #P3
        np.array([[20, 25, 7]]).T,          #P4
        np.array([[30, 30, 6]]).T,           #P5
        np.array([[40, 48, 5]]).T,           #P6
        np.array([[55,52,4]]).T,           #P7
        np.array([[60,55,3]]).T,            #P8
        np.array([[65,68,2]]).T,             #P9
        np.array([[75,70,1]]).T,            #P10
        np.array([[80,80,0]]).T,             #P11
        np.array([[90, 90, 0]]).T]         #P12


# This function generates a spline of catmul roll that defines the movement and also is a reference for the tobogan
def createLine(N,Lista):
    


    CRcurve = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[0], N)    #C1
    CRcurve2 = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[1], N)   #C2
    CRcurve3 = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[2], N)   #C3
    CRcurve4 = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[3], N)   #C4
    CRcurve5 = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[4], N)   #C5
    CRcurve6 = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[5], N)   #C6
    CRcurve7 = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[6], N)   #C7
    CRcurve8 = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[7], N)   #C8
    CRcurve9 = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[8], N)   #C9
    CRcurve10 = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[9], N)  #C10

    ver = np.concatenate((CRcurve[0:-1,:],
                          CRcurve2[0:-1,:],
                          CRcurve3[0:-1,:],
                          CRcurve4[0:-1,:],
                          CRcurve5[0:-1,:],
                          CRcurve6[0:-1,:],
                          CRcurve7[0:-1,:],
                          CRcurve8[0:-1,:],
                          CRcurve9[0:-1,:],
                          CRcurve10), axis=0) #numpy array
    

    vertices = ver.reshape(1,np.size(ver)).tolist()[0] #list
    indices = [i for i in range(10*N-9)]


    return bs.Shape(vertices, indices), ver

curve = createLine(100,Lista)[0]                                            
#List of List of List, but vertex has 1 less, it has the posicions.
vertex = createLine(100,Lista)[1]                            #HERE you can change the velocity of the boat
vertex2 = createLine(30,Lista)[1]                            #HERE you can change the number of points of the tobogan, 30 is good                                     
# So vertex has the positions of our curve



# This function generates a normal vector 
def perpendicular_vector(v):
    #A vector is perpendicular to other vector when dot product equal 0.

    if v[0] == v[1] == v[2] == 0:
        raise ValueError('zero vector')
    if v[0] == 0:
        return np.array([1,0,0])
    if v[1] == 0:
        return np.array([0,1,0])
    if v[2] == 0:
        return np.array([0,0,1])
    
    # Solvin the equation of a dot product, using arbitrarily some parameters as 1.
    return np.array([1,1,-1.0*(v[0]+v[1])/v[2]])



#This function defines the tangent planes of vertex
def TangentPlanesVertex(vertex):

    aux = []
    TangentPlanes = []
    for i in range(np.size(vertex,0)-1):
        NormalVector = vertex[i+1,:] - vertex[i,:] / np.linalg.norm(vertex[i+1,:] - vertex[i,:])

        #Perpendicular Plane
        PerpendicularVector = perpendicular_vector(NormalVector) / np.linalg.norm(perpendicular_vector(NormalVector))
        PerpendicularVector2 = np.cross(NormalVector,PerpendicularVector) / np.linalg.norm(np.cross(NormalVector,PerpendicularVector))
        aux.append(PerpendicularVector) 
        aux.append(PerpendicularVector2) 
        TangentPlanes.append(aux)
    TangentPlanes = np.array(TangentPlanes)
    return TangentPlanes

TangentPlanesVertex = TangentPlanesVertex(vertex)



# This function generates all the points for the tobogan
def createLines(vertex):
    R = 5                                               # Radio of the tobogan
    CircleNodes = 16                                    # Number of vertices of the tobogan
    phi = np.linspace(0,2*np.pi,CircleNodes)[0:]        # CKECK CHANGE

    Puntos = np.zeros((np.size(vertex,0)-1,len(phi),3))

    for i in range(np.size(vertex,0)-1): #circles
        NormalVector = vertex[i+1,:] - vertex[i,:] / np.linalg.norm(vertex[i+1,:] - vertex[i,:])

        #Perpendicular Plane
        PerpendicularVector = perpendicular_vector(NormalVector) / np.linalg.norm(perpendicular_vector(NormalVector))
        PerpendicularVector2 = np.cross(NormalVector,PerpendicularVector) / np.linalg.norm(np.cross(NormalVector,PerpendicularVector))

        for j in range(len(phi)): #angles
            Puntos[i,j,:] = (R*np.cos(phi[j]) * PerpendicularVector + R*np.sin(phi[j]) * PerpendicularVector2) + vertex[i,:]

    return Puntos
# puntos works as a list, each element of it is a list with a group of np.arrays.
#each one of this in lists represents one circle


LINES = createLines(vertex2)




# Function that creates the tobogan
def createTobogan(LINES, vertex2):
    # Defining locations and texture coordinates for each vertex of the shape

    #vertices = LINES.reshape(1,np.size(LINES)).tolist()[0]
 
    indices = []
    vertices = []
    VerCirc = len(LINES[0])               # Cantidad de vertices circulo
    counter = 0                           # keeps 
    for i in range(len(LINES)-1):         # i iterates changing circles
        Circle = LINES[i]
        Circle2 = LINES[i+1]
        for j in range(VerCirc):
            vertices += [Circle[j][0], Circle[j][1], Circle[j][2], 
                         j%2,i%2,
                         (vertex2[i]- Circle[j])[0],(vertex2[i]- Circle[j])[1],(vertex2[i]- Circle[j])[2]]
            if i == len(LINES)-2:         # To have the end of the tobogan
                vertices += [Circle2[j][0], Circle2[j][1], Circle2[j][2], 
                         j%2,i%2,
                         (vertex2[i]- Circle2[j])[0],(vertex2[i]- Circle2[j])[1],(vertex2[i]- Circle2[j])[2]]
            if i <= len(LINES)-4:         # This makes the end looks grate
                indices += [j + counter, j + VerCirc + counter, j + 1 + counter]
                indices += [j + VerCirc + counter, j + 1 + counter, j + VerCirc + 1 + counter]

        counter += VerCirc

    return bs.Shape(vertices, indices)

Tobogan = createTobogan(LINES, vertex2)



# This function is used for creating the piece of water, reutiliza different functions mentioned before
def createSectionWater(vertex):
    # It uses crateLines, but it changes it to get less angles.
    def createLines2(vertex):
        R = 5                                               # Radio of the tobogan
        CircleNodes = 3                                     # Number of vertices of the tobogan
        phi = np.linspace(-1*np.pi/6,1*np.pi/6,CircleNodes)[0:]        # CKECK CHANGE

        Puntos = np.zeros((np.size(vertex,0)-1,len(phi),3))

        for i in range(np.size(vertex,0)-1): #circles
            NormalVector = vertex[i+1,:] - vertex[i,:] / np.linalg.norm(vertex[i+1,:] - vertex[i,:])

            #Perpendicular Plane
            PerpendicularVector = perpendicular_vector(NormalVector) / np.linalg.norm(perpendicular_vector(NormalVector))
            PerpendicularVector2 = np.cross(NormalVector,PerpendicularVector) / np.linalg.norm(np.cross(NormalVector,PerpendicularVector))

            for j in range(len(phi)): #angles
                Puntos[i,j,:] = (R*np.cos(phi[j]) * PerpendicularVector + R*np.sin(phi[j]) * PerpendicularVector2) + vertex[i,:]

        return Puntos



    LINES2 = createLines2(vertex)
 
    indices = []
    vertices = []
    VerCirc = len(LINES2[0])               # Cantidad de vertices circulo
    counter = 0                            # keeps 
    for i in range(len(LINES2)-1):         # i iterates changing circles
        Circle = LINES2[i]
        Circle2 = LINES2[i+1]
        for j in range(VerCirc):
            vertices += [Circle[j][0], Circle[j][1], Circle[j][2], 
                         j%2,i%2,
                         (vertex2[i]- Circle[j])[0],(vertex2[i]- Circle[j])[1],(vertex2[i]- Circle[j])[2]]
            if i == len(LINES2)-2:         # To have the end of the tobogan
                vertices += [Circle2[j][0], Circle2[j][1], Circle2[j][2], 
                         j%2,i%2,
                         (vertex2[i]- Circle2[j])[0],(vertex2[i]- Circle2[j])[1],(vertex2[i]- Circle2[j])[2]]
            if i <= len(LINES2)-4:         # This makes the end looks grate
                indices += [j + counter, j + VerCirc + counter, j + 1 + counter]
                indices += [j + VerCirc + counter, j + 1 + counter, j + VerCirc + 1 + counter]

        counter += VerCirc
    return bs.Shape(vertices, indices)

WaterSection = createSectionWater(vertex2)








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

    ###########################################################################
    ###########################################################################
    ###########################################################################
    # Pipelines
    # Different shader programs for different lighting strategies
    textureFlatPipeline = ls.SimpleTextureFlatShaderProgram()
    textureGouraudPipeline = ls.SimpleTextureGouraudShaderProgram()
    texturePhongPipeline = ls.SimpleTexturePhongShaderProgram()
    textureMultiplePhongPipeline = ls.MultipleTexturePhongShaderProgram()
    displacementeMultiplePipeline = dv.Displacement3D()               

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
    def createGPUShape(pipeline, shape, draw = GL_STATIC_DRAW):
        gpuShape = es.GPUShape().initBuffers()
        pipeline.setupVAO(gpuShape)
        gpuShape.fillBuffers(shape.vertices, shape.indices, draw)
        return gpuShape

    # Creating shapes on GPU memory
    gpuAxis = createGPUShape(colorPipeline, bs.createAxis(4))
    gpuCurve = createGPUShape(curvePipeline, curve)
    lightingPipeline = textureMultiplePhongPipeline
    #Tobogan to gpu
    gpuTobogan = createGPUShape(lightingPipeline, Tobogan,GL_DYNAMIC_DRAW)
    gpuTobogan.texture = es.textureSimpleSetup(
        getAssetPath("madera.jpg"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)

    #WaterSection to gpu
    gpuWaterSection = createGPUShape(displacementeMultiplePipeline, WaterSection)
    gpuWaterSection.texture = es.textureSimpleSetup(
        getAssetPath("Textura2.PNG"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)
    gpuWaterSection.texture2 = es.textureSimpleSetup(
        getAssetPath("Textura1.PNG"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)

    #Endo to gpu
    gpuFinal = createGPUShape(lightingPipeline, createEnd())
    gpuFinal.texture = es.textureSimpleSetup(
        getAssetPath("final.jpg"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)
    


    # Creating Scenegraph of a CompleteBoat
    CompleteBoat = CompleteBoat()

    t0 = glfw.get_time()




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

        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
            controller.theta -= 2*np.pi * 0.005/2
        if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
            controller.theta += 2*np.pi * 0.005/2
        

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        theta = 6*t1
        dt = t1 - t0
        t0 = t1

        #Rotate Flag from the boat
        rotatedflag = sg.findNode(CompleteBoat, "RotatedFlag")
        rotatedflag.transform = tr.rotationZ(t1)

        #CKECK THIS !!!!!---------------------------------------------------------------------
        #Translate Boat
        translatedboat = sg.findNode(CompleteBoat, "TranslatedDefBoat")


        #Position of the boat
        if controller.move:
            if controller.ITR <= len(vertex)-2:
                R = 5
                curvePos = vertex[controller.ITR][0], vertex[controller.ITR][1], vertex[controller.ITR][2]
                Plane = TangentPlanesVertex[controller.ITR]
                traslacion = (R*np.cos(controller.theta) * Plane[0] + R*np.sin(controller.theta) * Plane[1]) + vertex[controller.ITR,:]
                translatedboat.transform = tr.translate(traslacion[0], traslacion[1], traslacion[2])
                #translatedboat.transform = tr.translate(curvePos[0],curvePos[1],curvePos[2])
                controller.ITR +=1
            
            elif controller.ITR > len(vertex)-2:
                controller.CameraEnd = True
            if controller.ITR > (len(vertex)-1)/10:
                controller.ITR2 = controller.ITR -100   #HERE you can change the delay of the camera
        
        # Re-start or lose against the obstacle
        if not controller.move:
            controller.ITR = 0
            controller.ITR2 = 0
            controller.theta = 0
            controller.CameraEnd = False
            translatedboat.transform = tr.translate(5, 5, 10)
        

        # Camera at the end
        if controller.CameraEnd:
            projection = tr.ortho(-1, 1, -1, 1, 1, 100)
            viewPos = [-1,0,0]     #If you want to see better 
            view = tr.lookAt(
                viewPos,
                np.array([0,0,0]),
                np.array([0,0,1])
            )
            gpuFinal.texture = es.textureSimpleSetup(
                getAssetPath("final.jpg"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)
            

        # Cameras while moving
        else:

            # First case of Camera
            if not controller.Camera2:

                projection = tr.perspective(40, float(width)/float(height), 0.1, 100)
                viewPos = [50,0,0]     #If you want to see better 
                view = tr.lookAt(
                    viewPos,
                    np.array([translatedboat.transform[0][3], translatedboat.transform[1][3], translatedboat.transform[2][3]]),
                    np.array([0,0,1])
                )

            
            # Second case of Camera
            if controller.Camera2:
                #Initial case
                if controller. ITR == 0:
                    projection = tr.perspective(40, float(width)/float(height), 0.1, 100)
                    viewPos = np.array([3, 3, 12])
                    view = tr.lookAt(
                        viewPos,
                        np.array([6,6,10]),
                        np.array([0,0,1])
                    )
                #Oficial camera
                else:
                    projection = tr.perspective(40, float(width)/float(height), 0.1, 100)
                    viewPos = np.array([vertex[controller.ITR2][0], vertex[controller.ITR2][1], vertex[controller.ITR2][2]+1])
                    view = tr.lookAt(
                        viewPos,
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
            # glUseProgram(curvePipeline.shaderProgram)
            # glUniformMatrix4fv(glGetUniformLocation(curvePipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
            # glUniformMatrix4fv(glGetUniformLocation(curvePipeline.shaderProgram, "view"), 1, GL_TRUE, view)
            # glUniformMatrix4fv(glGetUniformLocation(curvePipeline.shaderProgram, "model"), 1, GL_TRUE, tr.uniformScale(1.0))
            # colorPipeline.drawCall(gpuCurve, GL_LINE_STRIP)

            # glUseProgram(curvePipeline.shaderProgram)
            # glUniformMatrix4fv(glGetUniformLocation(curvePipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
            # glUniformMatrix4fv(glGetUniformLocation(curvePipeline.shaderProgram, "view"), 1, GL_TRUE, view)
            # glUniformMatrix4fv(glGetUniformLocation(curvePipeline.shaderProgram, "model"), 1, GL_TRUE, tr.uniformScale(1.0))
            # colorPipeline.drawCall(gpuTobogan)

            glUseProgram(colorPipeline.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(colorPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
            glUniformMatrix4fv(glGetUniformLocation(colorPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
            glUniformMatrix4fv(glGetUniformLocation(colorPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.translate(80,80,0))
            colorPipeline.drawCall(gpuAxis, GL_LINES)

        #Using lightin
        lightingPipeline = textureMultiplePhongPipeline


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

        # Drawing
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        lightingPipeline.drawCall(gpuTobogan)

        # Drawing
        if not controller.CameraEnd:
            glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.matmul([
                    tr.translate(83, 83, 0),
                    tr.rotationZ(np.pi/3), 
                    tr.uniformScale(15)]))
            lightingPipeline.drawCall(gpuFinal)
        if controller.CameraEnd:
            glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.matmul([
                    tr.translate(0, 0, 0), 
                    tr.uniformScale(2)]))
            lightingPipeline.drawCall(gpuFinal)

        # Drawing
        glUseProgram(displacementeMultiplePipeline.shaderProgram)

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

        glUniformMatrix4fv(glGetUniformLocation(displacementeMultiplePipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(displacementeMultiplePipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(displacementeMultiplePipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())

        # Binding samplers to both texture units
        glUniform1i(glGetUniformLocation(displacementeMultiplePipeline.shaderProgram, "WaterText"), 0)
        glUniform1i(glGetUniformLocation(displacementeMultiplePipeline.shaderProgram, "DisplaceText"), 1)

        # Sending the mouse vertical location to our shader
        glUniform1f(glGetUniformLocation(displacementeMultiplePipeline.shaderProgram, "time"), theta)
        glUniform1f(glGetUniformLocation(displacementeMultiplePipeline.shaderProgram, "maximo"), 0.6)


        displacementeMultiplePipeline.drawCall(gpuWaterSection)

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuAxis.clear()

    glfw.terminate()
