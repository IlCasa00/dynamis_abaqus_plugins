from abaqusGui import getAFXApp, Activator, AFXMode
from abaqusConstants import ALL
import os
thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
toolset.registerGuiMenuButton(
    buttonText='Symmetric hex mesh', 
    object=Activator(os.path.join(thisDir, 'symmetric_hex_meshDB.py')),
    kernelInitString='import HexSymMesh',
    messageId=AFXMode.ID_ACTIVATE,
    icon=None,
    applicableModules=('Mesh',),
    version='N/A',
    author='N/A',
    description='N/A',
    helpUrl='N/A'
)
