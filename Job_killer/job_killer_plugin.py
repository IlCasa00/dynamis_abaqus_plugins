from abaqusGui import getAFXApp, Activator, AFXMode
from abaqusConstants import ALL
import os
thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
toolset.registerGuiMenuButton(
    buttonText='Job killer', 
    object=Activator(os.path.join(thisDir, 'job_killerDB.py')),
    kernelInitString='import Job_killer',
    messageId=AFXMode.ID_ACTIVATE,
    icon=None,
    applicableModules=('Job',),
    version='N/A',
    author='N/A',
    description='N/A',
    helpUrl='N/A'
)
