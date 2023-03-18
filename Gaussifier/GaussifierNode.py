# gaussifierNode.py

import sys
import random

import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

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
kPluginNodeTypeName = "gaussifierNode"


# Give the node a unique ID. Make sure this ID is different from all of your other nodes!
gaussifierNodeId = OpenMaya.MTypeId(0x8704)

# Node definition
class gaussifierNode(OpenMayaMPx.MPxNode):
    # Declare class variables:
    # TODO:: declare the input and output class variables
    #         i.e. inNumPoints = OpenMaya.MObject()

    inNumPoints = OpenMaya.MObject()

    xCov = OpenMaya.MObject()
    yCov = OpenMaya.MObject()
    zCov = OpenMaya.MObject()


    outPoints = OpenMaya.MObject()


    
    # constructor
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    # compute
    def compute(self,plug,data):
        # TODO:: create the main functionality of the node. Your node should 
        #         take in three floats for max position (X,Y,Z), three floats 
        #         for min position (X,Y,Z), and the number of random points to
        #         be generated. Your node should output an MFnArrayAttrsData 
        #         object containing the random points. Consult the homework
        #         sheet for how to deal with creating the MFnArrayAttrsData. 

        if plug == gaussifierNode.outPoints:

            inNumPointsData = data.inputValue(gaussifierNode.inNumPoints)
            inNumPointsValue = inNumPointsData.asInt()

            xCovData = data.inputValue(gaussifierNode.xCov)
            xCovValue = xCovData.asFloat()   
            yCovData = data.inputValue(gaussifierNode.yCov)
            yCovValue = yCovData.asFloat()
            zCovData = data.inputValue(gaussifierNode.zCov)
            zCovValue = zCovData.asFloat()

            pointsData = data.outputValue(gaussifierNode.outPoints) 
            pointsAAD = OpenMaya.MFnArrayAttrsData() 
            pointsObject = pointsAAD.create()

            # Create the vectors for "position" and "id". Names and types must match  
            # the table above.
            positionArray = pointsAAD.vectorArray("position")
            idArray = pointsAAD.doubleArray("id")

            # Loop to fill the arrays:
            for index in range(0, inNumPointsValue):
                pX = random.uniform(0, 1)
                pY = random.uniform(0, 1)
                pZ = random.uniform(0, 1)

                positionArray.append(OpenMaya.MVector(pX, pY, pZ))
                idArray.append(index)

            # Finally set the output data handle pointsData.setMObject(pointsObject)
            pointsData.setMObject(pointsObject)



        data.setClean(plug)
    
# initializer
def nodeInitializer():
    tAttr = OpenMaya.MFnTypedAttribute()
    nAttr = OpenMaya.MFnNumericAttribute()

    # TODO:: initialize the input and output attributes. Be sure to use the 
    #         MAKE_INPUT and MAKE_OUTPUT functions.

    gaussifierNode.inNumPoints = nAttr.create("numPoints", "np", OpenMaya.MFnNumericData.kInt, 10)
    MAKE_INPUT(nAttr)

    gaussifierNode.xCov = nAttr.create("xCovariance", "xCov", OpenMaya.MFnNumericData.kFloat, 0.5)
    MAKE_INPUT(nAttr)
    gaussifierNode.yCov = nAttr.create("yCovariance", "yCov", OpenMaya.MFnNumericData.kFloat, 0.5)
    MAKE_INPUT(nAttr)
    gaussifierNode.zCov = nAttr.create("zCovariance", "zCov", OpenMaya.MFnNumericData.kFloat, 0.5)
    MAKE_INPUT(nAttr)



    gaussifierNode.outPoints = tAttr.create("outPoints", "op", OpenMaya.MFnArrayAttrsData.kDynArrayAttrs)
    MAKE_OUTPUT(tAttr)


    try:
        # TODO:: add the attributes to the node and set up the
        #         attributeAffects (addAttribute, and attributeAffects)
        print("Initialization!\n")

        gaussifierNode.addAttribute(gaussifierNode.inNumPoints)
        gaussifierNode.addAttribute(gaussifierNode.xCov)
        gaussifierNode.addAttribute(gaussifierNode.yCov)
        gaussifierNode.addAttribute(gaussifierNode.zCov)
        gaussifierNode.addAttribute(gaussifierNode.outPoints)  

        gaussifierNode.attributeAffects(gaussifierNode.inNumPoints, gaussifierNode.outPoints)
        gaussifierNode.attributeAffects(gaussifierNode.xCov, gaussifierNode.outPoints)
        gaussifierNode.attributeAffects(gaussifierNode.yCov, gaussifierNode.outPoints)
        gaussifierNode.attributeAffects(gaussifierNode.zCov, gaussifierNode.outPoints)

    except:
        sys.stderr.write( ("Failed to create attributes of %s node\n", kPluginNodeTypeName) )

# creator
def nodeCreator():
    return OpenMayaMPx.asMPxPtr( gaussifierNode() )

# initialize the script plug-in
def initializePlugin(mobject):
    
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    sys.path.append('D:/Upenn/CGGT/CIS660/Gaussifier/Gaussifier')

    try:
        mplugin.registerCommand("GaussifierCmd", nodeCreator)
        mplugin.registerNode( kPluginNodeTypeName, gaussifierNodeId, nodeCreator, nodeInitializer )
    except:
        sys.stderr.write( "Failed to register node: %s\n" % kPluginNodeTypeName )

    melPath = mplugin.loadPath() + "/GaussifierDialog.mel"
    melFile = open(melPath, "r")
    melCmds = melFile.read().replace("\n", "")
    OpenMaya.MGlobal.executeCommand(melCmds)
    

# uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode( gaussifierNodeId )
    except:
        sys.stderr.write( "Failed to unregister node: %s\n" % kPluginNodeTypeName )
