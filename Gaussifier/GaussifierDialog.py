import maya.cmds as cmds
import GaussifierCmd
import GaussifierNode
import numpy as np

from functools import partial


global currNumSubdiv
currNumSubdiv = int(1)

def getCurrNumSubdiv():
    global currNumSubdiv
    return currNumSubdiv

def setCurrNumSubdiv(numSubdiv):
    global currNumSubdiv
    currNumSubdiv = numSubdiv


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

    global controlMeshNode

    orignalTransformNode = cmds.createNode("transform", name="ControlMesh")
    controlMeshNode = cmds.createNode("mesh", name="ControlMeshShape1", parent=orignalTransformNode)
    cmds.sets(controlMeshNode, add="initialShadingGroup")
    # cmds.scale(2, 2, 2, orignalTransformNode)
    cmds.connectAttr(gaussifierNode + ".controlMesh", controlMeshNode + ".inMesh")
    # cmds.connectAttr(transformNode + ".translate", orignalTransformNode + ".translate")
    cmds.connectAttr(transformNode + ".rotate", orignalTransformNode + ".rotate")
    cmds.connectAttr(transformNode + ".scale", orignalTransformNode + ".scale")

   
def loadMesh(melArg):
    objects = cmds.ls(selection=True)
    if objects:
        mesh = objects[0]
        GaussifierCmd.loadMesh(mesh)
    else:
        print("No mesh is selected.")

def generateCovariances(melArg):
    GaussifierCmd.generateInvCov()


def generateMesh(melArg):
    createNode()
    visualizeCovariances()


def setCovariance(scrollField):
    global vertIndex
    covStr = cmds.scrollField(scrollField, q=True, text=True)
    # print("covStr inSetCovariance: " + covStr)
    GaussifierCmd.setCovarianceAt(vertIndex, covStr)
    # print("Before Generate Mesh")
    # GaussifierCmd.generateMesh(GaussifierNode.getCurrNumSubdiv())
    cmds.setAttr("GaussifierNode1.numSubdivisions", getCurrNumSubdiv())

def saveCovToFile(melArg):
    invCovs = GaussifierCmd.getInvCovs()
    flattenedCov = invCovs.reshape((invCovs.shape[0], -1))
    savePath = cmds.fileDialog2(fileMode = 0, caption = 'Save Covariance', 
                                okCaption = 'Save', startingDirectory = 
                                'D:/Upenn/CGGT/CIS660/Gaussifier/Gaussifier',
                                fileFilter = 'Text Files (*.txt)')
    if savePath is not None:
        np.savetxt(savePath[0], flattenedCov, delimiter=',')
        # print(invCovs)

def readCovFromFile(melArg):
    
    covPath = cmds.fileDialog2(fileMode=1, caption="Open File", fileFilter="Text Files (*.txt)")
    
    if covPath is not None:
        flattenedCov = np.loadtxt(covPath[0], delimiter=',')

        # global invCovs
        # global initInvCovs
        invCovs = flattenedCov.reshape((flattenedCov.shape[0], 3, 3))
        # initInvCovs = copy.deepcopy(invCovs)
        GaussifierCmd.setInitInvCovs(invCovs)

        # global cubes
        for cube in cubes:
            cmds.delete(cube)
        visualizeCovariances()

        # print(invCovs)



def createDialogWindow(melArg):
    dialogWindow = cmds.window(title="Gaussifier", widthHeight=(500, 500), rtf=True)

    cmds.frameLayout(label=" ")
    
    
    cmds.button(label="Load selected Mesh", w=120, h=20, command=loadMesh)
    cmds.button(label="Generate covariances", w=120, h=20, command=generateCovariances)
    cmds.setParent("..")
    
    cmds.frameLayout(label="Selected vertex")
    selectedVertexScrollField = cmds.scrollField(wordWrap=True, editable=True)

    cmds.button(label="Update Mesh", w=120, h=20, command=lambda melArg: setCovariance(selectedVertexScrollField))

    cmds.rowLayout(nc=3, adjustableColumn=2)
    cmds.button(label="Save Covariances", w=120, h=20, command=saveCovToFile)
    cmds.text(label=" ")
    cmds.button(label="Read Covariances", w=120, h=20, command=readCovFromFile)
    cmds.setParent("..")

    #cmds.button(label="Enable covariance visualization", w=120, h=20, command=enableCovVisualization)
    #cmds.button(label="Disable covariance visualization", w=120, h=20, command=disableCovVisualization)
    covCheckBox = cmds.checkBox(label='Enable covariance visualization')
    cmds.checkBox(covCheckBox, value=True, edit=True, onCommand=enableCovVisualization, offCommand=disableCovVisualization)
    cmds.setParent("..")
    
    # cmds.frameLayout(label="Selected covariance parameters", collapsable=True, collapse=False)
    # cmds.columnLayout() 
    # cmds.floatSliderGrp("xSlider", label="X", field=True, min=0.0, max=1.0)
    # cmds.floatSliderGrp("ySlider", label="Y", field=True, min=0.0, max=1.0)
    # cmds.floatSliderGrp("zSlider", label="Z", field=True, min=0.0, max=1.0)
    # cmds.setParent("..")
    # cmds.setParent("..")

    buttonsForm = cmds.formLayout(numberOfDivisions=100)
    generateButton = cmds.button(label="Generate", w=100, h=40, command=generateMesh)
    cancelButton = cmds.button(label="Cancel", w=100, h=40, command=lambda *args: cmds.deleteUI(dialogWindow))

    cmds.formLayout(buttonsForm, edit=True,
                    attachForm=[(generateButton, "left", 50), (cancelButton, "right", 50)])
    cmds.showWindow(dialogWindow)

    cmds.scriptJob(event=["SelectionChanged", lambda: updateScrollfield(selectedVertexScrollField)])


def onScaleChanged(scrollField):
    # print("Selected Cov Scale Changed!") 

    global selectedCov
    global vertIndex

    cov = np.empty((3,3), dtype=float)
    initCov = GaussifierCmd.getInitCovarianceAt(vertIndex)

    selectedScale = cmds.getAttr(selectedCov + '.scale')
    # print("selected Scale: " + str(selectedScale[0][0]) + ", " + str(selectedScale[0][1]), ", " + str(selectedScale[0][2]))

    scale = selectedScale[0]
    # Let scaling have greater effect
    # for i in range(len(selectedScale[0])):
    #     if abs(selectedScale[0][i]) > 1.0:
    #         scale[i] = selectedScale[0][i] * 10.0
    #     else:
    #         scale[i] = selectedScale[0][i] / 10.0

    #3D to 3x3 conversion
    cov[0][0] =  initCov[0][0] * scale[0]
    cov[1][1] =  initCov[1][1] * scale[1]
    cov[2][2] =  initCov[2][2] * scale[2]

    np.set_printoptions(formatter={'float': lambda x: "{:.5f}".format(x)})
    covStr = np.array2string(cov)
    # print("covStr onScaleChanged: " + covStr)
    cmds.scrollField(scrollField, edit=True, text=covStr)

    # cov = GaussifierCmd.getCovarianceAt(vertIndex)
    # global cubes
    # cmds.setAttr(cubes[vertIndex] + ".scale", cov[0][0]*10.0, cov[1][1]*10.0, cov[2][2]*10.0)
    



def updateScrollfield(scrollField, *args):
    global nameToIndex
    global selectedCov
    # print("Selection Changed")
    selected_objects = cmds.ls(selection=True)
    if selected_objects:
        selectedCov = selected_objects[0]

        global vertIndex
        global covStr

        # select a covariance vertex
        if ".vtx[" in selectedCov:
            pass
            # start = indexOf("[", selectedCov)

            # if start == -1:
            #     return 
            
            # end = indexOf("]", selectedCov)
            # vertIndexStr = selectedCov[start + 1:end]
            # vertIndex = int(vertIndexStr)

            # # change the size of cubes
            # cov = GaussifierCmd.getCovarianceAt(vertIndex)
            # global cubes
            # cmds.setAttr(cubes[vertIndex] + ".scale", cov[0][0]*10.0, cov[1][1]*10.0, cov[2][2]*10.0)


        # select a covariance cube
        elif selectedCov.startswith("pCube"):
            cmds.scriptJob(attributeChange=[selectedCov + '.scale', lambda: onScaleChanged(scrollField)])
            vertIndex = nameToIndex[selectedCov]
        
        covStr = np.array2string(GaussifierCmd.getCovarianceAt(vertIndex), precision=4)
        
        cmds.scrollField(scrollField, edit=True, text=covStr)

    else:
        cmds.scrollField(scrollField, edit=True, text="")



def indexOf(val, vertexStr):
    try:
        return vertexStr.index(val)
    except ValueError:
        return -1 
    

def visualizeCovariances():
    global cubes
    cubes = []
    global nameToIndex
    nameToIndex = {}
    vertexData, _ = GaussifierCmd.getData()


    # invCovs = GaussifierCmd.getInvCovs()

    for i in range(len(vertexData)):
        v = vertexData[i]

        cov = GaussifierCmd.getCovarianceAt(i)
        cube = cmds.polyCube(width=cov[0][0]*10.0, height=cov[1][1]*10.0, depth=cov[2][2]*10.0)[0]
        # print(cube)
        cmds.move(v[0], v[1], v[2], cube)
        cmds.parent(cube, "ControlMesh")
    
        cubes.append(cube)
        nameToIndex[cube] = i

    # disableCovVisualization(None)

    
def enableCovVisualization(melArg):
    global cubes
    for cube in cubes:
        cmds.setAttr(cube + ".visibility", True)
        cmds.displaySurface(cube, xRay=True)
    

def disableCovVisualization(melArg):
    global cubes
    for cube in cubes:
        cmds.setAttr(cube + ".visibility", False)
