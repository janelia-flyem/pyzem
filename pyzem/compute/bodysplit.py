from __future__ import print_function
import subprocess
import json

from pyzem.dvid import dvidenv, dvidio

def update_ref_set(refSet, dc, key):
    taskJson = dc.read_split_task(key)
    if taskJson.has_key(dvidenv.REF_KEY):
        refTask = taskJson[dvidenv.REF_KEY]
        refTaskKey = refTask.split('/')[-1]
        refSet.add(refTaskKey)
        print(refTaskKey)
        update_ref_set(refSet, dc, refTaskKey)

def clearSplitTask(dc):
    referredSet = set()
    taskList = dc.read_split_task_keys()
    for task in taskList:
        processed = dc.is_split_task_processed(task)
        if not processed:
            referredSet.add(task)
            dc.update_ref_set(key = task, refSet = referredSet, source = 'task')
            if dc.has_split_result(task):
                print("Has result:", task)
                dc.set_split_task_processed(task)
        else:
            print("Processed:", task)

    print ("Reading tasks")
    splitKeyList = dc.read_keys(keyvalue = dvidenv.get_split_task())
    print("List:", splitKeyList)
    for key in splitKeyList:
        if key not in referredSet:
            age = dc.read_split_task_age(key)
            print ("Unreferred:", key, "Age:", age)
            if age < 1:
                dc.mark_split_task(key)
            elif age > 100:
                dc.delete_split_task(key)
        else:
            print("Referred:", key)
        
def clearSplitResult(dc):
    referredSet = set()
    resultList = dc.read_split_result_keys()
    for result in resultList:
        processed = dc.is_split_result_processed(result)
        if not processed:
            referredSet.add(result)
            dc.update_ref_set(key = result, refSet = referredSet, source = 'result')
        else:
            print("Processed:", result)

    print ("Reading results")
    splitKeyList = dc.read_keys(keyvalue = dvidenv.get_split_result())
    print("List:", splitKeyList)
    for key in splitKeyList:
        if key not in referredSet:
            age = dc.read_split_result_age(key)
            print ("Unreferred:", key, "Age:", age)
            if age < 1:
                dc.mark_split_result(key)
            elif age > 100:
                dc.delete_split_result(key)
        else:
            print("Referred:", key)
                    
class BodySplit:
    def __init__(self, neutuPath = None, env = None):
        self._neutu = neutuPath
        self._url = dvidenv.DvidUrl(env)
        self._commit = False
        
    def get_env(self):
        return self._url.get_env()
    
    def set_neutu_path(self, path):
        self._neutu = path
        
    def set_committing(self, committing):
        self._commit = committing

    def set_server(self, env):
        self._url = dvidenv.DvidUrl(env)
        
    def load_server(self, config):
        env = dvidenv.DvidEnv(host = config.get('host', None), port = config.get('port', None), uuid = config.get('uuid', None))
        self._url = dvidenv.DvidUrl(env)
        
    def get_split_task_url(self):
        return self._url.get_url(self._url.get_split_task_path())
    
    def clear_split_task(self):
        dc = dvidio.DvidClient(env = self._url.get_env())
        clearSplitTask(dc)
        
    def clear_split_result(self):
        dc = dvidio.DvidClient(env = self._url.get_env())
        clearSplitResult(dc)
        
    def read_task_entries(self):
        dc = dvidio.DvidClient(env = self._url.get_env())
        return dc.read_split_task_keys()
    
    def read_task_property(self, key):
        dc = dvidio.DvidClient(env = self._url.get_env())
        return dc.read_split_task_property(key)

    def run(self, task_key, commandFile = None):
        print(self._neutu)
        du = self._url
        task_url = du.get_url(du.get_split_task_path(task_key)) 
        print(task_url)

        commandConfig = {"command": "split_body", "commit": self._commit}
#         '{"command": "split_body"}'
        args = [self._neutu, '--command', '--general', json.dumps(commandConfig), task_url, '-o', du.get_node_url()]
        print(args)
        p = subprocess.Popen(args)
        p.wait()
        return p

if __name__ == '__main__':
    bs = BodySplit('/Users/zhaot/Work/neutube/neurolabi/neuTube_Debug_FlyEM_Qt5/neutu_d.app/Contents/MacOS/neutu_d')
    bs.set_server(dvidenv.DvidEnv("zhaot-ws1", 9000, "194d"))
    bs.set_committing(True)
    bs.run("task__http-++emdata1.int.janelia.org-8500+api+node+b6bc+bodies+sparsevol+12767166")
#     print(bs.get_split_task_url())
#     
#     dc = dvidio.DvidClient(env = bs.get_env())
#     print(dc.is_split_result_processed(key = "task__http-++emdata1.int.janelia.org-8500+api+node+b6bc+bodies+sparsevol+12767166"))
#     
#     bs.clear_split_task()
#     bs.clear_split_result()





