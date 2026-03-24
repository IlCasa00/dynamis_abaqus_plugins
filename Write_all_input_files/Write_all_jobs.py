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

def write_all_jobs():
    for ii in mdb.jobs.keys():
        if mdb.jobs[ii].model in mdb.models.keys():
            mdb.jobs[ii].writeInput()