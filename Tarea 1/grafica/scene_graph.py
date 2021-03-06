# coding=utf-8
"""A simple scene graph class and functionality"""

from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import grafica.transformations as tr
import grafica.gpu_shape as gs
import glfw

__author__ = "Daniel Calderon"
__license__ = "MIT"


class SceneGraphNode:
    """
    A simple class to handle a scene graph
    Each node represents a group of objects
    Each leaf represents a basic figure (GPUShape)
    To identify each node properly, it MUST have a unique name
    """
    def __init__(self, name):
        self.name = name
        self.transform = tr.identity()
        self.childs = []
        self.click = False
        self.click2 = False
        self.valor = 0
        self.lineaIzquierda = False
        self.lineaDerecha = False
        self.PadreIzquierdo = False
        self.PadreDerecho = False

    def clear(self):
        """Freeing GPU memory"""

        for child in self.childs:
            child.clear()

            

    
def findNode(node, name):

    # The name was not found in this path
    if isinstance(node, gs.GPUShape):
        return None

    # This is the requested node
    if node.name == name:
        return node
    
    # All childs are checked for the requested name
    for child in node.childs:
        foundNode = findNode(child, name)
        if foundNode != None:
            return foundNode

    # No child of this node had the requested name
    return None


def findTransform(node, name, parentTransform=tr.identity()):

    # The name was not found in this path
    if isinstance(node, gs.GPUShape):
        return None

    newTransform = np.matmul(parentTransform, node.transform)

    # This is the requested node
    if node.name == name:
        return newTransform
    
    # All childs are checked for the requested name
    for child in node.childs:
        foundTransform = findTransform(child, name, newTransform)
        if isinstance(foundTransform, (np.ndarray, np.generic) ):
            return foundTransform

    # No child of this node had the requested name
    return None


def findPosition(node, name, parentTransform=tr.identity()):
    foundTransform = findTransform(node, name, parentTransform)

    if isinstance(foundTransform, (np.ndarray, np.generic) ):
        zero = np.array([[0,0,0,1]], dtype=np.float32).T
        foundPosition = np.matmul(foundTransform, zero)
        return foundPosition

    return None


def drawSceneGraphNode(node, pipeline, transformName, parentTransform=tr.identity()):
    assert(isinstance(node, SceneGraphNode))

    # Composing the transformations through this path
    newTransform = np.matmul(parentTransform, node.transform)

    # If the child node is a leaf, it should be a GPUShape.
    # Hence, it can be drawn with drawCall
    if len(node.childs) == 1 and isinstance(node.childs[0], gs.GPUShape):
        leaf = node.childs[0]
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, transformName), 1, GL_TRUE, newTransform)
        pipeline.drawCall(leaf)

    # If the child node is not a leaf, it MUST be a SceneGraphNode,
    # so this draw function is called recursively
    else:
        for child in node.childs:
            drawSceneGraphNode(child, pipeline, transformName, newTransform)


def drawSceneGraphNodeTEXT(node, pipeline, Color, transformName, parentTransform=tr.identity()):
    # Composing the transformations through this path
    newTransform = np.matmul(parentTransform, node.transform)

    if len(node.childs) == 1 and isinstance(node.childs[0], gs.GPUShape):
        leaf = node.childs[0]

        glUniform4f(glGetUniformLocation(pipeline.shaderProgram, "fontColor"), 0,0,0,1)
        glUniform4f(glGetUniformLocation(pipeline.shaderProgram, "backColor"), Color[0],Color[1],Color[2],1)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, transformName), 1, GL_TRUE, newTransform)
        pipeline.drawCall(leaf)

    else:
        for child in node.childs:
            drawSceneGraphNodeTEXT(child, pipeline, Color, transformName,newTransform)


#Orden pipeline 1 = Simple, pipeline 2 = Texto pipeline 3 = Texto color 2
#shader.1 Simple shader.2 Text Color shader.3 Text Color2 
def drawSceneGraphNodeDefinitivo(node, pipeline1, pipeline2, pipeline3, Color,Color2,Color3, transformName, parentTransform = tr.identity()):
    newTransform = np.matmul(parentTransform, node.transform)

    if len(node.childs) == 1 and isinstance(node.childs[0], gs.GPUShape):
        leaf = node.childs[0]
        if leaf.shader == 1:
            glUseProgram(pipeline1.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(pipeline1.shaderProgram, transformName), 1, GL_TRUE, newTransform)
            pipeline1.drawCall(leaf)

        elif leaf.shader == 2:
            glUseProgram(pipeline2.shaderProgram)
            glUniform4f(glGetUniformLocation(pipeline2.shaderProgram, "fontColor"), 0,0,0,1)
            glUniform4f(glGetUniformLocation(pipeline2.shaderProgram, "backColor"), Color[0],Color[1],Color[2],1)
            glUniformMatrix4fv(glGetUniformLocation(pipeline2.shaderProgram, transformName), 1, GL_TRUE, newTransform)
            pipeline2.drawCall(leaf)

        elif leaf.shader == 3:
            glUseProgram(pipeline2.shaderProgram)
            glUniform4f(glGetUniformLocation(pipeline2.shaderProgram, "fontColor"), 0,0,0,1)
            glUniform4f(glGetUniformLocation(pipeline2.shaderProgram, "backColor"), Color2[0],Color2[1],Color2[2],1)
            glUniformMatrix4fv(glGetUniformLocation(pipeline2.shaderProgram, transformName), 1, GL_TRUE, newTransform)
            pipeline2.drawCall(leaf)

        elif leaf.shader == 4:
            glUseProgram(pipeline2.shaderProgram)
            glUniform4f(glGetUniformLocation(pipeline2.shaderProgram, "fontColor"), 0,0,0,1)
            glUniform4f(glGetUniformLocation(pipeline2.shaderProgram, "backColor"), Color3[0],Color3[1],Color3[2],1)
            glUniformMatrix4fv(glGetUniformLocation(pipeline2.shaderProgram, transformName), 1, GL_TRUE, newTransform)
            pipeline2.drawCall(leaf)

        elif leaf.shader == 5:
            glUseProgram(pipeline3.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(pipeline3.shaderProgram, transformName), 1, GL_TRUE, newTransform)
            pipeline3.drawCall(leaf)

        elif leaf.shader == 6:
            theta = glfw.get_time()
            glUseProgram(pipeline1.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(pipeline1.shaderProgram, transformName), 1, GL_TRUE, tr.matmul([newTransform,tr.shearing(0.2*np.cos(theta), 0, 0, 0, 0, 0)]))
            pipeline1.drawCall(leaf)

        elif leaf.shader == 7:
            glUseProgram(pipeline1.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(pipeline1.shaderProgram, transformName), 1, GL_TRUE, newTransform)
            glLineWidth(10)
            pipeline1.drawCall(leaf, GL_LINES)
    else:
        for child in node.childs:
            drawSceneGraphNodeDefinitivo(child, pipeline1, pipeline2,pipeline3, Color,Color2, Color3, transformName, newTransform)