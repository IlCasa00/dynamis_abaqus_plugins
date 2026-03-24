from abaqusGui import getAFXApp, Activator, AFXMode
from abaqusConstants import ALL
import os
thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
toolset.registerGuiMenuButton(
    buttonText='Bearing load', 
    object=Activator(os.path.join(thisDir, 'bearing_loadDB.py')),
    kernelInitString='import Bearing_load',
    messageId=AFXMode.ID_ACTIVATE,
    icon=None,
    applicableModules=('Load',),
    version='N/A',
    author='N/A',
    description='N/A',
    helpUrl='N/A'
)
