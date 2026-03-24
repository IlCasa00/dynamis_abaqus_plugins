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

# V2

def getCurrentModel():
    """
    Ritorna una stringa contenente il nome del modello attualmente
    attivo nel viewport
    """
    vpName = session.currentViewportName
    return str(session.sessionState[vpName]['modelName'])

def assingn_sections(sectionName, overwriteFlag, instList):
    modelName = getCurrentModel()
    parts = list(dict.fromkeys([ii.partName for ii in instList]))
    # determinazione delle parti di interesse
    # ciclaggio sulle parti
    for partName in parts:
        # assegno sezione se non e' gia' stata assegnata o se il flag di overwrite lo consente
        if (not mdb.models[modelName].parts[partName].sectionAssignments) or overwriteFlag:
            mdb.models[modelName].parts[partName].SectionAssignment(offset=0.0, 
                offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
                cells=mdb.models[modelName].parts[partName].cells),
                sectionName=sectionName, thicknessAssignment=FROM_SECTION)
    mdb.models[modelName].rootAssembly.regenerate()