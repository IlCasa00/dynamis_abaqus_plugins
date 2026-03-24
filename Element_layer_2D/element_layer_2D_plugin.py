from abaqusGui import getAFXApp, Activator, AFXMode
from abaqusConstants import ALL
import os
thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
toolset.registerGuiMenuButton(
    buttonText='Element layer 2D', 
    object=Activator(os.path.join(thisDir, 'element_layer_2DDB.py')),
    kernelInitString='import Element_layer_2D',
    messageId=AFXMode.ID_ACTIVATE,
    icon=None,
    applicableModules=['Part', 'Assembly', 'Mesh',],
    version='N/A',
    author='N/A',
    description='N/A',
    helpUrl='N/A'
)
