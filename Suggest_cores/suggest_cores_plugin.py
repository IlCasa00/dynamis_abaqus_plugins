from abaqusGui import getAFXApp, Activator, AFXMode
from abaqusConstants import ALL
import os
thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
toolset.registerGuiMenuButton(
    buttonText='Suggest cores', 
    object=Activator(os.path.join(thisDir, 'suggest_coresDB.py')),
    kernelInitString='import Suggest_cores',
    messageId=AFXMode.ID_ACTIVATE,
    icon=None,
    applicableModules=('Job',),
    version='N/A',
    author='N/A',
    description='N/A',
    helpUrl='N/A'
)
