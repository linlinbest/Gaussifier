import maya.OpenMaya as OpenMaya
import maya.cmds as cmds

import igl
import numpy as np
import re
import copy


def getGPSData():
    global gpsVertexData
    global gpsFaceData

    return gpsVertexData, gpsFaceData


def getData():
    global vertexData
    global faceData
    return vertexData, faceData

def getInvCovs():
    global invCovs
    return invCovs

def setInitInvCovs(invCovsArg):
    global invCovs
    global initInvCovs
    invCovs = invCovsArg
    initInvCovs = copy.deepcopy(invCovs)


def setCovarianceAt(i, covStr):
    global invCovs
    covStr = covStr.replace('\n', '').replace('[', '').replace(']', '')
    print("covStr in setCovarianceAt" + covStr)
    cov = np.fromstring(covStr, sep=' ', dtype= float)
    cov = cov.reshape((3, 3))
    invCovs[i] =np.linalg.inv(cov) 


def getCovarianceAt(i):
    global invCovs
    return np.linalg.inv(invCovs[i])

def getInitCovarianceAt(i):
    global initInvCovs
    return np.linalg.inv(initInvCovs[i])


def loadMesh(mesh):
    global vertexData
    global faceData

    numVertices = cmds.polyEvaluate(mesh, vertex=True)
    numFaces = cmds.polyEvaluate(mesh, face=True)

    faceToVertex = cmds.polyInfo(mesh, faceToVertex=True)
    
    
    vertexData = np.empty(shape=(numVertices,3))
    faceData = np.empty(shape=(numFaces,3), dtype=int)

    for i in range(numVertices):
        v = cmds.pointPosition(mesh+'.vtx[' + str(i) + ']')
        vertexData[i] = np.array([v[0], v[1], v[2]])

    for i in range(numFaces):
        f = faceToVertex[i]
        indicesStr = re.findall(r'\d+', f)
        indices = [int(i) for i in indicesStr]
        faceData[i] = np.array([indices[1], indices[2], indices[3]])

    print("Selected mesh is successfully loaded.")

    generateIndentityCov()
    # generateInvCov()



def generateIndentityCov():
    global vertexData
    global invCovs
    global initInvCovs

    # creating covariance matrices with diagonal values as 0.01
    identityMat = np.identity(3) * 100.0
    invCovs = np.tile(identityMat, (len(vertexData), 1, 1))

    # invCovs = np.zeros((len(vertexData), 3, 3))
    initInvCovs = copy.deepcopy(invCovs)


def generateInvCov():
    global vertexData
    global faceData
    global invCovs
    global initInvCovs

    invCovs = np.zeros((len(vertexData), 3, 3))

    # infer covariances of the mesh
    for f in faceData:
        # compute covariance of face vertices
        cov = np.zeros((3,3))
        sum = np.zeros(3)
        for j in [1,2]:
            v = vertexData[f[j]] - vertexData[f[0]]
            sum += v
            cov += np.outer(v,v)
        cov = cov/3 - np.outer(sum,sum)/9

        # bias covariance by some fraction of its dominant eigenvalue
        bias = np.linalg.eigvalsh(cov)[2] * 0.05
        cov += np.identity(3) * bias

        for fv in f:
            invCovs[fv] += np.linalg.inv(cov)

    initInvCovs = copy.deepcopy(invCovs)
    print("Covariances are successfully generated.")


def generateMesh(numSubdivisions):
    global vertexData
    global faceData
    global invCovs

    global gpsVertexData
    global gpsFaceData

    # transform to 9D dual-space vertices
    qq1 = np.zeros((len(vertexData), 3))
    qq2 = np.zeros((len(vertexData), 3))
    qlin = np.zeros((len(vertexData), 3))
    for i, invCov in enumerate(invCovs):
        flatInvCov = invCov.flatten()
        qq1[i] = [flatInvCov[0],flatInvCov[1],flatInvCov[2]]
        qq2[i] = [flatInvCov[4],flatInvCov[5],flatInvCov[8]]
        qlin[i] = invCov @ vertexData[i]


    # perform Gaussian-product subdivision
    gpsFaceData = faceData
    for _ in range(numSubdivisions):
        qq1, _ = igl.loop(qq1, gpsFaceData)
        qq2, _ = igl.loop(qq2, gpsFaceData)
        qlin, gpsFaceData = igl.loop(qlin, gpsFaceData)
    
        
    # transform back to 3D
    gpsVertexData = np.zeros((len(qlin),3))
    for i, ql in enumerate(qlin):
        invCov = [qq1[i],
                [qq1[i,1], qq2[i,0], qq2[i,1]],
                [qq1[i,2], qq2[i,1], qq2[i,2]]]
        gpsVertexData[i] = np.linalg.inv(invCov) @ ql
   
def createFnMesh(faceData, verticesData, outputMeshObject):
    faces = OpenMaya.MIntArray()
    numVertPerFace = OpenMaya.MIntArray()
    vertices = OpenMaya.MFloatPointArray()
    for f in faceData:
        numVertPerFace.append(3)
        for fv in f:
            faces.append(int(fv))
    
    for v in verticesData:
        vertices.append(OpenMaya.MFloatPoint(v[0], v[1], v[2]))


    meshFn = OpenMaya.MFnMesh()
    meshFn.create(vertices.length(), numVertPerFace.length(), vertices, numVertPerFace, faces, outputMeshObject)
    
    return outputMeshObject