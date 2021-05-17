    def createTextureQuad4():

        # Defining locations and texture coordinates for each vertex of the shape    
        vertices = [
        #   positions        texture
            -1.0, -1.0, 0.0,  0, 1,
            0.0, -1.0, 0.0, 1,1,
            0.0, 0.0, 0.0, 1,0,
            -1.0, 0.0, 0.0, 0,0
            -1.0 ,1.0, 0.0,  1,0,
            0.0, 1.0, 0.0, 1,0,
            1.0, 1.0, 0.0, 1, 0,
            1.0, 0.0, 0.0, 1,1,
            1.0,-1.0,0.0,1,1]

        # Defining connections among vertices
        # We have a triangle every 3 indices specified
        indices = [
            0,1,2,
            2,3,0,
            3,2,4,
            4,5,2,
            2,5,6,
            6,7,2,
            2,7,8,
            2,1,8]

        return Shape(vertices, indices)