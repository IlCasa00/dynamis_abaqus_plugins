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

def getCurrentPart():
    """
    Ritorna una stringa contenente il nome della parte attualmente
    attiva nel viewport
    """
    return session.viewports[session.currentViewportName].displayedObject.name

def getCentroid(elemento):
    sumCoords = np.array([0.,0.,0.])
    for ii in elemento.getNodes():
        sumCoords += np.array(ii.coordinates)
    return list(sumCoords/len(elemento.connectivity))

def getSymPoint(point, plane_point, normal):
    point = np.array(point, dtype=float)
    plane_point = np.array(plane_point, dtype=float)
    normal = np.array(normal, dtype=float)
    v = point - plane_point
    dist = np.dot(v, normal) / np.dot(normal, normal)
    reflected_point = point - 2 * dist * normal
    return list(reflected_point)

def mirrorConn(indici, associative):
    """
    Dandogli in pasto la lista di connetticita' di un elemento hex
    sia esso lineare o quadratico
    e la lista di associativita' speculare dei nodi ritona la lista
    di associativita' dell'elemento simmetrico.
    La lista di associativita' speculare e' una lista di liste
    dove goni sottolista e' composta dall'indice del nodo originale
    e l'indice del nodo slave specchiato.
    I nodi sul piano di simmetria sono master di se stessi, a meno che
    non si volgiano duplicare volontariamente.
    """
    nuoviIndici = [associative[ii] for ii in indici]
    if len(nuoviIndici)==8:
        nuoviIndici = nuoviIndici[4:] + nuoviIndici [:4]
    else:
        nuoviIndici = nuoviIndici[4:8] + nuoviIndici [:4] + nuoviIndici[12:16] + nuoviIndici[8:12] + nuoviIndici[16:]
    return tuple(nuoviIndici)

def symHexMesh(mirrorFaces, assocFlag):
    #mirrorFaces = mdb.models['Model-1'].parts['Part-1'].sets['Set-1'].faces
    modelName = getCurrentModel()
    partName = getCurrentPart()
    parte = mdb.models[modelName].parts[partName]
    elementi = parte.elements
    nElems = len(elementi)
    nEdges = len(parte.elementEdges)
    nodi = parte.nodes
    nodeLabels = [ii.label for ii in nodi]
    normSymPlane = mirrorFaces[0].getNormal()
    pointSymPlane = mirrorFaces[0].pointOn[0]
    # nodi sulla faccia di simmetria
    symPlaneNodes = []
    for faccia in mirrorFaces:
        modelFace = parte.faces.findAt(faccia.pointOn[0])
        symPlaneNodes += [nodeLabels.index(ii.label) for ii in modelFace.getNodes() if ii.label not in symPlaneNodes]
    nonSymPlaneNodes = [ii for ii in list(range(len(nodi))) if ii not in symPlaneNodes]
    # dict con label dei nodi originali e quelli nuovi
    labelCounter = len(nodi)
    assocLabels = {}
    for nodo in symPlaneNodes:
        assocLabels.update({nodo: nodo})
    # creazione dei nodi
    for indiceNodo in nonSymPlaneNodes:
        nodo = nodi[indiceNodo]
        coordinata = getSymPoint(nodo.coordinates, pointSymPlane, normSymPlane)
        mdb.models[modelName].parts[partName].Node(coordinata)
        assocLabels.update({indiceNodo: labelCounter})
        labelCounter += 1
    # creazione elementi
    for elementoIdx in range(nElems):
        connessioni = mirrorConn(elementi[elementoIdx].connectivity, assocLabels)
        connNodes = tuple([mdb.models[modelName].parts[partName].nodes[ii] for ii in connessioni])
        if len(connNodes)==8:
            tipo = HEX8
        elif len(connNodes)==20:
            tipo = HEX20
        # elif len(connNodes)==4:
        #     tipo = TET4
        # elif len(connNodes)==10:
        #     tipo = TET10
        mdb.models[modelName].parts[partName].Element(nodes=connNodes, elemShape=tipo)
    if assocFlag:
        # assoc celle
        cellElems = {}
        # ciclaggio degli elementi per vedere a che celle appartengono
        elemCounter = 0
        for elemento in mdb.models[modelName].parts[partName].elements[nElems:]:
            # calcolo centroide
            centroide = getCentroid(elemento)
            # check centroide in cella
            if cella:=mdb.models[modelName].parts[partName].cells.findAt(centroide):
                # check esistenza dict
                if (cellIdx:=cella.index) not in cellElems.keys():
                    # creazione dict
                    cellElems.update({cellIdx: []})
                # aggiunta indice lista elemento al dict
                cellElems[cellIdx].append(elemCounter+nElems)
            # aggiornamento counter
            elemCounter += 1
        # associazione degli elementi alle celle
        for cellKey in cellElems.keys():
            # conversione della cella in bottomup
            mdb.models[modelName].parts[partName].setMeshControls(regions=
                    mdb.models[modelName].parts[partName].cells[cellKey:cellKey+1], technique=BOTTOM_UP)
            # creaizone della geom sequence degli elementi
            sequenzaElementi = mdb.models[modelName].parts[partName].elements[cellElems[cellKey][0]:cellElems[cellKey][0]+1]
            for ii in cellElems[cellKey][1:]:
                sequenzaElementi += mdb.models[modelName].parts[partName].elements[ii:ii+1]
            # associazione
            mdb.models[modelName].parts[partName].associateMeshWithGeometry(elements=
                sequenzaElementi, geometricEntity=mdb.models[modelName].parts[partName].cells[cellKey])
        # rigenerazione assieme
        mdb.models[modelName].rootAssembly.regenerate()
        # assoc facce
        # accesso con p.elementFaces ad un array like
        # col metodo .getNodes() ottengo lista di nodi
        # verificare che ogn nodo appartenga ad una faccia
        # media di coordinate per trovare centroide -> faces.getClosest()
        # salvataggio id facce in lista per gli edge come prima
        # trovo gli elementi candidati, ovvero quelli non originali
        elemCandidates = [ii.label for ii in mdb.models[modelName].parts[partName].elements[nElems:]]
        # salvataggio indici delle facce che appartengono ai candidati
        # non sono incluse le facce comuni agli elementi originali dato che sono gia associate
        # almeno riduco il numero di facce da controllare e riduco il loop
        facceElementi = mdb.models[modelName].parts[partName].elementFaces
        faceCandidates = [ii for ii in range(len(facceElementi)) if facceElementi[ii].label in elemCandidates]
        # dict per assoc faccia cad to faccia elem
        face2elFace = {}
        # lista degli indici delle facce elementi che si trovano su facce geoemtriche
        # mi serve per ridurre successivamente il ciclaggio sugli spigoli
        elFaceInterest = []
        # ciclaggio sulle facce degli elementi
        for candidato in faceCandidates:
            # controllo che i nodi si trovino sulla faccia e filtro con un flag
            onFaceFlag = True
            for nodo in facceElementi[candidato].getNodes():
                if onFaceFlag and not mdb.models[modelName].parts[partName].faces.findAt(nodo.coordinates):
                    onFaceFlag = False
            # se il flag è verificato allora aggiungo la faccia dell'elemento al dict
            # insieme all'indice della faccia cad piu vicina al centroide
            # il dict va aggiornato con indice faccia cad se non esiste
            if onFaceFlag:
                # calcolo centroide
                centroide = np.array([0.,0.,0.])
                for ii in facceElementi[candidato].getNodes():
                    centroide += np.array(ii.coordinates)
                
                centroide = list(centroide/len(facceElementi[candidato].getNodes()))
                # ricerca dell'indice faccia piu vicina al centroide
                faceIdx = mdb.models[modelName].parts[partName].faces.getClosest(coordinates=(centroide,))[0][0].index
                # se non eisste un dict con indice faccia trovata allora si aggiunge
                if faceIdx not in face2elFace.keys():
                    face2elFace.update({faceIdx:[]})
                # aggiunta dell'element face id al dict nella relativa faccia geometrica
                face2elFace[faceIdx].append(candidato)
                elFaceInterest.append(candidato)
        # associazione delle facce degli elementi alle facce geometriche
        for faceIdx in face2elFace.keys():
            # creaizone della sequence di facce elementi
            elFaces = mdb.models[modelName].parts[partName].elementFaces[face2elFace[faceIdx][0]:face2elFace[faceIdx][0]+1]
            for elFaceIdx in face2elFace[faceIdx][1:]:
                elFaces += mdb.models[modelName].parts[partName].elementFaces[elFaceIdx:elFaceIdx+1]
            # associazione
            mdb.models[modelName].parts[partName].associateMeshWithGeometry(elemFaces=
                elFaces, geometricEntity=mdb.models[modelName].parts[partName].faces[faceIdx])
        mdb.models[modelName].rootAssembly.regenerate()
        # assoc spigoli
        # metodo uguale a quello di prima
        # nota del giorno dopo: porco dio non e' vero mai
        # lista dei nodi associati a indici spigoli messi in sottoliste
        elEdgesIdx2nodeLabels = [[jj.label for jj in ii.getNodes()] for ii in mdb.models[modelName].parts[partName].elementEdges[nEdges:]]
        # compliaizone lista degli indici dei candidati 
        elEdgesIdxCandidates = []
        for elFaceId in elFaceInterest:
            spigoliFaccia = mdb.models[modelName].parts[partName].elementFaces[elFaceId].getElemEdges()
            for spigolo in spigoliFaccia:
                edgeNodeLabels = [ii.label for ii in spigolo.getNodes()]
                if edgeNodeLabels in elEdgesIdx2nodeLabels:
                    if (indiceSpigolo:=elEdgesIdx2nodeLabels.index(edgeNodeLabels)) not in elEdgesIdxCandidates:
                        elEdgesIdxCandidates.append(indiceSpigolo+nEdges)
        # a questo punto ho gli indici degli spigoli candidati
        # inizializzo il dict degli spigoli
        edge2elEdge = {}
        for elEdgeId in elEdgesIdxCandidates:
            # check nodi su spigolo geometrico
            coordNodiSpigolo = [ii.coordinates for ii in mdb.models[modelName].parts[partName].elementEdges[elEdgeId].getNodes()]
            onEdgeFlag = True
            for coordinata in coordNodiSpigolo:
                if onEdgeFlag and not mdb.models[modelName].parts[partName].edges.findAt(coordinata):
                    onEdgeFlag = False
            # se tutti i nodi si trovano su uno spigolo geometrico allora
            # trovo lo spigolo più vicino al centroide
            # aggiungo il suo id al dict associativo se non presente
            # e poi ci metto quindi l'id dello spigolo dell'elemento
            if onEdgeFlag:
                centroide = np.array(coordNodiSpigolo[0])/len(coordNodiSpigolo)
                for ii in coordNodiSpigolo[1:]:
                    centroide += np.array(ii)/len(coordNodiSpigolo)
                # ricerca dell'indice faccia piu vicina al centroide
                edgeIdx = mdb.models[modelName].parts[partName].edges.getClosest(coordinates=(list(centroide),))[0][0].index
                # se non eisste un dict con indice faccia trovata allora si aggiunge
                if edgeIdx not in edge2elEdge.keys():
                    edge2elEdge.update({edgeIdx:[]})
                # aggiunta dell'element face id al dict nella relativa faccia geometrica
                edge2elEdge[edgeIdx].append(elEdgeId)
        # associazione
        for edgeIdx in edge2elEdge.keys():
            # creaizone della sequence di facce elementi
            elEdges = mdb.models[modelName].parts[partName].elementEdges[edge2elEdge[edgeIdx][0]:edge2elEdge[edgeIdx][0]+1]
            for elEdgeIdx in edge2elEdge[edgeIdx][1:]:
                elEdges += mdb.models[modelName].parts[partName].elementEdges[elEdgeIdx:elEdgeIdx+1]
            # associazione
            mdb.models[modelName].parts[partName].associateMeshWithGeometry(elemEdges=
                elEdges, geometricEntity=mdb.models[modelName].parts[partName].edges[edgeIdx])
        # regen assieme
        mdb.models[modelName].rootAssembly.regenerate()