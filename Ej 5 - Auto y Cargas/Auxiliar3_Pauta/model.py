""" Clases y objetos correspondiente al modelo"""

import glfw
import numpy as np
import grafica.transformations as tr

class Player():
    # Clase que contiene al modelo del player / auro
    def __init__(self, size):
        self.pos = [0,-0.65] # Posicion en el escenario
        self.vel = [1,1] # Velocidad de desplazamiento
        self.model = None # Referencia al grafo de escena asociado
        self.controller = None # Referencia del controlador, para acceder a sus variables
        self.size = size # Escala a aplicar al nodo 
        self.radio = 0.1 # distancia para realiozar los calculos de colision

    def set_model(self, new_model):
        # Se obtiene una referencia a uno nodo
        self.model = new_model

    def set_controller(self, new_controller):
        # Se obtiene la referncia al controller
        self.controller = new_controller

    def update(self, delta):
        # Se actualiza la posicion del auto

        # Si detecta la tecla [D] presionada se mueve hacia la derecha
        if self.controller.is_d_pressed:
            self.pos[0] += self.vel[0] * delta
        # Si detecta la tecla [A] presionada se mueve hacia la izquierda
        if self.controller.is_a_pressed:
            self.pos[0] -= self.vel[0] * delta
        # Si detecta la tecla [W] presionada y no se ha salido de la pista se mueve hacia arriba
        if self.controller.is_w_pressed and self.pos[1] < -0.45:
            self.pos[1] += self.vel[1] * delta
        # Si detecta la tecla [S] presionada y no se ha salido de la pista se mueve hacia abajo
        if self.controller.is_s_pressed and self.pos[1] > -0.8:
            self.pos[1] -= self.vel[1] * delta
        #print(self.pos[0], self.pos[1])

        # Se le aplica la transformacion de traslado segun la posicion actual
        self.model.transform = tr.matmul([tr.translate(self.pos[0], self.pos[1], 0), tr.scale(self.size, self.size, 1)])

    def collision(self, cargas):
        # Funcion para detectar las colisiones con las cargas

        # Se recorren las cargas 
        for carga in cargas:
            # si la distancia a la carga es menor que la suma de los radios ha ocurrido en la colision
            if (self.radio+carga.radio)**2 > ((self.pos[0]- carga.pos[0])**2 + (self.pos[1]-carga.pos[1])**2):
                print("Kiwi chocastes")
                return
        
class Carga():
    # Clase para contener las caracteristicas de un objeto que representa una carga 
    def __init__(self, posx, posy, size):
        self.pos = [posx, posy]
        self.radio = 0.05
        self.size = size
        self.model = None
    
    def set_model(self, new_model):
        self.model = new_model

    def update(self):
        # Se posiciona el nodo referenciado
        self.model.transform = tr.matmul([tr.translate(self.pos[0], self.pos[1], 0), tr.scale(self.size, self.size, 1)])

    
