""" Local shapes module, containing the logic for creating shapes"""

import numpy as np

import grafica.basic_shapes as bs

def createColorTriangleIndexation(start_index, a, b, c, color):
    # Defining locations and colors for each vertex of the shape    
    vertices = [
    #        positions               colors             
        a[0], a[1], a[2], color[0], color[1], color[2],
        b[0], b[1], b[2], color[0], color[1], color[2],
        c[0], c[1], c[2], color[0], color[1], color[2]
    ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
         start_index, start_index+1, start_index+2,
         start_index+2, start_index+3, start_index
        ]

    return (vertices, indices)


def createColorNormalsTriangleIndexation(start_index, a, b, c, color):
    # Computing normal from a b c
    v1 = np.array([a_v - b_v for a_v, b_v in zip(a, b)])
    v2 = np.array([b_v - c_v for b_v, c_v in zip(b, c)])
    v1xv2 = np.cross(v1, v2)

    # Defining locations and colors for each vertex of the shape    
    vertices = [
    #        positions               colors                        normals
        a[0], a[1], a[2], color[0], color[1], color[2], v1xv2[0], v1xv2[1], v1xv2[2],
        b[0], b[1], b[2], color[0], color[1], color[2], v1xv2[0], v1xv2[1], v1xv2[2],
        c[0], c[1], c[2], color[0], color[1], color[2], v1xv2[0], v1xv2[1], v1xv2[2]
    ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
         start_index, start_index+1, start_index+2,
         start_index+2, start_index+3, start_index
        ]

    return (vertices, indices)


def createColorQuadIndexation(start_index, a, b, c, d, color):
    # Defining locations and colors for each vertex of the shape    
    vertices = [
    #        positions               colors
        a[0], a[1], a[2], color[0], color[1], color[2],
        b[0], b[1], b[2], color[0], color[1], color[2],
        c[0], c[1], c[2], color[0], color[1], color[2],
        d[0], d[1], d[2], color[0], color[1], color[2]
    ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
         start_index, start_index+1, start_index+2,
         start_index+2, start_index+3, start_index
        ]

    return (vertices, indices)


def createColorNormalsQuadIndexation(start_index, a, b, c, d, color):

    # Computing normal from a b c
    v1 = np.array(a-b)
    v2 = np.array(b-c)
    v1xv2 = np.cross(v1, v2)

    # Defining locations and colors for each vertex of the shape    
    vertices = [
    #        positions               colors                 normals
        a[0], a[1], a[2], color[0], color[1], color[2],  v1xv2[0], v1xv2[1], v1xv2[2],
        b[0], b[1], b[2], color[0], color[1], color[2],  v1xv2[0], v1xv2[1], v1xv2[2],
        c[0], c[1], c[2], color[0], color[1], color[2],  v1xv2[0], v1xv2[1], v1xv2[2],
        d[0], d[1], d[2], color[0], color[1], color[2],  v1xv2[0], v1xv2[1], v1xv2[2]
    ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
         start_index, start_index+1, start_index+2,
         start_index+2, start_index+3, start_index
        ]
    
    return (vertices, indices)


def createColorSpecificNormals(start_index, a, b, c, d, a_n, b_n, c_n, d_n, color):


    # Defining locations and colors for each vertex of the shape    
    vertices = [
    #        positions               colors                 normals
        a[0], a[1], a[2], color[0], color[1], color[2],  a_n[0], a_n[1], a_n[2],
        b[0], b[1], b[2], color[0], color[1], color[2],  b_n[0], b_n[1], b_n[2],
        c[0], c[1], c[2], color[0], color[1], color[2],  c_n[0], c_n[1], c_n[2],
        d[0], d[1], d[2], color[0], color[1], color[2],  d_n[0], d_n[1], d_n[2]
    ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
         start_index, start_index+1, start_index+2,
         start_index+2, start_index+3, start_index
        ]
    
    return (vertices, indices)

