import sys

#sys.path.append('<GaussifierPath>')
sys.path.append('D:/Upenn/CGGT/CIS660/Gaussifier/Gaussifier')
sys.path.append('c:/users/admin/appdata/local/programs/python/python39/lib/site-packages')
#sys.path.append('C:/Users/Lin Zhuohao/AppData/Local/Programs/Python/Python39/Lib/site-packages')

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
    controlMesh = OpenMaya.MObject()
    
    # constructor
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    # compute
    def compute(self,plug,data):
        if plug == GaussifierNode.outputMesh:

            numSubdivisionsData = data.inputValue(GaussifierNode.numSubdivisions)
            numSubdivisionsValue = numSubdivisionsData.asInt()

            GaussifierDialog.setCurrNumSubdiv(numSubdivisionsValue)

            GaussifierCmd.generateMesh(numSubdivisionsValue)
            gpsVertexData, gpsFaceData = GaussifierCmd.getGPSData()

            outputMeshData = data.outputValue(GaussifierNode.outputMesh)
            outputMeshAAD = OpenMaya.MFnMeshData()
            outputMeshObject = outputMeshAAD.create()

            outputMeshObject = GaussifierCmd.createFnMesh(gpsFaceData, gpsVertexData, outputMeshObject)
            outputMeshData.setMObject(outputMeshObject)

            

        if plug == GaussifierNode.controlMesh:
            vertexData, faceData = GaussifierCmd.getData()
            controlMeshData = data.outputValue(GaussifierNode.controlMesh)

            controlMeshAAD = OpenMaya.MFnMeshData()
            controlMeshObject = controlMeshAAD.create() 
            controlMeshObject = GaussifierCmd.createFnMesh(faceData, vertexData, controlMeshObject)
            controlMeshData.setMObject(controlMeshObject)
            cmds.displaySurface("ControlMesh", xRay=True)

          
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

    GaussifierNode.controlMesh = tAttr.create("controlMesh", "control", OpenMaya.MFnData.kMesh)
    MAKE_OUTPUT(tAttr)


    try:
        # add the attributes to the node and set up the attributeAffects (addAttribute, and attributeAffects)
        print("Node initialization!\n")

        GaussifierNode.addAttribute(GaussifierNode.numSubdivisions)
        GaussifierNode.addAttribute(GaussifierNode.outputMesh)
        GaussifierNode.addAttribute(GaussifierNode.controlMesh)

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
