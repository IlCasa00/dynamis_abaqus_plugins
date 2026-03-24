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

def copy_layup(modelName1, partName1, modelName2, partName2):
    regione = Region(faces=mdb.models[modelName2].parts[partName2].faces[0:1])
    for comp_layup in mdb.models[modelName1].parts[partName1].compositeLayups.keys():
        # salvataggio parametri layup
        elem_type = mdb.models[modelName1].parts[partName1].compositeLayups[comp_layup].elementType
        offset_type = mdb.models[modelName1].parts[partName1].compositeLayups[comp_layup].offsetType
        symmetry = mdb.models[modelName1].parts[partName1].compositeLayups[comp_layup].symmetric
        spessore = mdb.models[modelName1].parts[partName1].compositeLayups[comp_layup].thicknessAssignment
        integrazione = mdb.models[modelName1].parts[partName1].compositeLayups[comp_layup].section.integrationRule
        temperatura = mdb.models[modelName1].parts[partName1].compositeLayups[comp_layup].section.temperature
        poisson_definition = mdb.models[modelName1].parts[partName1].compositeLayups[comp_layup].section.poissonDefinition
        tipo_spessore = mdb.models[modelName1].parts[partName1].compositeLayups[comp_layup].section.thicknessType
        pre_integrazione = mdb.models[modelName1].parts[partName1].compositeLayups[comp_layup].section.preIntegrate
        #offset_values = mdb.models[modelName1].parts[partName1].compositeLayups[comp_layup].offsetValues
        # creazione del layup
        mdb.models[modelName2].parts[partName2].CompositeLayup(description='', 
            elementType=elem_type, name=comp_layup, offsetType=offset_type, 
            symmetric=symmetry, thicknessAssignment=spessore)
        mdb.models[modelName2].parts[partName2].compositeLayups[comp_layup].Section(
            integrationRule=integrazione, poissonDefinition=poisson_definition, preIntegrate=pre_integrazione, 
            temperature=temperatura, thicknessType=tipo_spessore, useDensity=OFF)
        mdb.models[modelName2].parts[partName2].compositeLayups[comp_layup].ReferenceOrientation(
            additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, fieldName='', 
            localCsys=None, orientationType=GLOBAL)
        mdb.models[modelName2].parts[partName2].compositeLayups[comp_layup].suppress()
        for pelle in mdb.models[modelName1].parts[partName1].compositeLayups[comp_layup].plies.keys():
            # salvataggio parametri pelle
            angolo = mdb.models[modelName1].parts[partName1].compositeLayups[comp_layup].plies[pelle].angle
            asse = mdb.models[modelName1].parts[partName1].compositeLayups[comp_layup].plies[pelle].axis
            materiale = mdb.models[modelName1].parts[partName1].compositeLayups[comp_layup].plies[pelle].material
            int_points = mdb.models[modelName1].parts[partName1].compositeLayups[comp_layup].plies[pelle].numIntPoints
            #orientamento = mdb.models[modelName1].parts[partName1].compositeLayups[comp_layup].plies[pelle].orientationType
            nome = mdb.models[modelName1].parts[partName1].compositeLayups[comp_layup].plies[pelle].plyName
            soppresso = mdb.models[modelName1].parts[partName1].compositeLayups[comp_layup].plies[pelle].suppressed
            spessore_pelle = mdb.models[modelName1].parts[partName1].compositeLayups[comp_layup].plies[pelle].thickness
            tipo_spessore = mdb.models[modelName1].parts[partName1].compositeLayups[comp_layup].plies[pelle].thicknessType
            # creazione pelle
            mdb.models[modelName2].parts[partName2].compositeLayups[comp_layup].CompositePly(
            additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=angolo
            , axis=asse, material=materiale, numIntPoints=int_points, orientationType=
            ANGLE_0, plyName=nome, region=regione, suppressed=soppresso, thickness=spessore_pelle,
            thicknessType=tipo_spessore)
        # resume del layup se non soppresso
        if not mdb.models[modelName1].parts[partName1].compositeLayups[comp_layup].suppressed:
            mdb.models[modelName2].parts[partName2].compositeLayups[comp_layup].resume()