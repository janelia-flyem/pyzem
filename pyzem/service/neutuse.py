from bottle import route, run, get, post, request, static_file, abort, hook, response
from pyzem.dvid import dvidenv, dvidio
from pyzem.compute import skeletonizer, bodysplit
import flyem_data as fd

import json
import subprocess
import sys
import socket
import jsonschema
import os
import time
import threading
import datetime
import copy
import yaml
import argparse
from queue import *

parser = argparse.ArgumentParser(description='Process arguments for running neutu service')
parser.add_argument('--config', dest='config', type=str, help='Configuration file in YAML format')
args=parser.parse_args()
print(args.config)

if not args.config:
    args.config = '/Users/zhaot/Work/neutube/neurolabi/python/service/test.yaml'
    
with open(args.config, 'r') as fp:
    serverConfig = yaml.load(fp)
    print(serverConfig)

skl = skeletonizer.Skeletonizer()
bs = bodysplit.BodySplit()

if 'command' in serverConfig:
    command = serverConfig['command']
    skl.setExecutable(command)
    bs.set_neutu_path(command)

if 'task_server' in serverConfig:
    bs.load_server(serverConfig['task_server'])
    
# print(bs.get_env())
# bs.clear_split_task()
# exit(1)
    
socket.setdefaulttimeout(1000)

dvidEnvMap = {}
eventQueue = Queue()
#eventLock = Lock()
dvidWriter = dvidio.DvidClient()

def processEvent(event):
    print("Processing event ...")
    print(event.dvidEnv)
    dvidWriter.set_dvidenv(event.dvidEnv)
    if event.getType() == fd.DataEvent.DATA_INVALIDATE:
        if event.getDataId().getType() == fd.DataId.DATA_BODY:
            print("Invalidating body", event.getDataId().getBodyId())
            dvidWriter.delete_skeleton(event.getDataId().getBodyId())
            dvidWriter.delete_thumbnail(event.getDataId().getBodyId())
    elif event.getType() == fd.DataEvent.DATA_DELETE:
        if event.getDataId().getType() == fd.DataId.DATA_BODY:
            print("Deleting body data", event.getDataId().getBodyId())
            dvidWriter.delete_skeleton(event.getDataId().getBodyId())
            dvidWriter.delete_thumbnail(event.getDataId().getBodyId())
            dvidWriter.delete_body_annotation(event.getDataId().getBodyId())
    elif event.getType() == fd.DataEvent.DATA_UPDATE:
        time.sleep(5)
        if event.getDataId().getType() == fd.DataId.DATA_SKELETON:
            print("Skeletionzing body", event.getDataId().getBodyId(), event.dvidEnv)
            skl.setDvidEnv(event.dvidEnv)
            print(skl.getDvidEnv())
            skl.skeletonize(event.getDataId().getBodyId())
            
def process():
    eqcopy =  []
    while True:
        try:
            elem = eventQueue.get(block=False)
        except Empty:
            break
        else:
            eqcopy.append(elem)

    for i, e in reversed(eqcopy):
        print(e.getDataId().getBodyId(), i)

    while True:
        try:
            event = eventQueue.get(timeout = 5)
            print(datetime.datetime.now(), "Processing event ...", event)
            processEvent(event)
        except Exception as e:
            print(e)
            
        try:
            print("Clearing split task ...")
            bs.clear_split_task()
            print("Clearing split result ...")
            bs.clear_split_result()
        except Exception as e:
            print (e)
            
    

        #threading.Timer(1, process).start()
    
threading.Timer(1, process).start()

def getSchema(service, method):
    with open(service  + '/interface.raml') as f:
        content = f.readlines()
    f.close()
    
    if not content:
        raise Exception("Invalid schema")

    #print content

    serviceHead = False
    methodStart = False
    schemaStart = False
    objectLevel = 0
    schema =''
    
    for line in content:
        if schemaStart:
            schema += line
            if line.find('{') >= 0:
                objectLevel += 1
            if line.find('}') >= 0:
                objectLevel -= 1
            if objectLevel == 0:
                break
        line = line.strip(' \t\n\r')
        if methodStart:
            if line == 'schema: |':
                schemaStart = True 
        if serviceHead:
            methodStart = True
        if line == '/' + service + ":":
            serviceHead = True
    
    return schema

@get('/home')
def home():
    return '<h1>Welcome to the skeletonization service</h1>'

@get('/split_task')
def list_split_task():
    response = '''
        <h1>Split tasks</h1>
        <p>
        <ol>
        '''
    taskList = bs.read_task_entries()
    for task in taskList:
        response += '<li>' + task + '</li>'
        p = bs.read_task_property(task)
        if p:
            if "age" in p:
                print(p)
                
    response += '</ol></p>'
    
    return response

# @get('/skeletonize')
# def skeletonize():
#     response = '''
#         <form action="/skeletonize" method="post">
#             Body ID: <input name="bodyId" type="text"/>
#             <input value="Submit" type="submit"/>
#             '''
#     response += "<select name=\"database\">"
#     for name in sorted(dvidEnvMap):
#         response += "<option value=\"" + name + "\">" + name + "</option>"
#     response += "</select>"
# 
#     response += "</form>"
# 
#     return response 

# @get('/update_body')
# def requestBodyUpdate():
#     response = '''
#         <form action="/update_body" method="post">
#             Body ID: <input name="bodyId" type="text"/>
#             <input value="Submit" type="submit"/>
#             '''
#     response += "<select name=\"database\">"
#     for name in sorted(dvidEnvMap):
#         response += "<option value=\"" + name + "\">" + name + "</option>"
#     response += "</select>"
# 
#     response += "</form>"
# 
#     return response 

@post('/update_body')
def updateBody():
    print(request.content_type)
    bodyArray = [];
    dvidEnv = None
    #dvidServer = getDefaultDvidServer()
    #uuid = getDefaultUuid()
    option = None
    if request.content_type == 'application/json':
        print(request.json)
        jsonObj = request.json
        try:
            schema = getSchema('update_body', 'post')
            #print schema
            jsonschema.validate(jsonObj, json.loads(schema))
        except jsonschema.exceptions.ValidationError as inst:
            print('Invalid json input')
            print(inst)
            return '<p>Update for ' + str(bodyArray) + ' failed.</p>'
        bodyArray = jsonObj.get('bodies')
        #dvidServer = jsonObj.get('dvid-server')
        option = jsonObj.get('option')
        #uuid = jsonObj['uuid']
        #config = {'dvid-server': dvidServer, 'uuid': uuid}
        dvidEnv = dvidenv.DvidEnv()
        dvidEnv.load_server_config(jsonObj)
        print(dvidEnv)

    if not option:
        option = "update"

    for bodyId in bodyArray:
        if option == "delete":
            event = fd.DataEvent(fd.DataEvent.DATA_DELETE, fd.DataId(fd.DataId.DATA_BODY, bodyId), dvidEnv)
            eventQueue.put(event)
            print("+++Event added:", event)

        if option == "update" or option == "invalidate":
            event = fd.DataEvent(fd.DataEvent.DATA_INVALIDATE, fd.DataId(fd.DataId.DATA_BODY, bodyId), dvidEnv)
            eventQueue.put(event)
            print("+++Event added:", event)

        if option == "update" or option == "add":
            event = fd.DataEvent(fd.DataEvent.DATA_UPDATE, fd.DataId(fd.DataId.DATA_SKELETON, bodyId), dvidEnv)
            eventQueue.put(event)
            print("+++Event added:", event)

@post('/skeletonize')
def do_skeletonize():
    print(request.content_type)
    bodyArray = [];
    #dvidServer = getDefaultDvidServer()
    #uuid = getDefaultUuid()
    if request.content_type == 'application/x-www-form-urlencoded':
        bodyIdStr = request.forms.get('bodyId')
        dvidName = request.forms.get('database')
        skl.setDvidEnv(dvidEnvMap[dvidName])
        print(skl.getDvidEnv())
        bodyArray = [int(bodyId) for bodyId in bodyIdStr.split()]
    elif request.content_type == 'application/json':
        print(request.json)
        jsonObj = request.json
        try:
            jsonschema.validate(jsonObj, json.loads(getSchema('skeletonize', 'post')))
        except jsonschema.exceptions.ValidationError as inst:
            print('Invalid json input')
            print(inst)
            return '<p>Skeletonization for ' + str(bodyArray) + ' failed.</p>'
        uuid = jsonObj['uuid']
        if 'dvid-server' in jsonObj:
            dvidServer = jsonObj['dvid-server']
        bodyArray = jsonObj['bodies']
        config = {'dvid-server': dvidServer, 'uuid': uuid}

        skl.loadDvidConfig(config)
    
    output = {}

    dvidUrl = DvidUrl(skl.getDvidEnv())

    for bodyId in bodyArray:
        print(dvidUrl.getServerUrl())
        conn = http.client.HTTPConnection(dvidUrl.getServerUrl())
        bodyLink = dvidUrl.getSkeletonEndPoint(bodyId)
        print('************', bodyLink)
        conn.request("GET", bodyLink)

        outputUrl = dvidUrl.getServerUrl() + bodyLink

        r1 = conn.getresponse()
        if not r1.status == 200:
            try:
                print("Skeletonizing " + str(bodyId))
                skl.skeletonize(bodyId)
                output[str(bodyId)] = outputUrl
            except Exception as inst:
                return '<p>' + str(inst) + '</p>'
        else:
            print("skeleton is ready for " + str(bodyId))
            output[str(bodyId)] = outputUrl
    
    print(output)
    return json.dumps(output, sort_keys = False)
#     return '<p>Skeletonization for ' + str(bodyArray) + ' is completed.</p>'

@hook('after_request')
def enable_cors(fn=None):
    def _enable_cors(*args, **kwargs):
        print('enable cors')
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Expose-Headers'] = 'Content-Type'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
        if request.method != 'OPTIONS':
            return fn(*args, **kwargs)
    return _enable_cors

@route('/interface/interface.raml', method=['GET', 'OPTIONS'])
@enable_cors
def retrieveRaml():
    print('retrieve raml')
    fileResponse = static_file('interface.raml', root='.', mimetype='application/raml+yaml')
    fileResponse.headers['Access-Control-Allow-Origin'] = '*'

    return fileResponse
    #with open('interface.raml', 'r') as ramlFile:
    #    ramlContent = ramlFile.read()
    #return ramlContent

def get_json_post():
    try:
        return json.load(request.body)
    except ValueError:
        abort(400, 'Bad request: Could not decode request body (expected JSON).')
        
@post('/json')
def parseJson():
    data = get_json_post()
    return '<p>' + data['head'] + '</p>'

port = 8080
if 'port' in serverConfig:
    port = int(serverConfig['port'])

host = 'localhost'
if 'host' in serverConfig:
    host = serverConfig['host']

#if len(sys.argv) > 1:
#    port = sys.argv[1]

#run(host=socket.gethostname(), port=port, debug=True)
run(host=host, port=port, debug=True)

# print getSchema('skeletonize', 'post')
# try:
#     jsonschema.validate({"bodies": [1, 2, 3]}, json.loads(getSchema('skeletonize', 'post')))
# except jsonschema.exceptions.ValidationError as inst:
#     print 'Invalid json input'
#     print inst
