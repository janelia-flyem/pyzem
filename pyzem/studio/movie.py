'''
Created on Jun 12, 2013

@author: zhaot
'''
from __future__ import print_function

def pauseScene(duration):
    return {"duration": duration};

def newScene(duration):
    return {"duration": duration};

def addActor(cast, actorId, actorSource):
    cast.append({"id": actorId, "source": actorSource});

def addAction(scene, actorId, action):
    if "action" not in scene:
        scene["action"] = list();
    scene["action"].append(dict({"id": actorId}.items() + action.items()));

if __name__ == '__main__':
    movieScript = {};
    movieScript["cast"] = list();
    addActor(movieScript["cast"], "test", "test.swc");
    addActor(movieScript["cast"], "test2", "test2.swc");
    scene = newScene(1000);
    addAction(scene, "test", {"color": [1, 0, 0], "move": [0, 0, 1]});
    print(movieScript);
    print(scene);