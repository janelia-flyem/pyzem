'''
Created on Sep 17, 2013

@author: zhaot
'''
import json;
import sys;
import os;

class MovieScene:
    def __init__(self, duration):
        self.scene = {"duration": duration};
        
    def addAction(self, scene, actorId, action):
        if "action" not in self.scene:
            self.scene["action"] = list();
        self.scene["action"].append(dict({"id": actorId}.items() + action.items()));        
        
class MovieScriptWriter:
    '''
    classdocs
    '''


    def __init__(self, script = {"cast": list(), "plot": list()}):
        '''
        Constructor
        '''
        self.script = script;
        self.rootPath = None
        
    def setRootPath(self, p):
        self.rootPath = p
        
    def write(self, scriptPath):
        outFile = open(scriptPath, "w");
        json.dump(self.script, outFile, indent = 2);
        outFile.close();
        
    def addActor(self, actorId, actorSource):
        if self.rootPath:
            actorSource = os.path.relpath(actorSource, self.rootPath)
        self.script["cast"].append({"id": actorId, "source": actorSource});

    def addScene(self, scene):
        if isinstance(scene, MovieScene):
            self.script["plot"].append(scene.scene);
        else:
            self.script["plot"].append(scene);
        
    def printToScreen(self):
        json.dump(self.script, sys.stdout, 2);
        
if __name__ == '__main__':
    scriptWriter = MovieScriptWriter();
    scriptWriter.addActor("test", "test.swc");
    scriptWriter.printToScreen();