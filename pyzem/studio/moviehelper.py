'''
Created on Apr 11, 2016

@author: zhaot
'''

import os
import sys

import MovieScriptWriter as mw
import movie

class MovieHelper(object):
    '''
    classdocs
    '''

    def __init__(self, castDir, colorMap, neuronNameIdMap):
        '''
        Constructor
        '''
        self.castDir = castDir
        self.scriptWriter = mw.MovieScriptWriter()
        self.scriptWriter.setRootPath(castDir + "/..")
        self.colorMap = colorMap
        self.neuronNameIdMap = neuronNameIdMap
    
    def addNeuronActor(self, nameList):
        actorList = []
        for name in nameList:
            for neuronId in self.neuronNameIdMap[name]:
                filePath = self.castDir + "/" + neuronId + ".swc"
                if not os.path.isfile(filePath):
                    print "WARNING: no file for", name, "(" + neuronId + ")", "-", filePath
                else:
                    print name, "added"
                    actorList.append(neuronId)
                    self.scriptWriter.addActor(neuronId, filePath)
                    
                filePath = self.castDir + "/" + neuronId + ".marker"
                if os.path.isfile(filePath):
                    print name, "added"
                    markerId = neuronId + "_marker"
                    actorList.append(markerId)
                    self.scriptWriter.addActor(markerId, filePath)
                    
        return actorList

    def addNeuronScene(self, nameList, t, index):
        startIndex = index
        for name in nameList:
            if index - startIndex == len(nameList) - 1: #last element
                scene = movie.newScene(t + 500)
            else:
                scene = movie.newScene(t);
            scene["camera"] = {"rotate":  {"axis": [0.0, 1.0, 0.5], "angle": 0.02}}
            action = {"visible": True, "color": self.colorMap[index % len(self.colorMap)]}
            movie.addAction(scene, name, action)
            index += 1    
                                         
            self.scriptWriter.addScene(scene)
            
        return index
    
    def addNeuronOnceScene(self, nameList, t, index):
#         startIndex = index
        scene = movie.newScene(t);
        scene["camera"] = {"rotate":  {"axis": [0.0, 1.0, 0.5], "angle": 0.02}}
        for name in nameList:
            action = {"visible": True, "color": self.colorMap[index % len(self.colorMap)]}
            movie.addAction(scene, name, action)
            index += 1    
                                         
        self.scriptWriter.addScene(scene)
            
        return index
    
    def addFadingOutNeuronScene(self, nameList, t):
        for name in nameList:
            scene = self.movie.newScene(t);
            action = {"fade": -1.1 / t}
            movie.addAction(scene, name, action)
        
        scene["camera"] = {"rotate":  {"axis": [0.0, 1.0, 0.5], "angle": 0.02}}                    
        self.scriptWriter.addScene(scene)    
        
    def addHidingNeuronScene(self, nameList, t):
        scene = movie.newScene(t);
        for name in nameList:
            action = {"visible": False}
            movie.addAction(scene, name, action)
    #     scene["camera"] = {"rotate":  {"axis": [0.0, 1.0, 0.5], "angle": 0.02}}                    
        self.scriptWriter.addScene(scene)   
    
    def addShowingNeuronScene(self, nameList, t):
        scene = movie.newScene(t);
        for name in nameList:
            action = {"visible": True}
            movie.addAction(scene, name, action)
    #     scene["camera"] = {"rotate":  {"axis": [0.0, 1.0, 0.5], "angle": 0.02}}                    
        scene["camera"] = {"rotate":  {"axis": [0.0, 1.0, 0.5], "angle": 0.02}}
        self.scriptWriter.addScene(scene)
