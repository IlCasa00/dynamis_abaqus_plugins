from abaqusGui import getAFXApp, Activator, AFXMode
from abaqusConstants import ALL
import os
thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
toolset.registerGuiMenuButton(
    buttonText='Copy layup', 
    object=Activator(os.path.join(thisDir, 'copy_layupDB.py')),
    kernelInitString='import Copy_layup',
    messageId=AFXMode.ID_ACTIVATE,
    icon=None,
    applicableModules=('Property',),
    version='N/A',
    author='N/A',
    description='N/A',
    helpUrl='N/A'
)
