"""
Display the Lightpath UI with the python IOC running in the background
"""
############
# Standard #
############
import logging

###############
# Third Party #
###############
import pydm

##########
# Module #
##########
import lightpath.tests
from lightpath.ui import LightApp
from lightpath.controller import LightController

logger = logging.getLogger('lightpath')


def main():
    #Gather devices
    cntrl = LightController(lightpath.tests.lcls_client())
    #Create Application
    app   = pydm.PyQt.QtGui.QApplication([])
    #Create Lightpath
    light = LightApp(cntrl)
    light.show()
    #Execute 
    app.exec_()

if __name__ == '__main__':
    main()

