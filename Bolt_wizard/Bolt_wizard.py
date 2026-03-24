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
mezzeriaIdx = [59, 62, 70, 75]                      # id delle facce nella mezzeria della vite per rpecarico
verticiIdx = [0, 11]                                # indici dei vertici per vincolo di coincidenza
flatFacesIdx = [45, 46, 51, 53, 68, 72, 79, 82]     # indici delle facce piane di appoggio delle teste per contatti
flatEdgesIdx = [1, 53, 76, 82, 7, 58, 83, 84, 19, 77, 89, 90, 22, 73, 93, 23, 70, 99, 4, 81, 25, 94, 5, 86]
shankFacesIdx = [50, 52, 56, 57, 69, 71, 76, 83]    # indici delle facce laterali
shankEdgesIdx = [1, 4, 5, 7, 11, 16, 19, 22, 23, 25, 26, 29, 60, 74, 87, 88, 91, 92, 96, 97]
namePrefix = 'Part-Bolt_M'
contPropName = 'IntProp-Bolt'

def getCurrentModel():
    vpName = session.currentViewportName
    return str(session.sessionState[vpName]['modelName'])

def bolt_builder(modelName, metric, height):
    tab_ind = tabella_metriche.index(metric)
    point_a = (0,0)
    point_b = (0, height/2+tabella_altezze_dadi[tab_ind])
    point_c = (tabella_diametri_rondelle[tab_ind]/2, height/2+tabella_altezze_dadi[tab_ind])
    point_d = (tabella_diametri_rondelle[tab_ind]/2, height/2)
    point_e = (metric/2, height/2)
    point_f = (metric/2, 0)
    height_str = f'{height:.6f}'
    while height_str[-1]=='0' and '.' in height_str:
        height_str = height_str[:-1]
    if height_str[-1]=='.':
        height_str = height_str[:-1]
    partName = namePrefix + str(metric).replace('.', '_') + 'x' + height_str.replace('.', '_')
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
    # linea di costruzione centrale automatica
    mdb.models[modelName].sketches['__profile__'].ConstructionLine(point1=(0.0, 
        -100.0), point2=(0.0, 100.0))
    mdb.models[modelName].sketches['__profile__'].FixedConstraint(entity=
        mdb.models[modelName].sketches['__profile__'].geometry[2])
    # creazione del profilo di mezzo bullone
    mdb.models[modelName].sketches['__profile__'].Line(point1=point_a, point2=point_b)
    mdb.models[modelName].sketches['__profile__'].VerticalConstraint(addUndoState=
        False, entity=mdb.models[modelName].sketches['__profile__'].geometry[3])
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
    # rivoluzione
    mdb.models[modelName].parts[partName].BaseSolidRevolve(angle=360.0, 
        flipRevolveDirection=OFF, sketch=
        mdb.models[modelName].sketches['__profile__'])
    del mdb.models[modelName].sketches['__profile__']
    mdb.models[modelName].parts[partName].Mirror(keepOriginal=ON, mirrorPlane=
        mdb.models[modelName].parts[partName].faces[4])
    mdb.models[modelName].parts[partName].PartitionCellByPlanePointNormal(cells=
        mdb.models[modelName].parts[partName].cells.getSequenceFromMask(('[#1 ]', 
        ), ), normal=mdb.models[modelName].parts[partName].edges[10], point=
        mdb.models[modelName].parts[partName].vertices[6])
    mdb.models[modelName].parts[partName].PartitionCellByPlaneThreePoints(cells=
        mdb.models[modelName].parts[partName].cells.getSequenceFromMask(('[#3 ]', 
        ), ), point1=mdb.models[modelName].parts[partName].vertices[2], point2=
        mdb.models[modelName].parts[partName].InterestingPoint(
        mdb.models[modelName].parts[partName].edges[12], MIDDLE), point3=
        mdb.models[modelName].parts[partName].vertices[5])
    mdb.models[modelName].parts[partName].PartitionCellByPlaneThreePoints(cells=
        mdb.models[modelName].parts[partName].cells.getSequenceFromMask(('[#f ]', 
        ), ), point1=mdb.models[modelName].parts[partName].InterestingPoint(
        mdb.models[modelName].parts[partName].edges[25], MIDDLE), point2=
        mdb.models[modelName].parts[partName].InterestingPoint(
        mdb.models[modelName].parts[partName].edges[22], MIDDLE), point3=
        mdb.models[modelName].parts[partName].InterestingPoint(
        mdb.models[modelName].parts[partName].edges[4], MIDDLE))
    mdb.models[modelName].parts[partName].PartitionCellByExtendFace(cells=
        mdb.models[modelName].parts[partName].cells.getSequenceFromMask(('[#ff ]', 
        ), ), extendFace=mdb.models[modelName].parts[partName].faces[17])
    mdb.models[modelName].parts[partName].PartitionCellByExtendFace(cells=
        mdb.models[modelName].parts[partName].cells.getSequenceFromMask((
        '[#ffff ]', ), ), extendFace=
        mdb.models[modelName].parts[partName].faces[37])
    mdb.models[modelName].parts[partName].PartitionCellByExtendFace(cells=
        mdb.models[modelName].parts[partName].cells.getSequenceFromMask((
        '[#fffff ]', ), ), extendFace=
        mdb.models[modelName].parts[partName].faces[64])
    mdb.models[modelName].parts[partName].seedPart(deviationFactor=0.1, 
        minSizeFactor=0.1, size=metric/10)
    mdb.models[modelName].parts[partName].generateMesh()
    # assegnazione della sezione
    mdb.models[modelName].parts[partName].SectionAssignment(offset=0.0, 
        offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
        cells=mdb.models[modelName].parts[partName].cells),
        sectionName='Section-bolt', thicknessAssignment=FROM_SECTION)

def bolt_wizard(point1, point2, metric, boltClass, contactFlag, adjustLengthFlag):
    modelName = getCurrentModel()
    coordPoint1 = np.array(point1.pointOn)
    coordPoint2 = np.array(point2.pointOn)
    # calcolo altezza libera e correzione per il nome
    height = np.linalg.norm(coordPoint1-coordPoint2)
    height_str = f'{height:.6f}'
    while height_str[-1]=='0' and '.' in height_str:
        height_str = height_str[:-1]
    if height_str[-1]=='.':
        height_str = height_str[:-1]
    height = float(height_str)
    # check esistenza bolt
    partName = namePrefix + str(metric).replace('.', '_') + 'x' + height_str.replace('.', '_')
    if partName not in mdb.models[modelName].parts.keys():
        bolt_builder(modelName=modelName, metric=metric, height=height)
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
    # # calcolo dei delta e salvataggio punto2
    deltas = [np.linalg.norm(coordPoint2-np.array(ii)) for ii in coordDatumPoints]
    datumPoint2 = mdb.models[modelName].rootAssembly.datums[keysDatumPoints[deltas.index(min(deltas))]]
    # creazione del datum axis
    mdb.models[modelName].rootAssembly.DatumAxisByTwoPoint(
        point1=datumPoint1, point2=datumPoint2)
    axisKey = mdb.models[modelName].rootAssembly.datums.keys()[-1]
    # constrain punto
    mdb.models[modelName].rootAssembly.CoincidentPoint(fixedPoint= datumPoint1, movablePoint=
        mdb.models[modelName].rootAssembly.instances[instanceName].datums[1])
    # constrain asse
    mdb.models[modelName].rootAssembly.EdgeToEdge(fixedAxis=
        mdb.models[modelName].rootAssembly.datums[axisKey], flip=OFF, movableAxis=
        mdb.models[modelName].rootAssembly.instances[instanceName].datums[1])
    # eventuale flip del constrain
    distanza = np.linalg.norm(coordPoint2 - np.array(mdb.models[modelName].rootAssembly.instances[instanceName].vertices[verticiIdx[1]].pointOn))
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
        kBolt = 210000*pi*metric**2/4/height
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