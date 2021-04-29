"""Vicente Hidalgo 20.537.661-5, se tomo de base la p5 del aux, 
por lo que algunos comentarios se conservan"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
from gpu_shape import GPUShape, SIZE_IN_BYTES


#Cambio las teclas para los shaders para demostrar que se como hacerlo, Z de zoom y C de corte

class Controller:
    """
    Clase controlador que guardar las variables a modificar en la funcion on_key
    """
    fillPolygon = True # Variable que indica si se debe dibujar en modo lineas o rellenar los triangulos
    effect1 = False # Variable que guarda el estado del efecto 1 : zoom (activado o desactivado)
    effect2 = False # Variable que guarda el estado del efecto 1 : corte (activado o desactivado)


# we will use the global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):
    """
    Funcion que recibe el input del teclado.
    Si no se detecta una tecla presionada, la funcion retorna
    """
    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

    # Si detecta la tecla [Q] cambia el estado del efecto 1 : zoom
    elif key == glfw.KEY_Z:
        controller.effect1 = not controller.effect1

    # Si detecta la tecla [W] cambia el estado del efecto 2 : corte
    elif key == glfw.KEY_C:
        controller.effect2 = not controller.effect2

    else:
        print('Unknown key')
    
class Shape:
    """
    Clase simple para guardar los vertices e indices
    """
    def __init__(self, vertices, indices):
        self.vertices = vertices
        self.indices = indices

class SimpleShaderProgram:
    """
    Clase para guardar el los shaders compilados
    Contiene los shaders basicos (sin efectos)
    """
    def __init__(self):

        vertex_shader = """
            #version 130

            in vec3 position;
            in vec3 color;

            out vec3 newColor;
            void main()
            {
                gl_Position = vec4(position, 1.0f);
                newColor = color;
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
        """
        Se le "dice" al shader como leer los bytes de la gpuShape asignada
        """

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + rgb color specification => 3*4 + 3*4 = 24 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        color = glGetAttribLocation(self.shaderProgram, "color")
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        """
        Se dibuja la gpuShape
        """
        assert isinstance(gpuShape, GPUShape)

        # Binding the VAO and executing the draw call
        glBindVertexArray(gpuShape.vao)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)


#Shader que hace un zoom al barquito

class ZoomShaderProgram:
    """
    Clase para guardar el los shaders compilados
    Contiene los shaders para hacer zoom a el barco
    """

    def __init__(self):

        # Modificacion de Vertex shader
        vertex_shader = """
            #version 130

            in vec3 position;
            in vec3 color;

            out vec3 newColor;
            void main()
            {
                vec3 newPos = vec3((position[0]/0.7)+0.25, position[1]/0.7, position[2]/0.1);
                gl_Position = vec4(newPos, 1.0f);
                newColor = color;
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
        """
        Se le "dice" al shader como leer los bytes de la gpuShape asignada
        """

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + rgb color specification => 3*4 + 3*4 = 24 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        color = glGetAttribLocation(self.shaderProgram, "color")
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        """
        Se dibuja la gpuShape
        """
        assert isinstance(gpuShape, GPUShape)

        # Binding the VAO and executing the draw call
        glBindVertexArray(gpuShape.vao)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)

class CorteShaderProgram:
    """
    Clase para guardar el los shaders compilados
    Contiene los shaders para cortar el barquito
    """
    def __init__(self):
        # Vertex shader no de modifica
        vertex_shader = """
            #version 130

            in vec3 position;
            in vec3 color;

            out vec3 newColor;
            void main()
            {
                gl_Position = vec4(position, 1.0f);
                newColor = color;
            }
            """
         # Se modifica el fragment shader para identificar la parte del corte deseada y cambiarla por mar
        fragment_shader = """
            #version 130
            in vec3 newColor;

            out vec4 outColor;
            void main()
            {
                // Se crea una nuevo vector para contener el color final
                vec3 finalColor = newColor;

                if (newColor.r == 0.4 || newColor.g ==0.32 || newColor.b == 0.2)
                {
                    finalColor = vec3(0.0, 0.41, 0.58);
                }

                outColor = vec4(finalColor, 1.0f);
            }
            """

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):
        """
        Se le "dice" al shader como leer los bytes de la gpuShape asignada
        """
        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + rgb color specification => 3*4 + 3*4 = 24 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        color = glGetAttribLocation(self.shaderProgram, "color")
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        """
        Se dibuja la gpuShape
        """
        assert isinstance(gpuShape, GPUShape)

        # Binding the VAO and executing the draw call
        glBindVertexArray(gpuShape.vao)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)

def create_noche(y0, y1):
    """
    Funcion para crear noche

    Parameters:
    y_0 (float): altura inferior donde empezara el rectangulo de noche
    y_1 (float): altura superior donde termina el rectangulo de noche
    """
    # Defining the location and colors of each vertex  of the shape 
    vertices = [
    #   positions        colors
        -1.0, y0, 0.0,  0.15, 0.16, 0.5,
         1.0, y0, 0.0,  0.15, 0.16, 0.5,
         1.0, y1, 0.0,  0.15, 0.16, 0.1,
        -1.0, y1, 0.0,  0.15, 0.16, 0.1]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [0, 1, 2,
                2, 3, 0]

    return Shape(vertices, indices)

def create_arena(y0, y1):
    """
    Funcion para crear arena

    Parameters:
    y_0 (float): altura inferior donde empezara el rectangulo de arena
    y_1 (float): altura superior donde termina el rectangulo de arena
    """
    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #   positions        colors
        -1.0, y0, 0.0,  0.4, 0.32, 0.2,
         1.0, y0, 0.0,  0.4, 0.32, 0.2,
         1.0, y1, 0.0,  0.77, 0.64, 0.39,
        -1.0, y1, 0.0,  0.77, 0.64, 0.39]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [0, 1, 2,
                2, 3, 0]

    return Shape(vertices, indices)

def create_barco(x0, y0,largo_1,largo_2,alto):
    """
    Funcion para crear una figura que represente una isla

    Parameters:
    x_0 (float): posicion horizontal/coord x donde se ubica la punta superior izquierda del barco
    y_0 (float): posicion vertical/coord y donde se ubica la punta superior izquierda del barco
    largo_1(float): distancia de un punto externo de un triangulo que forma un trapecio.
    largo_2(floar): distancia de un punto interno de un rectangulo que forma un trapecio.
    """
    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #   positions                           colors
         x0,            y0, 0.0,                   0.7,  0.25, 0.2,  #Punto uno linea superior
         x0 + largo_1,  y0, 0.0,                   0.7,  0.25, 0.2,  #Punto dos linea superior
         x0 + largo_1 + largo_2, y0, 0.0,          0.5,  0.25, 0.0,  #Punto tres linea superior
         x0 + (largo_1)*2 + largo_2, y0, 0.0,      0.5,  0.25, 0.0,  #Punto cuatro linea superior

         x0 + largo_1,  y0 - alto, 0.0,            0.7,  0.25, 0.2,  #Punto uno linea inferior
         x0 + largo_1 + largo_2, y0 - alto, 0.0,   0.5,  0.25, 0.0]  #Punto dos linea inferior

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [0, 1, 4,
                4, 1, 2,
                2, 4, 5,
                5, 3, 2]

    return Shape(vertices, indices)

def create_banderita(x0, y0, delta, altura, altura_2, derecha):
    """
    Funcion para crear una banderita

    Parameters:
    x_0 (float): posicion horizontal/coord x donde se ubica el inicio de la bandera
    y_0 (float): posicion vertical/coord y donde se ubica el inicio de la bandera
    delta(float): pequeño desfase para generar el palo
    altura(float): altura del palo
    altura_2(float): altura de la bandera
    derecha(float): distancia en x desde el palo hasta el borde externo de la bandera
    """

    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #   positions                         colors
         x0, y0, 0.0,                                         0.0, 0.0, 0.0,    #Palo
         x0 + delta, y0, 0.0,                                 0.0, 0.0, 0.0,    #Palo
         x0 + delta, y0 + altura, 0.0,                        0.0, 0.0, 0.0,    #Palo
         x0, y0 + altura,0.0,                                 0.0, 0.0, 0.0,    #Palo inicio bandera
         x0, y0 + altura + altura_2, 0.0,                     0.0, 0.8, 0.0,    #Bandera punto alto
         x0 + derecha, y0 + altura + (altura_2)*0.5, 0.0,     0.0, 0.4, 0.0]    #Bandera punto derecho

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [0, 1, 2,
                2, 3, 0,
                3, 4, 5]

    return Shape(vertices, indices)

if __name__ == "__main__":
    """
    Funcion o bloque que se ejecuta al correr el codigo
    """

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    # Dimensiones de la ventana de la aplicacion
    width = 800
    height = 800

    # Se crea la ventana con el titulo asignado
    window = glfw.create_window(width, height, "Ejercicio 2", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)
    
    # Creamos las instancias de los ShaderProgram, que compila los shaders creados
    simplePipeline = SimpleShaderProgram() # Shaders normales
    zoomPipeline = ZoomShaderProgram() # Shaders para efecto zoom
    cortePipeline = CorteShaderProgram() #Shaders para efecto corte

    """
    Se crea cada figura en la memoria de la GPU.
    Es importante recordar que se debe hacer setupVAO a cada shaderProgram con cada figura 
    que desea dibujar
    """

    # 1- Creamos la Figura de noche en la GPU
    noche_shape = create_noche(y0=0.1, y1=1.0) # Creamos los vertices e indices (guardandolos en un objeto shape)
    gpu_noche = GPUShape().initBuffers() # Se le pide memoria a la GPU para guardar la figura
    simplePipeline.setupVAO(gpu_noche) # Se le dice al ShaderProgram NORMAL como leer esta parte de la memoria 
    zoomPipeline.setupVAO(gpu_noche) # Se le dice al ShaderProgram del EFECTO 1 (zoom) como leer esta parte de la memoria 
    cortePipeline.setupVAO(gpu_noche) # Se le dice al ShaderProgram del EFECTO 2 (corte) como leer esta parte de la memoria 
    gpu_noche.fillBuffers(noche_shape.vertices, noche_shape.indices, GL_STATIC_DRAW) # Llenamos esta memoria de la GPU con los vertices e indices

    # 2- Creamos la Figura de arena en la GPU
    arena_shape = create_arena(y0=-1.0, y1=-0.5) # Creamos los vertices e indices (guardandolos en un objeto shape)
    gpu_arena = GPUShape().initBuffers() # Se le pide memoria a la GPU para guardar la figura
    simplePipeline.setupVAO(gpu_arena) # Se le dice al ShaderProgram NORMAL como leer esta parte de la memoria 
    zoomPipeline.setupVAO(gpu_arena) # Se le dice al ShaderProgram del EFECTO 1 (zoom) como leer esta parte de la memoria 
    cortePipeline.setupVAO(gpu_arena) # Se le dice al ShaderProgram del EFECTO 2 (corte) como leer esta parte de la memoria 
    gpu_arena.fillBuffers(arena_shape.vertices, arena_shape.indices, GL_STATIC_DRAW) # Llenamos esta memoria de la GPU con los vertices e indices

     # 3- Creamos la Figura del barco en la GPU
    barco_shape = create_barco(x0=-0.8, y0=0.0, largo_1 = 0.2, largo_2= 0.5, alto = 0.4) # Creamos los vertices e indices (guardandolos en un objeto shape)
    gpu_barco = GPUShape().initBuffers() # Se le pide memoria a la GPU para guardar la figura
    simplePipeline.setupVAO(gpu_barco) # Se le dice al ShaderProgram NORMAL como leer esta parte de la memoria 
    zoomPipeline.setupVAO(gpu_barco) # Se le dice al ShaderProgram del EFECTO 1 (zoom) como leer esta parte de la memoria 
    cortePipeline.setupVAO(gpu_barco) # Se le dice al ShaderProgram del EFECTO 2 (corte) como leer esta parte de la memoria 
    gpu_barco.fillBuffers(barco_shape.vertices, barco_shape.indices, GL_STATIC_DRAW) # Llenamos esta memoria de la GPU con los vertices e indices

    # 4- Creamos la Figura del volcan en la GPU 
    banderita_shape = create_banderita(x0=-0.1, y0=0, delta = 0.01, altura = 0.4, altura_2= 0.3, derecha=0.3) # Creamos los vertices e indices (guardandolos en un objeto shape)
    gpu_banderita = GPUShape().initBuffers() # Se le pide memoria a la GPU para guardar la figura
    simplePipeline.setupVAO(gpu_banderita) # Se le dice al ShaderProgram NORMAL como leer esta parte de la memoria 
    zoomPipeline.setupVAO(gpu_banderita) # Se le dice al ShaderProgram del EFECTO 1 (zoom) como leer esta parte de la memoria 
    cortePipeline.setupVAO(gpu_banderita) # Se le dice al ShaderProgram del EFECTO 2 (corte) como leer esta parte de la memoria 
    gpu_banderita.fillBuffers(banderita_shape.vertices, banderita_shape.indices, GL_STATIC_DRAW) # Llenamos esta memoria de la GPU con los vertices e indices


    # Color de fondo de la visualizacion
    glClearColor(0.0, 0.41, 0.58, 1.0)   #Cambiado a color azul de mar

    # Loop principal que muestra las figuras
    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        """
        Si esta el efecto 1 activado (se activa o desactiva con la tecla [Z]
        Se usa el shaderProgram del efecto 1: verde
        """
        if (controller.effect1):
            # Se le dice a OpenGL que use el shaderProgram del efecto 1: Zoom
            glUseProgram(zoomPipeline.shaderProgram)
            zoomPipeline.drawCall(gpu_noche) # Se dibuja la noche
            zoomPipeline.drawCall(gpu_arena) # Se dibuja la arena
            zoomPipeline.drawCall(gpu_barco) # Se dibuja la barco
            zoomPipeline.drawCall(gpu_banderita) # Se dibuja el bandera
        # Si esta el efecto 2 activado (se activa o desactiva con la tecla [C]
        # Se usa el shaderProgram del efecto 2: atardecer
        elif (controller.effect2):
            # Se le dice a OpenGL que use el shaderProgram del efecto 2: atardecer
            glUseProgram(cortePipeline.shaderProgram)
            cortePipeline.drawCall(gpu_noche) # Se dibuja la noche
            cortePipeline.drawCall(gpu_arena) # Se dibuja el arena
            cortePipeline.drawCall(gpu_barco) # Se dibuja la barco
            cortePipeline.drawCall(gpu_banderita) # Se dibuja el bandera
        # Si no hay un efecto activado
        # Se usa el shaderProgram normal
        else:
            # Se le dice a OpenGL que use el shaderProgram normal
            glUseProgram(simplePipeline.shaderProgram)
            simplePipeline.drawCall(gpu_noche) # Se dibuja la noche
            simplePipeline.drawCall(gpu_arena) # Se dibuja el arenao
            simplePipeline.drawCall(gpu_barco) # Se dibuja la barco
            simplePipeline.drawCall(gpu_banderita) # Se dibuja el bandera

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpu_arena.clear()
    gpu_arena.clear()
    gpu_barco.clear()
    gpu_banderita.clear()

    glfw.terminate()