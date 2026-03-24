from abaqusGui import getAFXApp, Activator, AFXMode
from abaqusConstants import ALL
import os
thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
toolset.registerGuiMenuButton(
    buttonText='Lag screw wizard', 
    object=Activator(os.path.join(thisDir, 'lag_screw_wizardDB.py')),
    kernelInitString='import Lag_screw_wizard',
    messageId=AFXMode.ID_ACTIVATE,
    icon=None,
    applicableModules=('Assembly',),
    version='N/A',
    author='N/A',
    description='N/A',
    helpUrl='N/A'
)
