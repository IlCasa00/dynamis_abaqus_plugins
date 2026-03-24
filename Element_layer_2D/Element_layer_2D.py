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
from copy import copy

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

def element_layer_2d(edges, nLayers):
    # creazione primo layer
    modelName = getCurrentModel()
    elements = edges[0].getElements()[0:]
    for edge in edges[1:]:
        edgeElements = edge.getElements()
        for ii in range(len(elements)):
            if edgeElements[ii] not in elements:
                elements += edgeElements[ii:ii+1]
    # aggiunta dei layer successivi
    prevLayer = list(elements)
    while nLayers > 1:
        currLayer = []
        for element in prevLayer:
            adjElems = element.getAdjacentElements()
            for ii in range(len(adjElems)):
                if adjElems[ii] not in elements:
                    elements += adjElems[ii:ii+1]
                    currLayer += adjElems[ii]
        nLayers -= 1
        prevLayer = copy(currLayer)
    # nome del set
    setCounter = 1
    if edges[0].instanceName:
        while 'elemLayer2D-'+str(setCounter) in mdb.models[modelName].rootAssembly.sets.keys():
            setCounter += 1
        setName = 'elemLayer2D-'+str(setCounter)
        mdb.models[modelName].rootAssembly.Set(elements=elements, name=setName)
    else:
        partName = getCurrentPart()
        while 'elemLayer2D-'+str(setCounter) in mdb.models[modelName].parts[partName].sets.keys():
            setCounter += 1
        setName = 'elemLayer2D-'+str(setCounter)
        mdb.models[modelName].parts[partName].Set(elements=elements, name=setName)
    print('Created element set: '+setName)