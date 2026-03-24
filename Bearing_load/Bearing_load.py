from part import *
from material import *
from section import *
from optimization import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *
from abaqusConstants import *
from abaqus import *
from regionToolset import Region
def bearing_load(loadName, modelName, stepName, setName, cylCsys, radialForce, faceRadius, faceHeight):
    # Creazione del field analitico
    fieldName = loadName+'_field'
    espressione = f'sin( Th )*2/({faceRadius}*{faceHeight}*pi)'
    mdb.models[modelName].ExpressionField(description='', expression=espressione, 
    localCsys=cylCsys, name=fieldName)
    if mdb.models[modelName].rootAssembly.sets[setName].faces:
        # Creazione del carico su faccia
        mdb.models[modelName].Pressure(amplitude=UNSET, createStepName=stepName, 
        distributionType=FIELD, field=fieldName, magnitude=radialForce, name=loadName, region=Region(side1Faces=mdb.models[modelName].rootAssembly.sets[setName].faces))
    else:
        # Creazione del carico su spigolo
        mdb.models[modelName].Pressure(amplitude=UNSET, createStepName=stepName, 
        distributionType=FIELD, field=fieldName, magnitude=radialForce, name=loadName, region=Region(side1Edges=mdb.models[modelName].rootAssembly.sets[setName].edges))