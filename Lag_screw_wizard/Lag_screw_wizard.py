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
from math import *

tabella_metriche =          [2,   2.5, 3,   4,   5,   6,   8,   10,  12,  14,   16,   18,   20,   24]
tabella_altezze_dadi =      [1.6, 1.9, 2.4, 3.1, 3.9, 5.1, 6.3, 7.8, 9.8, 10.8, 12.7, 14.6, 15.3, 18.3]
tabella_diametri_rondelle = [5,   6.5, 7,   9,   10,  12,  16,  20,  24,  28,   30,   34,   37,   44]
classi =      [4.8,   5.8,    6.8,    8.8,    10.9,   12.9]
precarichi = [[490,   610,    733,    977,    1374,   1649],        # M2
              [814,   1017,   1220,   1627,   2288,   2746],        # M2.5
              [1220,  1525,   1830,   2440,   3431,   4117],        # M3
              [2115,  2664,   3173,   4231,   5950,   7140],        # M4
              [3462,  4327,   5192,   6923,   9736,   11683],       # M5
              [4875,  6093,   7312,   9750,   13710,  16452],       # M6
              [7135,  8918,   10702,  14269,  20065,  24079],       # M8
              [8947,  11184,  13421,  17894,  25164,  30197],       # M10
              [14245, 17806,  21367,  28489,  40063,  48075],       # M12
              [28390, 35487,  42585,  56780,  79847,  95816],       # M14
              [39242, 49053,  58863,  78484,  110368, 132442],      # M16
              [47533, 59416,  71300,  95066,  133687, 160424],      # M18
              [61238, 76546,  91857,  122476, 172232, 206678],      # M20
              [88232, 110291, 132349, 176465, 248154, 297784]]      # M24
mezzeriaIdx = [28, 31, 55, 59]                      # id delle facce nella mezzeria della vite per rpecarico
verticiIdx = [5, 16]                                # indici dei vertici per vincolo di coincidenza
flatFacesIdx = [17, 40, 41, 65]                     # indici delle facce piane di appoggio della testa per contatti
flatEdgesIdx = [28, 41, 43, 57, 70, 71, 78, 79]
shankFacesIdx = [20, 23, 51, 52, 53, 54, 60, 66]    # indici delle facce lisce per contatto
shankEdgesIdx = [41, 43, 48, 51, 57, 61, 76, 78]
threadFacesIdx = [22, 47, 48, 62]                   # indici facce filettate per il tie
threadEdgesIdx = [48, 49, 51, 56, 61, 74, 75, 76]
namePrefix = 'Part-lag_bolt_M'
contPropName = 'IntProp-Bolt'

def getCurrentModel():
    return str(session.sessionState[session.currentViewportName]['modelName'])

def lag_builder(modelName, metric, shank, thread):
    tab_ind = tabella_metriche.index(metric)
    height = shank + thread
    point_a = (0,0)
    point_b = (0, height+tabella_altezze_dadi[tab_ind])
    point_c = (tabella_diametri_rondelle[tab_ind]/2, height+tabella_altezze_dadi[tab_ind])
    point_d = (tabella_diametri_rondelle[tab_ind]/2, height)
    point_e = (metric/2, height)
    point_f = (metric/2, 0)
    heightStr = f'{height:.6f}'
    while heightStr[-1]=='0' and '.' in heightStr:
        heightStr = heightStr[:-1]
    if heightStr[-1]=='.':
        heightStr = heightStr[:-1]
    threadStr = f'{thread:.6f}'
    while threadStr[-1]=='0' and '.' in threadStr:
        threadStr = threadStr[:-1]
    if threadStr[-1]=='.':
        threadStr = threadStr[:-1]
    partName = namePrefix + str(metric).replace('.', '_') + 'x' + heightStr.replace('.', '_') + '-' + threadStr.replace('.', '_')
    # check esistenza materiale per il bolt
    if 'Material-bolt' not in mdb.models[modelName].materials.keys():
        mdb.models[modelName].Material(name='Material-bolt')
        mdb.models[modelName].materials['Material-bolt'].Elastic(table=((210000.0, 
            0.33), ))
    # check esistenza sezione per il bolt
    if 'Section-bolt' not in mdb.models[modelName].sections.keys():
        mdb.models[modelName].HomogeneousSolidSection(material='Material-bolt', name=
            'Section-bolt', thickness=None)
    # sketch del profilo del bullone
    mdb.models[modelName].ConstrainedSketch(name='__profile__', sheetSize=200.0)
    mdb.models[modelName].sketches['__profile__'].ConstructionLine(point1=(0.0, 
        -100.0), point2=(0.0, 100.0))
    mdb.models[modelName].sketches['__profile__'].FixedConstraint(entity=
        mdb.models[modelName].sketches['__profile__'].geometry[2])
    mdb.models[modelName].sketches['__profile__'].Line(point1=point_a, point2=point_b)
    mdb.models[modelName].sketches['__profile__'].VerticalConstraint(addUndoState=
        False, entity=mdb.models[modelName].sketches['__profile__'].geometry[3])
    mdb.models[modelName].sketches['__profile__'].ParallelConstraint(addUndoState=
        False, entity1=mdb.models[modelName].sketches['__profile__'].geometry[2], 
        entity2=mdb.models[modelName].sketches['__profile__'].geometry[3])
    mdb.models[modelName].sketches['__profile__'].CoincidentConstraint(
        addUndoState=False, entity1=
        mdb.models[modelName].sketches['__profile__'].vertices[0], entity2=
        mdb.models[modelName].sketches['__profile__'].geometry[2])
    mdb.models[modelName].sketches['__profile__'].Line(point1=point_b, point2=point_c)
    mdb.models[modelName].sketches['__profile__'].HorizontalConstraint(
        addUndoState=False, entity=
        mdb.models[modelName].sketches['__profile__'].geometry[4])
    mdb.models[modelName].sketches['__profile__'].PerpendicularConstraint(
        addUndoState=False, entity1=
        mdb.models[modelName].sketches['__profile__'].geometry[3], entity2=
        mdb.models[modelName].sketches['__profile__'].geometry[4])
    mdb.models[modelName].sketches['__profile__'].Line(point1=point_c, point2=point_d)
    mdb.models[modelName].sketches['__profile__'].VerticalConstraint(addUndoState=
        False, entity=mdb.models[modelName].sketches['__profile__'].geometry[5])
    mdb.models[modelName].sketches['__profile__'].PerpendicularConstraint(
        addUndoState=False, entity1=
        mdb.models[modelName].sketches['__profile__'].geometry[4], entity2=
        mdb.models[modelName].sketches['__profile__'].geometry[5])
    mdb.models[modelName].sketches['__profile__'].Line(point1=point_d, point2=point_e)
    mdb.models[modelName].sketches['__profile__'].HorizontalConstraint(
        addUndoState=False, entity=
        mdb.models[modelName].sketches['__profile__'].geometry[6])
    mdb.models[modelName].sketches['__profile__'].PerpendicularConstraint(
        addUndoState=False, entity1=
        mdb.models[modelName].sketches['__profile__'].geometry[5], entity2=
        mdb.models[modelName].sketches['__profile__'].geometry[6])
    mdb.models[modelName].sketches['__profile__'].Line(point1=point_e, point2=point_f)
    mdb.models[modelName].sketches['__profile__'].VerticalConstraint(addUndoState=
        False, entity=mdb.models[modelName].sketches['__profile__'].geometry[7])
    mdb.models[modelName].sketches['__profile__'].PerpendicularConstraint(
        addUndoState=False, entity1=
        mdb.models[modelName].sketches['__profile__'].geometry[6], entity2=
        mdb.models[modelName].sketches['__profile__'].geometry[7])
    mdb.models[modelName].sketches['__profile__'].Line(point1=point_f, point2=point_a)
    mdb.models[modelName].sketches['__profile__'].HorizontalConstraint(
        addUndoState=False, entity=
        mdb.models[modelName].sketches['__profile__'].geometry[8])
    mdb.models[modelName].sketches['__profile__'].PerpendicularConstraint(
        addUndoState=False, entity1=
        mdb.models[modelName].sketches['__profile__'].geometry[7], entity2=
        mdb.models[modelName].sketches['__profile__'].geometry[8])
    mdb.models[modelName].Part(dimensionality=THREE_D, name=partName, type=
        DEFORMABLE_BODY)
    mdb.models[modelName].parts[partName].BaseSolidRevolve(angle=360.0, 
        flipRevolveDirection=OFF, sketch=
        mdb.models[modelName].sketches['__profile__'])
    del mdb.models[modelName].sketches['__profile__']
    mdb.models[modelName].parts[partName].DatumPlaneByOffset(flip=SIDE2, offset=thread
        , plane=mdb.models[modelName].parts[partName].faces[4])
    mdb.models[modelName].parts[partName].PartitionCellByDatumPlane(cells=
        mdb.models[modelName].parts[partName].cells.getSequenceFromMask(('[#1 ]', 
        ), ), datumPlane=mdb.models[modelName].parts[partName].datums[2])
    mdb.models[modelName].parts[partName].PartitionCellByPlanePointNormal(cells=
        mdb.models[modelName].parts[partName].cells.getSequenceFromMask(('[#1 ]', 
        ), ), normal=mdb.models[modelName].parts[partName].edges[8], point=
        mdb.models[modelName].parts[partName].InterestingPoint(
        mdb.models[modelName].parts[partName].edges[8], MIDDLE))
    mdb.models[modelName].parts[partName].PartitionCellByExtendFace(cells=
        mdb.models[modelName].parts[partName].cells.getSequenceFromMask(('[#1 ]', 
        ), ), extendFace=mdb.models[modelName].parts[partName].faces[6])
    mdb.models[modelName].parts[partName].PartitionCellByExtendFace(cells=
        mdb.models[modelName].parts[partName].cells.getSequenceFromMask(('[#1 ]', 
        ), ), extendFace=mdb.models[modelName].parts[partName].faces[8])
    mdb.models[modelName].parts[partName].PartitionCellByPlanePointNormal(cells=
        mdb.models[modelName].parts[partName].cells.getSequenceFromMask(('[#1f ]', 
        ), ), normal=mdb.models[modelName].parts[partName].edges[10], point=
        mdb.models[modelName].parts[partName].InterestingPoint(
        mdb.models[modelName].parts[partName].edges[6], CENTER))
    mdb.models[modelName].parts[partName].PartitionCellByPlanePointNormal(cells=
        mdb.models[modelName].parts[partName].cells.getSequenceFromMask(('[#3ff ]', 
        ), ), normal=mdb.models[modelName].parts[partName].edges[0], point=
        mdb.models[modelName].parts[partName].InterestingPoint(
        mdb.models[modelName].parts[partName].edges[22], MIDDLE))
    mdb.models[modelName].parts[partName].seedPart(deviationFactor=0.1, 
        minSizeFactor=0.1, size=metric/10)
    mdb.models[modelName].parts[partName].generateMesh()
    # assegnazione della sezione
    mdb.models[modelName].parts[partName].SectionAssignment(offset=0.0, 
        offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
        cells=mdb.models[modelName].parts[partName].cells),
        sectionName='Section-bolt', thicknessAssignment=FROM_SECTION)

def lag_screw_wizard(point1, point2, point3, metric, boltClass, contactFlag, tieFlag, adjustLengthFlag):
    modelName = getCurrentModel()
    coordPoint1 = np.array(point1.pointOn)
    coordPoint2 = np.array(point2.pointOn)
    coordPoint3 = np.array(point3.pointOn)
    # calcolo altezza libera, parte liscia e parte filettata e correzione per il nome
    shank = np.linalg.norm(coordPoint1-coordPoint2)
    thread = np.linalg.norm(coordPoint2-coordPoint3)
    height = np.linalg.norm(coordPoint1-coordPoint3)
    heightStr = f'{height:.6f}'
    while heightStr[-1]=='0' and '.' in heightStr:
        heightStr = heightStr[:-1]
    if heightStr[-1]=='.':
        heightStr = heightStr[:-1]
    threadStr = f'{thread:.6f}'
    while threadStr[-1]=='0' and '.' in threadStr:
        threadStr = threadStr[:-1]
    if threadStr[-1]=='.':
        threadStr = threadStr[:-1]
    partName = namePrefix + str(metric).replace('.', '_') + 'x' + heightStr.replace('.', '_') + '-' + threadStr.replace('.', '_')
    # check esistenza bolt
    if partName not in mdb.models[modelName].parts.keys():
        lag_builder(modelName=modelName, metric=metric, shank=shank, thread=thread)
    # check step per i carichi
    if len(mdb.models[modelName].steps.keys())==1:
        stepName = 'Step-1'
        mdb.models[modelName].StaticStep(name=stepName, previous='Initial', description='', timePeriod=1.0, initialInc=0.1, minInc=1e-5, maxInc=1, nlgeom=OFF)
    else:
        stepCounter = 1
        staticStepFlag = False
        while stepCounter<=len(mdb.models[modelName].steps.keys()) and not staticStepFlag:
            stepName = mdb.models[modelName].steps.keys()[stepCounter]
            if str(mdb.models[modelName].steps[stepName].procedureType)=='STATIC_GENERAL':
                staticStepFlag = True
            else:
                stepCounter += 1
        if not staticStepFlag:
            stepName = 'Step-mannaggia'
            mdb.models[modelName].StaticStep(name=stepName, previous='Initial', description='', timePeriod=1.0, initialInc=0.1, minInc=1e-5, maxInc=1, nlgeom=OFF)
    # aggiunta instance vite all'assieme
    instanceCounter = 1
    instanceFlag = True
    while instanceFlag:
        if partName+'-'+str(instanceCounter) in mdb.models[modelName].rootAssembly.instances.keys():
            instanceCounter += 1
        else:
            instanceFlag = False
    instanceName = partName+'-'+str(instanceCounter)
    mdb.models[modelName].rootAssembly.Instance(name=instanceName, part=mdb.models[modelName].parts[partName], dependent=ON)
    # ricerca dei punti di constrain come oggetti
    coordDatumPoints = []
    keysDatumPoints = []
    for ii in mdb.models[modelName].rootAssembly.datums.keys():
        if len(dir(mdb.models[modelName].rootAssembly.datums[ii]))==24:
            coordDatumPoints.append(mdb.models[modelName].rootAssembly.datums[ii].pointOn)
            keysDatumPoints.append(ii)
    # calcolo dei delta e salvataggio punto1
    deltas = [np.linalg.norm(coordPoint1-np.array(ii)) for ii in coordDatumPoints]
    datumPoint1 = mdb.models[modelName].rootAssembly.datums[keysDatumPoints[deltas.index(min(deltas))]]
    # calcolo dei delta e salvataggio punto2
    deltas = [np.linalg.norm(coordPoint2-np.array(ii)) for ii in coordDatumPoints]
    datumPoint2 = mdb.models[modelName].rootAssembly.datums[keysDatumPoints[deltas.index(min(deltas))]]
    # calcolo dei delta e salvataggio punto3
    deltas = [np.linalg.norm(coordPoint3-np.array(ii)) for ii in coordDatumPoints]
    datumPoint3 = mdb.models[modelName].rootAssembly.datums[keysDatumPoints[deltas.index(min(deltas))]]
    # creazione del datum axis
    mdb.models[modelName].rootAssembly.DatumAxisByTwoPoint(
        point1=datumPoint1, point2=datumPoint3)
    axisKey = mdb.models[modelName].rootAssembly.datums.keys()[-1]
    # constrain punto
    mdb.models[modelName].rootAssembly.CoincidentPoint(fixedPoint= datumPoint1, movablePoint=
        mdb.models[modelName].rootAssembly.instances[instanceName].vertices[verticiIdx[0]])
    # constrain asse
    mdb.models[modelName].rootAssembly.EdgeToEdge(fixedAxis=
        mdb.models[modelName].rootAssembly.datums[axisKey], flip=OFF, movableAxis=
        mdb.models[modelName].rootAssembly.instances[instanceName].datums[1])
    # eventuale flip del constrain
    distanza = np.linalg.norm(coordPoint3 - np.array(mdb.models[modelName].rootAssembly.instances[instanceName].vertices[verticiIdx[1]].pointOn))
    if distanza > height/2:
        constrainName = mdb.models[modelName].rootAssembly.features.keys()[-1]
        mdb.models[modelName].rootAssembly.features[constrainName].setValues(flip=1)
        mdb.models[modelName].rootAssembly.regenerate()
    # determinaizone precarico
    boltLoad = np.array(precarichi)[tabella_metriche.index(metric), classi.index(float(boltClass))]
    # ricerca dei punti delle facce
    faceIdx = []
    for ii in mezzeriaIdx:
        faceIdx.append(mdb.models[modelName].rootAssembly.instances[instanceName].faces[ii].pointOn)
    # nome del carico
    loadCounter = 1
    loadFlag = True
    while loadFlag:
        if 'Preload_M'+str(metric)+'_'+str(loadCounter) in mdb.models[modelName].loads.keys():
            loadCounter += 1
        else:
            loadFlag = False
            loadName = 'Preload_M'+str(metric)+'_'+str(loadCounter)
    # creazione del carico
    regione = Region(side1Faces=mdb.models[modelName].rootAssembly.instances[instanceName].faces.findAt(faceIdx[0], faceIdx[1], faceIdx[2], faceIdx[3],))
    if adjustLengthFlag:
        kBolt = 210000*pi*metric**2/4/shank
        adjustLength = boltLoad/kBolt
        mdb.models[modelName].BoltLoad(boltMethod=ADJUST_LENGTH, createStepName=stepName,
            datumAxis=None, magnitude=adjustLength, name=loadName, region=regione)
    else:
        mdb.models[modelName].BoltLoad(boltMethod=APPLY_FORCE, createStepName=stepName,
            datumAxis=None, magnitude=boltLoad, name=loadName, region=regione)
    ##############################
    ### creazione dei contatti ###
    ##############################
    if contactFlag:
        # indici dei nodi sugli spigoli delle facce piane
        edgesNodesIdx = []
        for ii in flatEdgesIdx:
            edgesNodesIdx += [jj.label for jj in mdb.models[modelName].rootAssembly.instances[instanceName].edges[ii].getNodes() if jj.label not in edgesNodesIdx]
        # indici dei nodi delle facce piane meno gli spigoli
        facesNodesCoords = []
        for ii in flatFacesIdx:
            facesNodesCoords += [jj.coordinates for jj in mdb.models[modelName].rootAssembly.instances[instanceName].faces[ii].getNodes() if jj.label not in edgesNodesIdx]
        facesNodesCoords = tuple(facesNodesCoords)
        # ottenimento delle instance non bolt
        nonBoltInstances = [ii for ii in mdb.models[modelName].rootAssembly.instances.keys() if namePrefix not in ii]
        # ricerca degli id delle facce vicine ai nodi di tutte le instance
        # creazione del dict sulle instance
        faceIdx = {}
        for ii in nonBoltInstances:
            faceIdx.update({ii:[]})
        # ciclaggio sulle instance
        for istanza in nonBoltInstances:
            for coordinata in facesNodesCoords:
                foundFace = mdb.models[modelName].rootAssembly.instances[istanza].faces.findAt((coordinata,))
                if foundFace:
                    if foundFace[0].index not in faceIdx[istanza]:
                        faceIdx[istanza].append(foundFace[0].index)
        # eliminazione dei dict vuoti
        ii = 0
        while ii<len(list(faceIdx.keys())):
            if not faceIdx[list(faceIdx.keys())[ii]]:
                del faceIdx[list(faceIdx.keys())[ii]]
            ii += 1
        # se non rimangono dict allora termino la funzione
        if not list(faceIdx.keys()):
            return
        # creazione della IntProp del contatto (se serve)
        if contPropName not in mdb.models[modelName].interactionProperties.keys():
            mdb.models[modelName].ContactProperty(contPropName)
            mdb.models[modelName].interactionProperties[contPropName].TangentialBehavior(
                dependencies=0, directionality=ISOTROPIC, elasticSlipStiffness=None, 
                formulation=PENALTY, fraction=0.005, maximumElasticSlip=FRACTION, 
                pressureDependency=OFF, shearStressLimit=None, slipRateDependency=OFF, 
                table=((0.4, ), ), temperatureDependency=OFF)
            mdb.models[modelName].interactionProperties[contPropName].NormalBehavior(
                allowSeparation=ON, constraintEnforcementMethod=DEFAULT, 
                pressureOverclosure=HARD)
        # creazione della regione target (componenti in morsa)
        # mannaggia al cristo bisogna accedere coi piedi a ste facce per poterle sommare
        # praticamente findAt restituisce una abaqus.Face, che non si possono sommare
        # servono delle abaqus.Facearray da sommare, che si generano con ...faces[ii:11+1]
        # che menata per tenere un array di merda, a sto punto potrei mandargli un array diretto in Region
        # ma col cazzo che me lo lasica fare, vuole per forza un faceArray
        targetFaces = mdb.models[modelName].rootAssembly.instances[list(faceIdx.keys())[0]].faces[faceIdx[list(faceIdx.keys())[0]][0]:faceIdx[list(faceIdx.keys())[0]][0]+1]
        del faceIdx[list(faceIdx.keys())[0]][0]
        if not faceIdx[list(faceIdx.keys())[0]]:
            del faceIdx[list(faceIdx.keys())[0]]
        for ii in list(faceIdx.keys()):
            for jj in faceIdx[ii]:
                targetFaces = targetFaces + mdb.models[modelName].rootAssembly.instances[ii].faces[jj:jj+1]
        targetContFaces = Region(side1Faces=targetFaces)
        # creazione della regione  source (quella del bolt)
        targetFaces = mdb.models[modelName].rootAssembly.instances[instanceName].faces[flatFacesIdx[0]:flatFacesIdx[0]+1]
        for ii in flatFacesIdx[1:]:
            targetFaces = targetFaces + mdb.models[modelName].rootAssembly.instances[instanceName].faces[ii:ii+1]
        sourceContFaces = Region(side1Faces=targetFaces)
        # creazione del contatto
        intName = 'Int-'+instanceName
        mdb.models[modelName].SurfaceToSurfaceContactStd(adjustMethod=NONE, 
            clearanceRegion=None, createStepName='Initial', datumAxis=None, 
            initialClearance=OMIT, interactionProperty=contPropName, main=targetContFaces, name=intName,
            secondary=sourceContFaces, sliding=FINITE, thickness=ON)
    #########################
    ### creazione del tie ###
    #########################
    if tieFlag:
        edgesNodesIdx = []
        for ii in threadEdgesIdx:
            edgesNodesIdx += [jj.label for jj in mdb.models[modelName].rootAssembly.instances[instanceName].edges[ii].getNodes() if jj.label]
        # indici dei nodi delle facce piane meno gli spigoli
        facesNodesCoords = []
        for ii in threadFacesIdx:
            facesNodesCoords += [jj.coordinates for jj in mdb.models[modelName].rootAssembly.instances[instanceName].faces[ii].getNodes() if jj.label not in edgesNodesIdx]
        facesNodesCoords = tuple(facesNodesCoords)
        # ottenimento delle instance che non sono lag bolts
        nonBoltInstances = [ii for ii in mdb.models[modelName].rootAssembly.instances.keys() if namePrefix not in ii]
        # ricerca degli id delle facce vicine ai nodi di tutte le instance
        # creazione del dict sulle instance
        faceIdx = {}
        for ii in nonBoltInstances:
            faceIdx.update({ii:[]})
        # ciclaggio sulle instance
        for istanza in nonBoltInstances:
            for coordinata in facesNodesCoords:
                foundFace = mdb.models[modelName].rootAssembly.instances[istanza].faces.findAt((coordinata,))
                if foundFace:
                    if foundFace[0].index not in faceIdx[istanza]:
                        faceIdx[istanza].append(foundFace[0].index)
        # eliminazione dei dict vuoti
        ii = 0
        while ii<len(list(faceIdx.keys())):
            if not faceIdx[list(faceIdx.keys())[ii]]:
                del faceIdx[list(faceIdx.keys())[ii]]
            ii += 1
        # se non rimangono dict allora termino la funzione
        if not list(faceIdx.keys()):
            return
        # creazione della regione target (la parte filettata)
        targetFaces = mdb.models[modelName].rootAssembly.instances[list(faceIdx.keys())[0]].faces[faceIdx[list(faceIdx.keys())[0]][0]:faceIdx[list(faceIdx.keys())[0]][0]+1]
        del faceIdx[list(faceIdx.keys())[0]][0]
        if not faceIdx[list(faceIdx.keys())[0]]:
            del faceIdx[list(faceIdx.keys())[0]]
        for ii in list(faceIdx.keys()):
            for jj in faceIdx[ii]:
                targetFaces = targetFaces + mdb.models[modelName].rootAssembly.instances[ii].faces[jj:jj+1]
        targetTieFaces = Region(side1Faces=targetFaces)
        # creazione della regione  source (quella del bolt)
        targetFaces = mdb.models[modelName].rootAssembly.instances[instanceName].faces[threadFacesIdx[0]:threadFacesIdx[0]+1]
        for ii in threadFacesIdx[1:]:
            targetFaces = targetFaces + mdb.models[modelName].rootAssembly.instances[instanceName].faces[ii:ii+1]
        sourceTieFaces = Region(side1Faces=targetFaces)
        # creazione del tie
        intName = 'C-'+instanceName
        mdb.models[modelName].Tie(adjust=OFF, main=sourceTieFaces, name=intName, positionToleranceMethod=COMPUTED, secondary=targetTieFaces, thickness=ON, tieRotations=ON)