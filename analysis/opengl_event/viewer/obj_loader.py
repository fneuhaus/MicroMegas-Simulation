''' Based on http://www.pygame.org/wiki/OBJFileLoader '''
from pyglet.gl import *


class WavefrontOBJ:
   def __init__(self, filename, swapyz=False, color=(0.000, 0.169, 0.212), scale_factor=1.):
      self.scale_factor = scale_factor

      """Loads a Wavefront OBJ file. """
      self.vertices = []
      self.normals = []
      self.texcoords = []
      self.faces = []

      material = None
      for line in open(filename, "r"):
         if line.startswith('#'):
            continue
         values = line.split()
         if not values:
            continue

         if values[0] == 'v':
            v = list(map(self.scale, values[1:4]))
            if swapyz:
               v = v[0], v[2], v[1]
            self.vertices.append(v)
         elif values[0] == 'vn':
            v = list(map(self.scale, values[1:4]))
            if swapyz:
               v = v[0], v[2], v[1]
            self.normals.append(v)
         elif values[0] == 'vt':
            self.texcoords.append(list(map(self.scale, values[1:3])))
         elif values[0] == 'f':
            face = []
            texcoords = []
            norms = []
            for v in values[1:]:
               w = v.split('/')
               face.append(int(w[0]))
               if len(w) >= 2 and len(w[1]) > 0:
                  texcoords.append(int(w[1]))
               else:
                  texcoords.append(0)
               if len(w) >= 3 and len(w[2]) > 0:
                  norms.append(int(w[2]))
               else:
                  norms.append(0)
            self.faces.append((face, norms, texcoords, material))

      self.gl_list = glGenLists(1)
      glNewList(self.gl_list, GL_COMPILE)
      glEnable(GL_TEXTURE_2D)
      glFrontFace(GL_CCW)
      for face in self.faces:
         vertices, normals, texture_coords, material = face
         glColor3f(*color)

         glBegin(GL_POLYGON)
         for i in range(len(vertices)):
            if normals[i] > 0:
               normal = self.normals[normals[i] - 1]
               glNormal3f(normal[0], normal[1], normal[2])
            if texture_coords[i] > 0:
               texture_coord = self.texcoords[texture_coords[i] - 1]
               glTexCoord2f(texture_coord[0], texture_coord[1], texture_coord[2])
            vertex = self.vertices[vertices[i] - 1]
            glVertex3f(vertex[0], vertex[1], vertex[2])
         glEnd()
      glDisable(GL_TEXTURE_2D)
      glEndList()

   def scale(self, value):
      return self.scale_factor * float(value)
