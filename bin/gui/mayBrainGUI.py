# -*- coding: utf-8 -*-
"""

GUI for Maybrain

"""

# add the local path to python executable path
import sys
try:
    sys.path.append("/home/galileo/Dropbox/Share/maybrain/august 2014 dev/dev2-2")
except:
    pass

from pyface.qt import QtGui, QtCore
from numpy import log10
import maybrain as mb
import mayBrainUI as ui
from os import path

app = QtGui.QApplication.instance()

class mayBrainGUI(QtGui.QMainWindow):
    def __init__(self, parent=None):
#        app=QtGui.QApplication([])  # is this required to get it working properly?
#        app.exec_()
        
        QtGui.QMainWindow.__init__(self, parent)
        # set up UI
        self.ui = ui.Ui_Maybrain()
        self.ui.setupUi(self)
        self.ui.adjPlot.setEnabled(0)
        self.ui.skullPlot.setEnabled(0)

        # set up function
        self.brains = {} # dictionary to hold brain objects
        self.plot = mb.plotObj() # start plot object
        self.highlights = {} # dictionary of highlights, each entry contains [brainName, highlightName]
        
        # link up buttons and functions
        self.connectSlots()
        
        # plot selected in ui.plotTree
        self.selectedPlot = None
        
        # local variables
        self.lastFolder = None # last folder viewed by user
        self.brainName = ['brain', 0] # used to auto-create labels for brains if no user input given (currently only supports 1 brain)
            
        
    def connectSlots(self):
        ''' connect buttons and functions '''

        # quit app        
        QtCore.QObject.connect(self.ui.quitButton, QtCore.SIGNAL('clicked()'), app.quit)
        
        # tab 1: general settings
        QtCore.QObject.connect(self.ui.spatialFnameButton, QtCore.SIGNAL('clicked()'), self.getSpatialFilename)
        QtCore.QObject.connect(self.ui.adjFnameButton, QtCore.SIGNAL('clicked()'), self.getAdjFilename)
        QtCore.QObject.connect(self.ui.skullFnameButton, QtCore.SIGNAL('clicked()'), self.getSkullFilename)
        QtCore.QObject.connect(self.ui.propsFnameButton, QtCore.SIGNAL('clicked()'), self.getPropsFilename)                
        QtCore.QObject.connect(self.ui.brainLoad, QtCore.SIGNAL('clicked()'), self.loadBrain)
        QtCore.QObject.connect(self.ui.skullLoad, QtCore.SIGNAL('clicked()'), self.loadSkull)
        QtCore.QObject.connect(self.ui.skullPlot, QtCore.SIGNAL('clicked()'), self.plotSkull)
        QtCore.QObject.connect(self.ui.plotTree, QtCore.SIGNAL('itemClicked(QTreeWidgetItem*,int)'), self.setPlotValues)
        self.ui.opacitySlider.valueChanged.connect(self.setOpacity)
        self.ui.opacityBox.valueChanged.connect(self.setOpacityBox)
        self.ui.visibleCheckBox.clicked.connect(self.setVisibility)
        self.ui.redSlider.valueChanged.connect(self.setColourRed)
        self.ui.redValueBox.valueChanged.connect(self.setColourRedDial)
        self.ui.greenSlider.valueChanged.connect(self.setColourGreen)
        self.ui.greenValueBox.valueChanged.connect(self.setColourGreenDial)
        self.ui.blueSlider.valueChanged.connect(self.setColourBlue)
        self.ui.blueValueBox.valueChanged.connect(self.setColourBlueDial)
        self.ui.hlApplyButton.clicked.connect(self.makeHighlight)
        self.ui.propsLoad.clicked.connect(self.addProperties)
        
        
#        QtCore.QObject.connect(self.ui.opacitySlider, QtCore.SIGNAL('mouseReleaseEvent()'), self.setOpacity)
        
        
    ## =============================================

    ## Functions to connect slots and Maybrain function
        
    # Basic info, files and loading
    def getSpatialFilename(self):
        ''' open a dialog to get the spatial filename'''
        f = QtGui.QFileDialog.getOpenFileName(self, 'Choose spatial file', directory = self.lastFolder)
        self.ui.spatialFilename.setText(f)
        self.lastFolder = path.dirname(f)
        
    def getAdjFilename(self):
        ''' open a dialog to get the adjacency filename '''
        f = QtGui.QFileDialog.getOpenFileName(self, 'Choose adjacency file', directory = self.lastFolder)
        self.ui.adjFilename.setText(f)
        self.lastFolder = path.dirname(f)
        
    def getSkullFilename(self):
        ''' get a skull filename '''
        f = QtGui.QFileDialog.getOpenFileName(self, 'Choose skull file', directory = self.lastFolder)
        self.ui.skullFilename.setText(f)
        self.lastFolder = path.dirname(f)
        
    def getPropsFilename(self):
        f = QtGui.QFileDialog.getOpenFileName(self, 'Choose properties file', directory = self.lastFolder)
        self.ui.propsFilename.setText(f)
        self.lastFolder = path.dirname(f)
        
    def findBrainName(self, brainName = None):
        ''' construct a new brain name if necessary '''
        if brainName:
            boolOut = brainName in self.brains
        else:
            brainName = self.brainName[0] + str(self.brainName[1])
            boolOut = 0
            
        # returns the name and whether the name has already been used to label a brain
        return brainName, boolOut
        
    def loadBrain(self):
        ''' load a brain using given filenames '''
        self.ui.adjPlot.setEnabled(False)        
        
        # get adjacency filename
        adj = str(self.ui.adjFilename.text())
        # get threshold
        thold = float(self.ui.thresholdValue.text())
        # get spatial info file
        coords = str(self.ui.spatialFilename.text())
        
        # **** can add an option here for user-defined name ****

        # make name for brain
        brName, brainUsedBool = self.findBrainName()
        
        # create and add to list of brains
        if brainUsedBool:
            # case where brain name exists already
            # get brain object
            br = self.brains[brName]
            
            # update properties
            br.inputAdjFile(adj)
            br.inputSpatialInfo(coords)
            br.applythreshold(tVal=thold)
        
        else:
            # make and save brain
            br = mb.loadAndThreshold(adj, coords, thold)
            self.brains[brName] = br
        # add to box for subplotting
#        self.ui.subPlotBrain.addItem(brName)
            
        # enable plot button
        try:
            QtCore.QObject.disconnect(self.ui.adjPlot, QtCore.SIGNAL('clicked()'), self.rePlotBrain)
        except:
            pass
        QtCore.QObject.connect(self.ui.adjPlot, QtCore.SIGNAL('clicked()'), self.plotBrain)
        self.ui.adjPlot.setEnabled(True)
     
        
    def loadSkull(self):
        ''' load a skull file '''
        # get filename
        f = str(self.ui.skullFilename.text())
        # get brain name
        brainName, brUsedBool = self.findBrainName()
    
        # create brain object if it doesn't exist
        if not(brUsedBool):
            br = mb.brainObj()
            self.brains[brainName] = br
        else:
            br = self.brains[brainName]
        # read in file
        br.importSkull(f)
        
        # enable plot button
        self.ui.skullPlot.setEnabled(True)
        

    ## =============================================
    
    ## plotting functions
    
    def plotBrain(self):
        ''' plot the entire brain object '''
        
        # sort label for brain object
        label, labelUsedBool = self.findBrainName()

        # plot the brain
        try:            
            # plot the brain (excluding highlights)
            self.plot.plotBrainBase(self.brains[label], opacity = 0.2, edgeOpacity = None, label=label)

        except:
            print('problem plotting brain, have files been loaded?')

        # add to tree view
        self.readAvailablePlots() 
            
        # change plot button to replot
        QtCore.QObject.disconnect(self.ui.adjPlot, QtCore.SIGNAL('clicked()'), self.plotBrain)
        QtCore.QObject.connect(self.ui.adjPlot, QtCore.SIGNAL('clicked()'), self.rePlotBrain)
    
    
    def rePlotBrain(self):
        ''' plot brain with altered threhold '''        
        
        # get brain ***NEEDS CHANGING FOR MULTIPLE BRAINS***
        brName, nameUsedBool = self.findBrainName()
        
        if not(brName in self.brains):
            print(brName + ' not found in rePlot')
            return

        # remove old plots
        print('\n')
        for p in self.plot.brainEdgePlots:
            print(p)
        self.plot.brainEdgePlots[brName].remove()
        self.plot.brainNodePlots[brName].remove()
            
#        try:
        # get new threshold
        threshold = float(self.ui.thresholdValue.text())
        # replot
        br = self.brains[brName]
        br.applyThreshold(tVal = threshold)
        
        # *** need to get existing opacity value ***
        self.plot.plotBrainBase(br, label = brName)       
#        except:
#            print('problem plotting brain, is threshold correct?')
        self.readAvailablePlots()
            
            
    def plotSkull(self):
        ''' plot the skull '''
        
        # check if brain object exists
        if not('mainBrain' in self.brains):
            return
            
        # plot
        try:
            self.plot.plotSkull(self.brains['mainBrain'], label = 'skull')
            
            # add to treeview
            self.readAvailablePlots()
            # QtGui.QTreeWidgetItem(self.ui.plotTree, ['skull', 'skull'])     
            
        except:
            print('could not plot skull, has file been loaded?')
         
        
        
    def readAvailablePlots(self):
        ''' read in the available plots from the plotting object '''
        
        # clear current values
        self.ui.plotTree.clear()
        
        # add new values
        lists = [self.plot.brainEdgePlots, self.plot.brainNodePlots, self.plot.skullPlots, self.plot.isosurfacePlots]
        labels = ['edges', 'nodes', 'skull', 'isosurf']
        
        for ls in range(len(lists)):
            names = lists[ls].keys()
            names.sort()
            lab = labels[ls]
            for p in names:
                QtGui.QTreeWidgetItem(self.ui.plotTree, [lab, p])
        
#        for p in self.plot.brainEdgePlots:
#            QtGui.QTreeWidgetItem(self.ui.plotTree, ['brainEdge', p])
#        for p in self.plot.brainNodePlots:            
#            QtGui.QTreeWidgetItem(self.ui.plotTree, ['brainNode', p]) 
#        for s in self.plot.skullPlots:
#            QtGui.QTreeWidgetItem(self.ui.plotTree, ['skull', s])
#        for s in self.plot.isosurfacePlots:
#            QtGui.QTreeWidgetItem(self.ui.plotTree, ['isosurf', s])


    ## =============================================
    
    ## Highlight functions
    
    def makeHighlight(self):
        ''' make a highlight using settings from ui '''
        
        # get current brain object
        # *** needs changing to make flexible ***
        brName, nameUsedBool = self.findBrainName()
        br = self.brains[brName]        
        
        # get settings from ui
        propName = str(self.ui.hlProp.currentText())
        relation = self.getRelation()
        try:
            val1 = float(self.ui.hlValue1.text())
        except:
            val1 = str(self.ui.hlValue1.text())
        try:
            val2 = float(self.ui.hlValue2.text())
        except:
            val2 = str(self.ui.hlValue2.text())
        # *** should change the name to hlName ***
        label = str(self.ui.subPlotName.text())
        # NEEDS MODIFICATION
        if label=='':
            label = 'highlight1'
        mode = str(self.ui.hlNodesOrEdgesBox.currentText())
        # remove 's' from edge of mode
        mode = mode[:-1]
        red = float(self.ui.hlRedSpin.value())        
        green = float(self.ui.hlGreenSpin.value())
        blue = float(self.ui.hlBlueSpin.value())
        # *** maybe change to a box??
        opacity = float(self.ui.hlOpacityValue.text())
        
        # get value correct
        if relation in ['in()', 'in[)', 'in(]', 'in[]']:
            val = [val1, val2]
        else:
            val = val1
        
        # create the highlight object
        br.highlightFromConds(propName, relation, val, label=label, mode=mode, colour = (red, green, blue), opacity=opacity)
        
        # plot        
        self.plot.plotBrainHighlights(br, highlights=[label])          
        
        # add to list of plots
        self.readAvailablePlots()
        
        
    def getRelation(self):
        ''' retrieve information from the relation-box and translate into maybraintools language '''
        # get current value
        val = str(self.ui.hlRelationBox.currentText())
        
        # translate        
        if val=='=':
            outval = 'eq'
        elif val=='<':
            outval = 'lt'
        elif val=='>':
            outval = 'gt'
        elif val=='<=':
            outval = 'leq'
        elif val=='>=':
            outval = 'geq'
        elif val=='contains text':
            outval = 'contains'
        else:
            # covers cases in + 2 brackets
            outval = val
        
        return outval
    
#    def plotHighlight(self):
#        ''' plot the selected highlight '''
#        # Get highlight name
##        brainName, hlName = 
#        
#        # Do the plot
#        self.plot.plotHighlights(self.br[brainName], highlights=[hlName])
#        
#        QtGui.QTreeWidgetItem(self.ui.plotTree, ['brainNode', label])
#        QtGui.QTreeWidgetItem(self.ui.plotTree, ['brainEdge', label])

        
    ## =============================================
    
    ## setting and altering plot properties e.g. visibility, opacity
    
    def addProperties(self):
        ''' add properties to a brain from file '''
        
        # get properties filename from GUI
        fname = str(self.ui.propsFilename.text())        
        
        # find the active brain (doesn't allow multiple brains currently)
        brain = 'brain0'
        
        # call function from mayBrainTools to add properties to brain
        nodesOrEdges, prop = self.brains[brain].importProperties(fname)
        
        # add to plot properties box
        self.ui.hlProp.addItem(str(prop))
             
    
    def setPlotValues(self, item):
        ''' update all values for sliders and stuff of a specific plot '''
        
        # set the selected plot
        self.selectedPlot = str(item.text(1))
        self.selectedPlotType = str(item.text(0))
        
        # set values related to plot on sliders
        props = ['opacity', 'visibility', 'colour']
        
        for p in props:
            # get the property
            v = self.plot.getPlotProperty(self.selectedPlotType, p, self.selectedPlot)
            
            # pass values to gui
            if p == 'visibility':
                if v == 1:
                    v = 2
                self.ui.visibleCheckBox.setCheckState(v)
            elif p == 'opacity':
                v = log10(9.*v+1.)*100.
                print(v)
                self.ui.opacitySlider.setValue(v)
            elif p == 'colour':
                self.ui.redSlider.setValue(v[0]*100)
                self.ui.redValueBox.setValue(v[0])
                self.ui.greenSlider.setValue(v[1]*100)
                self.ui.greenValueBox.setValue(v[1])
                self.ui.blueSlider.setValue(v[2]*100)
                self.ui.blueValueBox.setValue(v[2])
                
                
    def setOpacity(self):
        ''' set the opacity for the currently selected plot from the slider '''

        v = float(self.ui.opacitySlider.value())
        v = (10**(v/100.)-1.)/9.
        # update value in box
        self.ui.opacityBox.setValue(v)
        # update plot
        self.plot.changePlotProperty(self.selectedPlotType, 'opacity', self.selectedPlot, v)
        

    def setOpacityBox(self):
        ''' set the opacity from a box '''
        
        v = self.ui.opacityBox.value()
        # set value in slider
        vs = log10(9.*v+1.)*100.
        self.ui.opacitySlider.setValue(vs)
        # change value in plot
        self.plot.changePlotProperty(self.selectedPlotType, 'opacity', self.selectedPlot, v)

        
    def setVisibility(self):
        ''' toggle visibility from checkbox '''        
        
        v = self.ui.visibleCheckBox.checkState()
        if v==0:
            v=False
        elif v==2:
            v = True
        self.plot.changePlotProperty(self.selectedPlotType, 'visibility', self.selectedPlot, value = v)
        
    def setColourRed(self):
        ''' change colours from sliders '''     
        # get old values
        v = self.plot.getPlotProperty(self.selectedPlotType, 'colour', self.selectedPlot)        
        # get new red value
        r = float(self.ui.redSlider.value()) * 0.01
        v1 = (r, v[1], v[2])        
        # change value in plot
        self.plot.changePlotProperty(self.selectedPlotType, 'colour', self.selectedPlot, value = v1)        
        # set dial value
        self.ui.redValueBox.setValue(r)
        
    def setColourRedDial(self):
        ''' change red colour from dial '''
        # get old values
        v = self.plot.getPlotProperty(self.selectedPlotType, 'colour', self.selectedPlot)
        # get new red value
        r = self.ui.redValueBox.value()
        v1 = (r, v[1], v[2])        
        # change value in plot
        self.plot.changePlotProperty(self.selectedPlotType, 'colour', self.selectedPlot, value = v1)        
        # set slider value
        self.ui.redSlider.setValue(int(r*100.))
        

    def setColourGreen(self):
        ''' change colours from sliders '''        
        # get old values
        v = self.plot.getPlotProperty(self.selectedPlotType, 'colour', self.selectedPlot)        
        # get new green value
        g = float(self.ui.greenSlider.value()) * 0.01
        v1 = (v[0], g, v[2])        
        # change value in plot
        self.plot.changePlotProperty(self.selectedPlotType, 'colour', self.selectedPlot, value = v1)        
        # set dial value
        self.ui.greenValueBox.setValue(g)
        
    def setColourGreenDial(self):
        ''' change green colour from dial '''
        # get old values
        v = self.plot.getPlotProperty(self.selectedPlotType, 'colour', self.selectedPlot)
        # get new green value
        g = self.ui.greenValueBox.value()
        v1 = (v[0], g, v[2])        
        # change value in plot
        self.plot.changePlotProperty(self.selectedPlotType, 'colour', self.selectedPlot, value = v1)        
        # set slider value
        self.ui.greenSlider.setValue(int(g*100.))
        
    def setColourBlue(self):
        ''' change colours from sliders '''        
        # get old values
        v = self.plot.getPlotProperty(self.selectedPlotType, 'colour', self.selectedPlot)        
        # get new blue value
        b = float(self.ui.blueSlider.value()) * 0.01
        v1 = (v[0], v[1], b)        
        # change value in plot
        self.plot.changePlotProperty(self.selectedPlotType, 'colour', self.selectedPlot, value = v1)        
        # set dial value
        self.ui.blueValueBox.setValue(b)
        
    def setColourBlueDial(self):               
        ''' change blue colour from dial '''
        # get old values
        v = self.plot.getPlotProperty(self.selectedPlotType, 'colour', self.selectedPlot)
        # get new blue value
        b = self.ui.blueValueBox.value()
        v1 = (v[0], v[1], b) 
        # change value in plot
        self.plot.changePlotProperty(self.selectedPlotType, 'colour', self.selectedPlot, value = v1)        
        # set slider value
        self.ui.blueSlider.setValue(int(b*100.))
                

        
def runGui():
    # using instance allows Mayavi to run alongside without any problems.
    
    ex = mayBrainGUI()
    ex.show()
    sys.exit(app.exec_())
    
    return(ex)


if __name__ == "__main__":

    runGui()