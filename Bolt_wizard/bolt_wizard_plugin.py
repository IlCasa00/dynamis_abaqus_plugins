from abaqusGui import getAFXApp, Activator, AFXMode
from abaqusConstants import ALL
import os
thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
toolset.registerGuiMenuButton(
    buttonText='Bolt wizard', 
    object=Activator(os.path.join(thisDir, 'bolt_wizardDB.py')),
    kernelInitString='import Bolt_wizard',
    messageId=AFXMode.ID_ACTIVATE,
    icon=None,
    applicableModules=('Assembly',),
    version='N/A',
    author='N/A',
    description='N/A',
    helpUrl='N/A'
)
