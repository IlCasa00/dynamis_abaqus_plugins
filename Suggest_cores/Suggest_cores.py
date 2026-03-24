# -*- coding: 1252 -*-
from abaqus import *
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
from math import *

def getCurrentModel():
    """
    Ritorna una stringa contenente il nome del modello attualmente
    attivo nel viewport
    """
    vpName = session.currentViewportName
    return str(session.sessionState[vpName]['modelName'])

def suggest_cores():
    # ottenimento del numero d nodi
    modelName = getCurrentModel()
    tot_nodi = sum([len(mdb.models[modelName].rootAssembly.instances[instanceName].nodes) for instanceName in mdb.models[modelName].rootAssembly.instances.keys()])        
    print('Suggested cores: {}'.format(int(tot_nodi/70000)+1))