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

def beam_auto_orient(modelName):
    for partName in mdb.models[modelName].parts.keys():
        for edgeId in range(len(mdb.models[modelName].parts[partName].edges)):
            punto = mdb.models[modelName].parts[partName].edges[edgeId].pointOn[0]
            if not mdb.models[modelName].parts[partName].faces.findAt((punto,)):
                regione = Region(edges=mdb.models[modelName].parts[partName].edges[edgeId:edgeId+1])
                mdb.models[modelName].parts[partName].assignBeamSectionOrientation(method=
                    N1_COSINES, n1=(0.0, 0.0, -1.0), region=regione)