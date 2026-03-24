from abaqusGui import getAFXApp, Activator, AFXMode
from abaqusConstants import ALL
import os
thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
toolset.registerGuiMenuButton(
    buttonText='Instance replace custom', 
    object=Activator(os.path.join(thisDir, 'instance_replace_customDB.py')),
    kernelInitString='import Instance_replace_custom',
    messageId=AFXMode.ID_ACTIVATE,
    icon=None,
    applicableModules=('Assembly',),
    version='N/A',
    author='N/A',
    description='N/A',
    helpUrl='N/A'
)
