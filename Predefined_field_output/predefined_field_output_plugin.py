from abaqusGui import getAFXApp, Activator, AFXMode
from abaqusConstants import ALL
import os
thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
toolset.registerGuiMenuButton(
    buttonText='Predefined field output', 
    object=Activator(os.path.join(thisDir, 'predefined_field_outputDB.py')),
    kernelInitString='import Predefined_output',
    messageId=AFXMode.ID_ACTIVATE,
    icon=None,
    applicableModules=('Step',),
    version='N/A',
    author='N/A',
    description='N/A',
    helpUrl='N/A'
)
