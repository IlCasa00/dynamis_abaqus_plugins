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
    vpName = session.currentViewportName
    return str(session.sessionState[vpName]['modelName'])

def predefined_output(caso, deleteFlag, historyFlag):
    match caso:
        case 'Standard':
            variabili = ('S', 'U', 'E', 'RT',)
        case 'Composite':
            variabili = ('S', 'U', 'E', 'RT', 'TSAIW',)
        case 'Contact':
            variabili = ('S', 'U', 'E', 'RT', 'CSTRESS', 'CFORCE', 'CSTATUS',)
        case 'Plastic':
            variabili = ('S', 'U', 'E', 'RT', 'EP', 'PS',)
    modelName = getCurrentModel()
    if len(mdb.models[modelName].steps.keys())==1:
        mdb.models[modelName].StaticStep(name='Step-1', previous='Initial')
        stepName = ('Step-1',)
    else:
        stepName = mdb.models[modelName].steps.keys()[1]
    # eliminazione dei field e history
    if deleteFlag:
        for f in mdb.models[modelName].fieldOutputRequests.keys():
            del mdb.models[modelName].fieldOutputRequests[f]
    if historyFlag:
        for h in mdb.models[modelName].historyOutputRequests.keys():
            del mdb.models[modelName].historyOutputRequests[h]
    # nome del field output
    idCounter = 1
    while 'F-Output-'+str(idCounter) in mdb.models[modelName].fieldOutputRequests.keys():
        idCounter += 1
    fieldName = 'F-Output-'+str(idCounter)
    mdb.models[modelName].FieldOutputRequest(createStepName=stepName, name=fieldName, variables=variabili)