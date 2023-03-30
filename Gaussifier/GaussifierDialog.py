import maya.cmds as cmds
import GaussifierCmd
import numpy as np

from functools import partial




def createMenu():
    gMainWindow = "MayaWindow"
    cmds.setParent(gMainWindow)
    cmds.menu(label="Gaussifier", parent=gMainWindow)
    cmds.menuItem(label="Gaussifier Command", command=createDialogWindow)


def createNode():
    transformNode = cmds.createNode("transform", name="Gaussifier1")
    meshNode = cmds.createNode("mesh", name="GaussifierShape1", parent=transformNode)
    cmds.sets(meshNode, add="initialShadingGroup")
    gaussifierNode = cmds.createNode("GaussifierNode", name="GaussifierNode1")
    cmds.connectAttr(gaussifierNode + ".outputMesh", meshNode + ".inMesh")


    orignalTransformNode = cmds.createNode("transform", name="ControlMesh")
    controlMeshNode = cmds.createNode("mesh", name="ControlMeshShape1", parent=orignalTransformNode)
    cmds.sets(controlMeshNode, add="initialShadingGroup")
    cmds.scale(2, 2, 2, orignalTransformNode)
    cmds.connectAttr(gaussifierNode + ".controlMesh", controlMeshNode + ".inMesh")
    cmds.connectAttr(transformNode + ".translate", orignalTransformNode + ".translate")
    cmds.connectAttr(transformNode + ".rotate", orignalTransformNode + ".rotate")
   
def loadMesh(melArg):
    objects = cmds.ls(selection=True)
    if objects:
        mesh = objects[0]
        GaussifierCmd.loadMesh(mesh)
    else:
        print("No mesh is selected.")


def generateMesh(melArg):
    createNode()

def setCovariance(scrollField):
    global vertIndex
    covStr = cmds.scrollField(scrollField, q=True, text=True)
    print(covStr)
    GaussifierCmd.setCovarianceAt(vertIndex, covStr)
    GaussifierCmd.generateMesh(1)
    cmds.setAttr("GaussifierNode1.numSubdivisions", 1)



def createDialogWindow(melArg):
    dialogWindow = cmds.window(title="Gaussifier", widthHeight=(500, 500), rtf=True)

    cmds.frameLayout(label=" ")
    cmds.rowLayout(nc=2, adjustableColumn=1)
    cmds.text(label="Browse for input mesh files")
    cmds.button(label="Browse", w=120, h=20, command=loadMesh)
    cmds.setParent("..")
    cmds.button(label="Load selected Mesh", w=120, h=20, command=loadMesh)
    cmds.setParent("..")
    
    cmds.frameLayout(label="Selected vertex")
    selectedVertexScrollField = cmds.scrollField(wordWrap=True, editable=True)
    cmds.button(label="Update Mesh", w=120, h=20, command=lambda melArg: setCovariance(selectedVertexScrollField))
    cmds.setParent("..")
    
    cmds.frameLayout(label="Selected covariance parameters", collapsable=True, collapse=False)
    cmds.columnLayout() 
    cmds.floatSliderGrp("xSlider", label="X", field=True, min=0.0, max=1.0)
    cmds.floatSliderGrp("ySlider", label="Y", field=True, min=0.0, max=1.0)
    cmds.floatSliderGrp("zSlider", label="Z", field=True, min=0.0, max=1.0)
    cmds.setParent("..")
    cmds.setParent("..")

    buttonsForm = cmds.formLayout(numberOfDivisions=100)
    generateButton = cmds.button(label="Generate", w=100, h=40, command=generateMesh)
    cancelButton = cmds.button(label="Cancel", w=100, h=40, command=lambda *args: cmds.deleteUI(dialogWindow))

    cmds.formLayout(buttonsForm, edit=True,
                    attachForm=[(generateButton, "left", 50), (cancelButton, "right", 50)])
    cmds.showWindow(dialogWindow)


    cmds.scriptJob(event=["SelectionChanged", lambda: updateScrollfield(selectedVertexScrollField)])
    

def updateScrollfield(scrollField, *args):
    selected_objects = cmds.ls(selection=True)
    if selected_objects:
        selectedVertex = selected_objects[0]
        start = indexOf("[", selectedVertex)

        if start == -1:
            return 
        global vertIndex
        global covStr
        end = indexOf("]", selectedVertex)
        vertIndexStr = selectedVertex[start + 1:end]
        vertIndex = int(vertIndexStr)
        covStr = np.array2string(GaussifierCmd.getCovarianceAt(vertIndex), precision=3)
        cmds.scrollField(scrollField, edit=True, text=covStr)
    else:
        cmds.scrollField(scrollField, edit=True, text="")

def indexOf(val, vertexStr):
    try:
        return vertexStr.index(val)
    except ValueError:
        return -1 