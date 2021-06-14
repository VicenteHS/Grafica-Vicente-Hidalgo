# coding=utf-8
"""Hermite and Bezier curves using python, numpy and matplotlib"""

import numpy as np
import matplotlib.pyplot as mpl
from mpl_toolkits.mplot3d import Axes3D

__author__ = "Daniel Calderon"
__license__ = "MIT"


def generateT(t):
    return np.array([[1, t, t**2, t**3]]).T


def hermiteMatrix(P1, P2, T1, T2):
    
    # Generate a matrix concatenating the columns
    G = np.concatenate((P1, P2, T1, T2), axis=1)
    
    # Hermite base matrix is a constant
    Mh = np.array([[1, 0, -3, 2], [0, 0, 3, -2], [0, 1, -2, 1], [0, 0, -1, 1]])    
    
    return np.matmul(G, Mh)


def bezierMatrix(P0, P1, P2, P3):
    
    # Generate a matrix concatenating the columns
    G = np.concatenate((P0, P1, P2, P3), axis=1)

    # Bezier base matrix is a constant
    Mb = np.array([[1, -3, 3, -1], [0, 3, -6, 3], [0, 0, 3, -3], [0, 0, 0, 1]])
    
    return np.matmul(G, Mb)


#################################################
#################################################
#################################################
#################################################
#################################################
#################################################

Lista = [np.array([[-1, -1, 50]]).T,  #P0
    np.array([[0, 0, 50]]).T,         #P1
    np.array([[5, 6, 45]]).T,         #P2
    np.array([[0, 12, 40]]).T,        #P3
    np.array([[-5, 6, 35]]).T,        #P4
    np.array([[-10, -2, 30]]).T,      #P5
    np.array([[-5, 0, 25]]).T]        #P6

def CatmullRomMatrixL(L):
    Matrices = []
    for i in range(len(L)-3):

        #Generate a matrix contatenating the columns
        G = np.concatenate((L[i], L[i+1], L[i+2], L[i+3]), axis=1)

        # Catmull-Rom vase matrix is a constant
        Mcr = np.array([[0,-1/2,1,-1/2],[1,0,-5/2,3/2],[0,1/2,2,-3/2],[0,0,-1/2,1/2]])

        Matrices.append(np.matmul(G,Mcr))
    
    return Matrices

#print(CatmullRomMatrixL(Lista))

def evalCurveCR(Matrices, N):
    # The parameter t should move between 0 and 1
    ts = np.linspace(0.0, 1.0, N)
    
    Curvas = []
    for j in range(len(Matrices)):

        M = Matrices[j]
        # The computed value in R3 for each sample will be stored here
        curve = np.ndarray(shape=(N, 3), dtype=float)
    
        for i in range(len(ts)):
            T = generateT(ts[i])
            curve[i, 0:3] = np.matmul(M, T).T
            Curvas.append(curve)
        
    return Curvas

#print(evalCurveCR(CatmullRomMatrixL(Lista),20))


def CatmullRomMatrix(p0, p1, p2, p3):

    #Generate a matrix contatenating the columns
    G = np.concatenate((p0, p1, p2, p3), axis=1)

    # Catmull-Rom vase matrix is a constant
    Mcr = np.array([[0,-1/2,1,-1/2],[1,0,-5/2,3/2],[0,1/2,2,-3/2],[0,0,-1/2,1/2]])

    return np.matmul(G, Mcr)




#################################################
#################################################
#################################################
#################################################
#################################################
#################################################


def plotCurve(ax, curve, label, color=(0,0,1)):
    
    xs = curve[:, 0]
    ys = curve[:, 1]
    zs = curve[:, 2]
    
    ax.plot(xs, ys, zs, label=label, color=color)
    

# M is the cubic curve matrix, N is the number of samples between 0 and 1
def evalCurve(M, N):
    # The parameter t should move between 0 and 1
    ts = np.linspace(0.0, 1.0, N)
    
    # The computed value in R3 for each sample will be stored here
    curve = np.ndarray(shape=(N, 3), dtype=float)
    
    for i in range(len(ts)):
        T = generateT(ts[i])
        curve[i, 0:3] = np.matmul(M, T).T
        
    return curve

if __name__ == "__main__":
    
    hermiteCurve = evalCurve(CatmullRomMatrixL(Lista)[0], 20)
    print(hermiteCurve)
    hermiteCurve2 = evalCurve(CatmullRomMatrixL(Lista)[1], 20)
    hermiteCurve3 = evalCurve(CatmullRomMatrixL(Lista)[2], 20)
    hermiteCurve4 = evalCurve(CatmullRomMatrixL(Lista)[3], 20)
    
    # Setting up the matplotlib display for 3D
    fig = mpl.figure()
    ax = fig.gca(projection='3d')
        
    plotCurve(ax, hermiteCurve, "Hermite curve", (1,0,0))
    plotCurve(ax, hermiteCurve2, "Hermite curve", (0,1,0))
    plotCurve(ax, hermiteCurve3, "Hermite curve", (1,0,1))
    plotCurve(ax, hermiteCurve4, "Hermite curve", (1,1,0))
    
    
    # Adding a visualization of the control points
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.legend()
    mpl.show()