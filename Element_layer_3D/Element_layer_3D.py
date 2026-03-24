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

# mappa facce opposte:
# 1-2 -> 0-1
# 4-6 -> 3-5
# 3-5 -> 2-4

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

def element_layer_3D(faces, nLayer):
    modelName = getCurrentModel()
    # ottenimento del primo strato di elementi
    # inizializzazione su prima faccia
    elements = faces[0].getElements()[0:]
    #ciclaggio sulle restanti
    for face in faces:
        elementsRaw = faces[0].getElements()[0:]
        for ii in range(len(elementsRaw)):
            if elementsRaw[ii] not in elements:
                elements += elementsRaw[ii]
    # ottenimento facce esterne elementi
    prevFaces = []
    for face in faces:
        prevFaces += list(face.getElementFaces())
    # srtrati successivi
    # inizializzaizone strato precedente
    prevLayer = list(elements)
    # ciclaggio layers
    while nLayer > 1:
        currLayer = []
        currFaces = []
        for element in prevLayer:
            elemFaces = list(element.getElementFaces())
            for elemFace in elemFaces:
                if elemFace in prevFaces:
                    faceIdx = elemFaces.index(elemFace)
                    match faceIdx:
                        case 0:
                            faceIdx = 1
                        case 1:
                            faceIdx = 0
                        case 2:
                            faceIdx = 4
                        case 4:
                            faceIdx = 2
                        case 3:
                            faceIdx = 5
                        case 5:
                            faceIdx = 3
                    candidates = elemFaces[faceIdx].getElements()
                    for ii in range(len(candidates)):
                        if candidates[ii] not in elements:
                            elements += candidates[ii:ii+1]
                            currLayer += candidates[ii]
                            currFaces += elemFaces[faceIdx]
        nLayer -= 1
    # nome del set
    setCounter = 1
    if faces[0].instanceName:
        while 'elemLayer3D-'+str(setCounter) in mdb.models[modelName].rootAssembly.sets.keys():
            setCounter += 1
        setName = 'elemLayer3D-'+str(setCounter)
        mdb.models[modelName].rootAssembly.Set(elements=elements, name=setName)
    else:
        partName = getCurrentPart()
        while 'elemLayer3D-'+str(setCounter) in mdb.models[modelName].parts[partName].sets.keys():
            setCounter += 1
        setName = 'elemLayer3D-'+str(setCounter)
        mdb.models[modelName].parts[partName].Set(elements=elements, name=setName)
    print('Created element set: '+setName)