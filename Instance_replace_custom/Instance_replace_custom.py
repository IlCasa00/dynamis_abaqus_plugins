# -*- coding: 1252 -*-
from part import *
from material import *
from section import *
from optimization import * # type: ignore
from assembly import *
from step import * # type: ignore
from interaction import *
from load import * # type: ignore
from mesh import *
from job import * # type: ignore
from sketch import * # type: ignore
from visualization import *
from connectorBehavior import *
from abaqusConstants import *
from abaqus import *
from regionToolset import Region # type: ignore
import numpy as np

def getCurrentModel():
    """
    Ritorna una stringa contenente il nome del modello attualmente
    attivo nel viewport
    """
    return str(session.sessionState[session.currentViewportName]['modelName'])

def getCurrentPart():
    """
    Ritorna una stringa contenente il nome della parte attualmente
    attiva nel viewport
    """
    return session.viewports[session.currentViewportName].displayedObject.name

def instance_replace_custom(oldInstance, newPart:str, tangentSearchFlag:bool):
    modelName = getCurrentModel()
    # nome nuova instance
    nameCounter = 1
    while newPart+'-'+str(nameCounter) in mdb.models[modelName].rootAssembly.instances.keys():
        nameCounter += 1
    newInstance = newPart+'-'+str(nameCounter)
    # creazione della instance
    mdb.models[modelName].rootAssembly.Instance(name=newInstance, part=mdb.models[modelName].parts[newPart], dependent=ON)
    # check solidi o shell
    if not mdb.models[modelName].parts[newPart].cells:
        cellFlag = False
    else:
        cellFlag = True
    # mesh check
    if not mdb.models[modelName].parts[newPart].elements:
        meshFlag = True
        if cellFlag:
            mdb.models[modelName].parts[newPart].setMeshControls(elemShape=TET, regions=
                mdb.models[modelName].parts[newPart].cells[0:], technique=FREE)
            mdb.models[modelName].parts[newPart].setElementType(elemTypes=(ElemType(
                elemCode=C3D20R, elemLibrary=STANDARD), ElemType(elemCode=C3D15, 
                elemLibrary=STANDARD), ElemType(elemCode=C3D10, elemLibrary=STANDARD)), 
                regions=(mdb.models[modelName].parts[newPart].cells[0:]))
        mdb.models[modelName].parts[newPart].seedPart(size=0, deviationFactor=0.1,minSizeFactor=0.1)
        mdb.models[modelName].parts[newPart].generateMesh()
    else:
        meshFlag = False
    # coordinate dei nodi sugli spigoli
    newEdgeCoords = []
    for ii in mdb.models[modelName].rootAssembly.instances[newInstance].edges:
        newEdgeCoords += [jj.coordinates for jj in ii.getNodes() if jj.coordinates not in newEdgeCoords]
    # coordinate dei nodi sulle facce
    newFaceCoords = []
    for ii in mdb.models[modelName].rootAssembly.instances[newInstance].faces:
        newFaceCoords += [jj.coordinates for jj in ii.getNodes() if jj.coordinates not in newEdgeCoords]
    # conversione in array di numpy
    newEdgeCoords = np.array(newEdgeCoords)
    newFaceCoords = np.array(newFaceCoords)
    # eliminaizone mesh nel caso non ci fosse in origine
    # tanto le coordinate le ho prese
    if meshFlag:
        mdb.models[modelName].parts[newPart].deleteMesh()
    # sostituzione dei set
    for setKey in mdb.models[modelName].rootAssembly.sets.keys():
        # set di facce
        faceFlag = False
        if mdb.models[modelName].rootAssembly.sets[setKey].faces:
            faceFlag = True
            for setFaceIdx in range(len(mdb.models[modelName].rootAssembly.sets[setKey].faces)):
                if mdb.models[modelName].rootAssembly.sets[setKey].faces[setFaceIdx].instanceName==oldInstance.name:
                    # trovata faccia della vecchia instance
                    faceFlag = True
                    # coordinata del punto sulla faccia vecchia
                    oldCoord = np.array(mdb.models[modelName].rootAssembly.sets[setKey].faces[setFaceIdx].pointOn[0])
                    # calcolo dei delta dei nodi delle facce
                    deltas = [np.linalg.norm(ii) for ii in newFaceCoords-oldCoord]
                    # coordianta del nodo della nuova instance a distanza minima da punto della faccia vecchia
                    nodeCoord = list(newFaceCoords[min(deltas)])
                    if tangentSearchFlag:
                        # sequence delle nuove facce con ricerca di tangenza
                        newFaceSequence = mdb.models[modelName].rootAssembly.instances[newInstance].faces.findAt(coordinates=nodeCoord).getFacesByFaceAngle(angle=1)
                        if setFaceIdx==0:
                            faceRegion = newFaceSequence
                        else:
                            for sequenceIdx in range(len(newFaceSequence)):
                                if newFaceSequence[sequenceIdx] not in faceRegion:
                                    faceRegion += newFaceSequence[sequenceIdx:sequenceIdx+1]
                    else:
                        # sequence senza ricerca in tangenza
                        if mdb.models[modelName].rootAssembly.instances[newInstance].faces.findAt(coordinates=nodeCoord) not in faceRegion:
                            newFaceIdx = mdb.models[modelName].rootAssembly.instances[newInstance].faces.findAt(coordinates=nodeCoord).index
                            newFaceSequence = mdb.models[modelName].rootAssembly.instances[newInstance].faces[newFaceIdx:newFaceIdx+1]
                            if setFaceIdx==0:
                                faceRegion = newFaceSequence
                            else:
                                faceRegion += newFaceSequence
                else:
                    if setFaceIdx==0:
                        # inizializzazione nel caso della prima faccia
                        faceRegion = mdb.models[modelName].rootAssembly.sets[setKey].faces[0:1]
                    else:
                        # aggiunta nell'altro caso
                        faceRegion += mdb.models[modelName].rootAssembly.sets[setKey].faces[setFaceIdx:setFaceIdx+1]
        edgeFlag = False
        if mdb.models[modelName].rootAssembly.sets[setKey].edges:
            # set di spigoli
            edgeFlag = True
            for setEdgeIdx in range(len(mdb.models[modelName].rootAssembly.sets[setKey].edges)):
                if mdb.models[modelName].rootAssembly.sets[setKey].edges[setEdgeIdx].instanceName==oldInstance.name:
                    # trovato spigolo della vecchia instance
                    edgeFlag = True
                    # coordinata del punto sullo psigolo vecchio
                    oldCoord = np.array(mdb.models[modelName].rootAssembly.sets[setKey].edges[setEdgeIdx].pointOn[0])
                    # calcolo dei delta dei nodi degli spigoli
                    deltas = [np.linalg.norm(ii) for ii in newEdgeCoords-oldCoord]
                    # coordianta del nodo della nuova instance a distanza minima da punto dello spigoli vecchio
                    nodeCoord = list(newEdgeCoords[min(deltas)])
                    if tangentSearchFlag:
                        newEdgeSequence = mdb.models[modelName].rootAssembly.instances[newInstance].edges.findAt(coordinates=nodeCoord).getEdgesByEdgeAngle(angle=1)
                        if setEdgeIdx==0:
                            edgeRegion = newEdgeSequence
                        else:
                            for sequenceIdx in range(len(newEdgeSequence)):
                                if newEdgeSequence[sequenceIdx] not in edgeRegion:
                                    edgeRegion += newEdgeSequence[sequenceIdx:sequenceIdx+1]
                    else:
                        if mdb.models[modelName].rootAssembly.instances[newInstance].edges.findAt(coordinates=nodeCoord) not in edgeRegion:
                            edgeIdx = mdb.models[modelName].rootAssembly.instances[newInstance].edges.findAt(coordinates=nodeCoord).index
                            newEdgeSequence = mdb.models[modelName].rootAssembly.instances[newInstance].edges[edgeIdx:edgeIdx+1]
                            if setEdgeIdx==0:
                                edgeRegion = newEdgeSequence
                            else:
                                edgeRegion += newEdgeSequence
                else:
                    if setEdgeIdx==0:
                        # inizializzazione nel caso della primo spigolo
                        edgeRegion = mdb.models[modelName].rootAssembly.sets[setKey].edges[0:1]
                    else:
                        # aggiunta nell'altro caso
                        edgeRegion += mdb.models[modelName].rootAssembly.sets[setKey].faces[setFaceIdx:setFaceIdx+1]
        if edgeFlag and not faceFlag:
            mdb.models[modelName].rootAssembly.Set(edges=edgeRegion, name=setKey)
        elif faceFlag and not edgeFlag:
            mdb.models[modelName].rootAssembly.Set(faces=faceRegion, name=setKey)
        elif faceFlag and edgeFlag:
            mdb.models[modelName].rootAssembly.Set(faces=faceRegion, edges=edgeRegion, name=setKey)
    # sostituzione delle superfici
    for surfKey in mdb.models[modelName].rootAssembly.surfaces.keys():
        # facce
        faceFlag = False
        if mdb.models[modelName].rootAssembly.surfaces[surfKey].faces:
            faceFlag = True
            for surfFaceIdx in range(len(mdb.models[modelName].rootAssembly.surfaces[surfKey].faces)):
                if mdb.models[modelName].rootAssembly.surfaces[surfKey].faces[surfFaceIdx].instanceName==oldInstance.name:
                    # trovata faccia della vecchia instance
                    faceFlag = True
                    # coordinata del punto sulla faccia vecchia
                    oldCoord = np.array(mdb.models[modelName].rootAssembly.surfaces[surfKey].faces[surfFaceIdx].pointOn[0])
                    # calcolo dei delta dei nodi delle facce
                    deltas = [np.linalg.norm(ii) for ii in newFaceCoords-oldCoord]
                    # coordianta del nodo della nuova instance a distanza minima da punto della faccia vecchia
                    nodeCoord = list(newFaceCoords[min(deltas)])
                    if tangentSearchFlag:
                        # sequence delle nuove facce con ricerca di tangenza
                        newFaceSequence = mdb.models[modelName].rootAssembly.instances[newInstance].faces.findAt(coordinates=nodeCoord).getFacesByFaceAngle(angle=1)
                        if surfFaceIdx==0:
                            faceRegion = newFaceSequence
                        else:
                            for sequenceIdx in range(len(newFaceSequence)):
                                if newFaceSequence[sequenceIdx] not in faceRegion:
                                    faceRegion += newFaceSequence[sequenceIdx:sequenceIdx+1]
                    else:
                        # sequence senza ricerca in tangenza
                        if mdb.models[modelName].rootAssembly.instances[newInstance].faces.findAt(coordinates=nodeCoord) not in faceRegion:
                            newFaceIdx = mdb.models[modelName].rootAssembly.instances[newInstance].faces.findAt(coordinates=nodeCoord).index
                            newFaceSequence = mdb.models[modelName].rootAssembly.instances[newInstance].faces[newFaceIdx:newFaceIdx+1]
                            if surfFaceIdx==0:
                                faceRegion = newFaceSequence
                            else:
                                faceRegion += newFaceSequence
                else:
                    if surfFaceIdx==0:
                        # inizializzazione nel caso della prima faccia
                        faceRegion = mdb.models[modelName].rootAssembly.surfaces[surfKey].faces[0:1]
                    else:
                        # aggiunta nell'altro caso
                        faceRegion += mdb.models[modelName].rootAssembly.surfaces[surfKey].faces[surfFaceIdx:surfFaceIdx+1]
        edgeFlag = False
        if mdb.models[modelName].rootAssembly.surfaces[surfKey].edges:
            # spigoli
            edgeFlag = True
            for surfEdgeIdx in range(len(mdb.models[modelName].rootAssembly.surfaces[surfKey].edges)):
                if mdb.models[modelName].rootAssembly.surfaces[surfKey].edges[surfEdgeIdx].instanceName==oldInstance.name:
                    # trovato spigolo della vecchia instance
                    edgeFlag = True
                    # coordinata del punto sullo psigolo vecchio
                    oldCoord = np.array(mdb.models[modelName].rootAssembly.surfaces[surfKey].edges[surfEdgeIdx].pointOn[0])
                    # calcolo dei delta dei nodi degli spigoli
                    deltas = [np.linalg.norm(ii) for ii in newEdgeCoords-oldCoord]
                    # coordianta del nodo della nuova instance a distanza minima da punto dello spigoli vecchio
                    nodeCoord = list(newEdgeCoords[min(deltas)])
                    if tangentSearchFlag:
                        newEdgeSequence = mdb.models[modelName].rootAssembly.instances[newInstance].edges.findAt(coordinates=nodeCoord).getEdgesByEdgeAngle(angle=1)
                        if surfEdgeIdx==0:
                            edgeRegion = newEdgeSequence
                        else:
                            for sequenceIdx in range(len(newEdgeSequence)):
                                if newEdgeSequence[sequenceIdx] not in edgeRegion:
                                    edgeRegion += newEdgeSequence[sequenceIdx:sequenceIdx+1]
                    else:
                        if mdb.models[modelName].rootAssembly.instances[newInstance].edges.findAt(coordinates=nodeCoord) not in edgeRegion:
                            edgeIdx = mdb.models[modelName].rootAssembly.instances[newInstance].edges.findAt(coordinates=nodeCoord).index
                            newEdgeSequence = mdb.models[modelName].rootAssembly.instances[newInstance].edges[edgeIdx:edgeIdx+1]
                            if surfEdgeIdx==0:
                                edgeRegion = newEdgeSequence
                            else:
                                edgeRegion += newEdgeSequence
                else:
                    if surfEdgeIdx==0:
                        # inizializzazione nel caso della primo spigolo
                        edgeRegion = mdb.models[modelName].rootAssembly.surfaces[surfKey].edges[0:1]
                    else:
                        # aggiunta nell'altro caso
                        edgeRegion += mdb.models[modelName].rootAssembly.surfaces[surfKey].faces[surfFaceIdx:surfFaceIdx+1]
        if edgeFlag and not faceFlag:
            mdb.models[modelName].rootAssembly.Surface(side1Edges=edgeRegion, name=surfKey)
        elif faceFlag and not edgeFlag:
            mdb.models[modelName].rootAssembly.Surface(side1Faces=faceRegion, name=surfKey)
        elif faceFlag and edgeFlag:
            mdb.models[modelName].rootAssembly.Surface(side1Faces=faceRegion, side1Edges=edgeRegion, name=surfKey)
    # elimiazione vecchia instance
    del mdb.models[modelName].rootAssembly.features[oldInstance.name]