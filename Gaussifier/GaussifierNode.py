import sys

sys.path.append('<GaussifierPath>')
sys.path.append('<C:/Users/AppData/Local/Programs/Python/Python39/Lib/site-packages>')


import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

import GaussifierDialog
import GaussifierCmd


# Useful functions for declaring attributes as inputs or outputs.
def MAKE_INPUT(attr):
    attr.setKeyable(True)
    attr.setStorable(True)
    attr.setReadable(True)
    attr.setWritable(True)
def MAKE_OUTPUT(attr):
    attr.setKeyable(False)
    attr.setStorable(False)
    attr.setReadable(True)
    attr.setWritable(False)

# Define the name of the node
kPluginNodeTypeName = "GaussifierNode"


# Give the node a unique ID. Make sure this ID is different from all of your other nodes!
GaussifierNodeId = OpenMaya.MTypeId(0x8724)

# Node definition
class GaussifierNode(OpenMayaMPx.MPxNode):
    numSubdivisions = OpenMaya.MObject()

    outputMesh = OpenMaya.MObject()

    
    # constructor
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    # compute
    def compute(self,plug,data):
        if plug == GaussifierNode.outputMesh:

            numSubdivisionsData = data.inputValue(GaussifierNode.numSubdivisions)
            numSubdivisionsValue = numSubdivisionsData.asInt()

            GaussifierCmd.generateMesh(numSubdivisionsValue)
            gpsVertexData, gpsFaceData = GaussifierCmd.getGPSData()


            outputMeshData = data.outputValue(GaussifierNode.outputMesh)
            outputMeshAAD = OpenMaya.MFnMeshData()
            outputMeshObject = outputMeshAAD.create()


            faces = OpenMaya.MIntArray()
            numVertPerFace = OpenMaya.MIntArray()
            vertices = OpenMaya.MFloatPointArray()
            for f in gpsFaceData:
                numVertPerFace.append(3)
                for fv in f:
                    faces.append(int(fv))
            
            for v in gpsVertexData:
                vertices.append(OpenMaya.MFloatPoint(v[0], v[1], v[2]))


            meshFn = OpenMaya.MFnMesh()
            meshFn.create(vertices.length(), numVertPerFace.length(), vertices, numVertPerFace, faces, outputMeshObject)

            outputMeshData.setMObject(outputMeshObject)


        data.setClean(plug)
    
# initializer
def nodeInitializer():
    tAttr = OpenMaya.MFnTypedAttribute()
    nAttr = OpenMaya.MFnNumericAttribute()

    # initialize the input and output attributes. Be sure to use the MAKE_INPUT and MAKE_OUTPUT functions.
    GaussifierNode.numSubdivisions = nAttr.create("numSubdivisions", "nDiv", OpenMaya.MFnNumericData.kInt, 1)
    MAKE_INPUT(nAttr)

    GaussifierNode.outputMesh = tAttr.create("outputMesh", "out", OpenMaya.MFnData.kMesh)
    MAKE_OUTPUT(tAttr)

    try:
        # add the attributes to the node and set up the attributeAffects (addAttribute, and attributeAffects)
        print("Node initialization!\n")

        GaussifierNode.addAttribute(GaussifierNode.numSubdivisions)
        GaussifierNode.addAttribute(GaussifierNode.outputMesh)

        GaussifierNode.attributeAffects(GaussifierNode.numSubdivisions, GaussifierNode.outputMesh)

    except:
        sys.stderr.write( ("Failed to create attributes of %s node\n", kPluginNodeTypeName) )


# creator
def nodeCreator():
    return OpenMayaMPx.asMPxPtr( GaussifierNode() )


# initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    mplugin.setName("Gaussifier")

    try:
        # mplugin.registerCommand("GaussifierCmd", nodeCreator)
        mplugin.registerNode( kPluginNodeTypeName, GaussifierNodeId, nodeCreator, nodeInitializer )
    except:
        sys.stderr.write( "Failed to register node: %s/n" % kPluginNodeTypeName )    

    GaussifierDialog.createMenu()
    

# uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode( GaussifierNodeId )
    except:
        sys.stderr.write( "Failed to unregister node: %s\n" % kPluginNodeTypeName )
