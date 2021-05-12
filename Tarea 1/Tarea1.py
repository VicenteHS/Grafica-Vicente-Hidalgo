import csv
import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.transformations as tr
import grafica.scene_graph as sg

########################################################################
# Obtener lista con los valores puestos en el csv

with open('input.csv','r') as file:
    file = csv.reader(file)

    for line in file:
        Numeros = line

print(Numeros)

########################################################################
# Controlador

SIZE_IN_BYTES = 4

class Controller:
    def __init__(self):
        self.leftClickOn = False
        self.mousePos = (0.0, 0.0)

        self.fillPolygon = True
    

controller = Controller()

def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

    else:
        print('Unknown key')

####################################################################
# Definicion de mouse

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
            print("por definir")

        if (button == glfw.MOUSE_BUTTON_2):
            print(glfw.get_cursor_pos(window))

    elif (action ==glfw.RELEASE):
        if (button == glfw.MOUSE_BUTTON_1):
            controller.leftClickOn = False
####################################################################
#Creacion de figuras
def createNodos(pipeline):

    # Creacion figura gpu de circulo
    shapeCirculo = bs.createCircleRGB(30,0.7,0.4,0.2)
    gpuCirculo = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuCirculo)
    gpuCirculo.fillBuffers(shapeCirculo.vertices, shapeCirculo.indices, GL_STATIC_DRAW)

    # Creacion de un Nodo
    Nodo = sg.SceneGraphNode("Nodo")
    Nodo.transform = tr.uniformScale(0.5)
    Nodo.childs = gpuCirculo

    # Creacion de todos los nodos de Numeros
    Nodos = sg.SceneGraphNode("Nodos")
    
    for i in range(len(Numeros)):

        newNode = sg.SceneGraphNode("Nodo" + str(i))
        newNode.transform = tr.identity
        newNode.childs += [Nodo]

        Nodos.childs += [newNode]

    return Nodos







####################################################################
# Codigo principal

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Handling mouse events", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)


    

    ####################################################################
    # Teclado a glfw
    glfw.set_key_callback(window, on_key)
    # Mouse a glfw.
    glfw.set_cursor_pos_callback(window, cursor_pos_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)

    ####################################################################
    # Eleccion de pipeline
    pipeline = es.SimpleTransformShaderProgram()
    glUseProgram(pipeline.shaderProgram)


    glClearColor(0.3, 0.3, 0.3, 1.0)


    glfw.swap_interval(0)

    Nodos = createNodos(pipeline)

    while not glfw.window_should_close(window):
        glfw.set_window_title(window, "hola")
        glfw.poll_events()


        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen
        glClear(GL_COLOR_BUFFER_BIT)


        sg.drawSceneGraphNode(Nodos, pipeline,"Transform")

        glfw.swap_buffers(window)
    
    #gpuCirculo.clear()

    glfw.terminate()