import sys
import math

import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds


def doIt(mesh):
    # message in Maya output window
    print("Implement Me!") 
    
    numVertices = cmds.polyEvaluate(mesh, vertex=True)
    vertices = cmds.polyListComponentConversion(mesh, tv=True) # convert mesh to vertices
    faces = cmds.polyListComponentConversion(mesh, tf=True) # convert mesh to faces

    vertex_data = cmds.getAttr(mesh+'.vtx[*]') # get vertex positions
    face_data = cmds.ls(faces, fl=True) # get face vertex indices
    print(vertex_data)
    print(face_data)
   
