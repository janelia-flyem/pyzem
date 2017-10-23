from __future__ import print_function
from __future__ import absolute_import
import os
import sys

from optparse import OptionParser
import json
import requests
from pyzem.dvid import dvidenv
import datetime

def compute_age(d):
    age = -1
    if 'timestamp' in d:
        t = datetime.datetime.strptime(d['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
        dt = datetime.datetime.now() - t
        age = dt.seconds / 60

    return age
    
class DvidClient:
    def __init__(self, host = None, port = None, uuid = None, env = None):
        if env:
            self._url = dvidenv.DvidUrl(env)
        else:
            self._url = dvidenv.DvidUrl(dvidenv.DvidEnv(host = host, port = port, uuid = uuid))
    
    def set_dvidenv(self, env):
        self._url = dvidenv.DvidUrl(env)
        
    def has_skeleton(self, id):
        r = requests.get(self._url.get_skeleon_url(id))
        return s.status_code == 200

    def print_split_result(self):
        url = self._url.join(self._url.get_split_result_url(), 'keyrange', 'task__0/task__z')
        print(url)
        r = requests.get(self._url.join(self._url.get_split_result_url(), 'keyrange', 'task__0/task__z'))
        print(r.text)

        resultList = json.loads(r.text)
        for result in resultList:
            r = requests.get(self._url.join(self._url.get_split_result_url(), 'key', result))
            resultJson = json.loads(r.text)
            print(resultJson[dvidenv.REF_KEY])
            r = requests.get(self._url.join(self._url.get_node_url(), resultJson[dvidenv.REF_KEY]))
            print(r.text)
            
    def clear_split_task(self):
        keys = self.read_keys(path = self._url.get_split_task_path())
        for key in keys:
            url = self._url.get_url(self._url.get_split_task_path(), 'key', key)
            try:
                r = requests.delete(url)
            except Exception as e:
                print("request failed")
                print(url) 

    def clear_split_result(self):
        keys = self.read_keys(path = self._url.get_split_result_path())
        for key in keys:
            url = self._url.get_url(self._url.get_split_result_path(), 'key', key)
            try:
                r = requests.delete(url)
            except Exception as e:
                print("request failed")
                print(url) 

    def read_split_task_keys(self):
        return self.read_keys(path = self._url.get_split_task_path(), range = ['task__0', 'task__z'])
    
    def read_split_result_keys(self):
        return self.read_keys(path = self._url.get_split_result_path(), range = ['task__0', 'task__z'])

    def read_split_task(self, key):
        try:
            r = requests.get(self._url.get_url(self._url.get_split_task_path(), 'key', key))
            taskJson = json.loads(r.text)
            return taskJson
        except Exception:
            return None
        
    def read_split_result(self, key):
        try:
            r = requests.get(self._url.get_url(self._url.get_split_result_path(), 'key', key))
            resultJson = json.loads(r.text)
            return resultJson
        except Exception:
            return None    
        
    def update_ref_set(self, refSet, key, source):
        taskJson = {}
        if source == 'task':
            taskJson = self.read_split_task(key)
        else:
            taskJson = self.read_split_result(key)
            
        if dvidenv.REF_KEY in taskJson:
            refTask = taskJson[dvidenv.REF_KEY]
            refTaskKey = refTask.split('/')[-1]
            refSet.add(refTaskKey)
            self.update_ref_set(refSet, refTaskKey, source)
            
    def clear_task_garbage(self):
        referredSet = set()
        taskList = self.read_split_task_keys()
        for task in taskList:
            self.update_ref_set(data = dvidenv.get_split_task(), key = task, result = referredSet, source = "task")
        
        splitKeyList = self.read_keys(keyvalue = dvidenv.get_split_task())
        for key in splitKeyList:
            if key not in referredSet:
                age = self.read_split_task_age(task)
                if age < 1:
                    self.mark_split_task(key)
                elif age > 100:
                    print("removing", key)
                    self.delete_split_task(key)

    def clear_result_garbage(self):
        referredSet = set()
        taskList = self.read_split_task_keys()
        for task in taskList:
            self.update_ref_set(data = dvidenv.get_split_task(), key = task, result = referredSet, source = "result")
        
        splitKeyList = self.read_keys(keyvalue = dvidenv.get_split_task())
        for key in splitKeyList:
            if key not in referredSet:
                age = self.read_split_result_age(task)
                if age < 1:
                    self.mark_split_result(key)
                elif age > 100:
                    print("removing", key)
                    self.delete_split_result(key)
        
    def print_split_task(self):
        r = requests.get(self._url.get_url(self._url.get_split_task_path(), 'keyrange/task__0/task__z'))
        taskList = json.loads(r.text)
        for task in taskList:
            r = requests.get(self._url.get_url(self._url.get_split_task_path(), 'key', task))
            taskJson = json.loads(r.text)
            if '->' in taskJson:
#                 print taskJson['->']
                data = self.read_path(taskJson['->'])
#                 print data
                taskJson = json.loads(data)
            print(task)
            print('  signal:', taskJson.get('signal'))
            print('  #seeds:', len(taskJson.get('seeds')))
            print('  Age:', self.read_split_task_age(task))
    
    def decode_response(self, r):
        return json.loads(r.text)

    def read_path(self, path):
        r = requests.get(self._url.join(self._url.get_node_url(), path))
        return r.text

    def read_keys(self, path = None, keyvalue = None, range = None):
        print(keyvalue)
        if keyvalue:
            path = self._url.get_data_path(keyvalue)
            
        print(path)
        if path:
            if not range:
                url = self._url.get_url(path, 'keys')
                print(url)
                return self.decode_response(requests.get(url))
            else:
                return self.decode_response(requests.get(self._url.join(self._url.get_url(path, 'keyrange', range[0], range[1]))))
            
    def has_key(self, path = None, key = None, keyvalue = None):
        return True if self.read_key(path, key, keyvalue) else False
        
    def read_key(self, path = None, key = None, keyvalue = None):
        if keyvalue:
            path = self._url.get_data_path(keyvalue)
        try:
            r = requests.get(self._url.get_url(path, 'key', key))
            if r.status_code == 200:
                return r.text
        except:
            print('No', key)
            pass
        
        return None
    
    def get_env(self):
        if self._url:
            return self._url.get_env()
        return None
    
    def delete_skeleton(self, bodyId):
        self.delete_key(self.get_env().get_skeleton_name(), str(bodyId) + "_swc")

    def delete_thumbnail(self, bodyId):
        self.delete_key(self.get_env().get_thumbnail_name(), str(bodyId) + "_mraw")
        
    def delete_body_annotation(self, bodyId):
        self.delete_key(self.get_env().get_body_annotation_name(), bodyId)
        
    def delete_split_task(self, key):
        self.delete_key(dvidenv.get_split_task(), key)
        
    def delete_split_result(self, key):
        self.delete_key(dvidenv.get_split_result(), key)

    def delete_key(self, dataname, key):
        print('Deleting', dataname, key)
        try:
            requests.delete(self._url.get_keyvalue_url(dataname, key))
        except Exception:
            pass

    def read_split_task_property(self, key):
        p = json.loads(self.read_key(self._url.get_split_task_property_path(key)))
        p['age'] = compute_age(p)
        return p
    
    def write_key(self, name, key, data):
        requests.post(self._url.get_keyvalue_url(name, key), data)
    
    def is_split_task_processed(self, key):
        v = self.read_key(keyvalue = dvidenv.get_split_task_property(), key = key)
        if v:
            data = json.loads(v)
            return data.get('processed', False)
        return False
    
    def is_split_result_processed(self, key):
        v = self.read_key(keyvalue = dvidenv.get_split_result_property(), key = key)
        data = json.loads(v) if v else None
        processed = data.get('processed', False) if data else False
            
#         if not processed:
#             v = self.read_key(keyvalue = dvidenv.get_split_result(), key = key)
#             data = json.loads(v) if v else None
#             if data:
#                 processed = "committed" in data
                
        return processed
            
    def has_split_result(self, key):
        return self.has_key(keyvalue = dvidenv.get_split_result(), key = key)
    
    def mark_split_task(self, key):
        v = self.read_key(keyvalue = dvidenv.get_split_task_property(), key = key)
        data = {}
        if v:
            data = json.loads(v)
        data['timestamp'] = str(datetime.datetime.now())
        self.write_key(dvidenv.get_split_task_property(), key, json.dumps(data))
        
    def set_split_task_processed(self, key):
        v = self.read_key(keyvalue = dvidenv.get_split_task_property(), key = key)
        data = {}
        if v:
            data = json.loads(v)
        data['processed'] = True
        self.write_key(dvidenv.get_split_task_property(), key, json.dumps(data))

    def mark_split_result(self, key):
        v = self.read_key(keyvalue = dvidenv.get_split_result_property(), key = key)
        data = {}
        if v:
            data = json.loads(v)
        data['timestamp'] = str(datetime.datetime.now())
        self.write_key(dvidenv.get_split_result_property(), key, json.dumps(data))

    def set_split_result_processed(self, key):
        v = self.read_key(keyvalue = dvidenv.get_split_result_property(), key = key)
        data = {}
        if v:
            data = json.loads(v)
        data['processed'] = True
        self.write_key(dvidenv.get_split_result_property(), key, json.dumps(data))
        
    def read_split_task_time_stamp(self, key):
        text = self.read_key(keyvalue = dvidenv.get_split_task_property(), key = key)
        try:
            d = json.loads(text)
            if 'timestamp' in d:
                return datetime.datetime.strptime(d['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
        except Exception as e:
            pass

        return None

    def read_split_result_time_stamp(self, key):
        v = self.read_key(keyvalue = dvidenv.get_split_result_property(), key = key)
        if v:
            d = json.loads(v)
            if 'timestamp' in d:
                return datetime.datetime.strptime(d['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
        return None

    def read_split_task_age(self, key):
        age = -1
        t = self.read_split_task_time_stamp(key)
        if t:
            dt = datetime.datetime.now() - t
            age = dt.seconds / 60
        return age

    def read_split_result_age(self, key):
        t = self.read_split_result_time_stamp(key)
        age = 0
        if t:
            dt = datetime.datetime.now() - t
            age = dt.seconds
        return age
        
        
class DvidService:
    def __init__(self, host = None, port = None, uuid = None):
        self._reader = DvidReader(host, port, uuid)

    #def get_split_task_list(self):

class Librarian:
    def __init__(self, host = None, port = None):
        self._host = host
        self._port = port
    
if __name__ == '__main__':
#     dvid = DvidClient("emdata1.int.janelia.org", 8500, "b6bc")
#     dvid.get_env().set_labelvol("bodies")
#     print(dvid.get_env())
#     
#     dvid.delete_skeleton(13054149)
    dvid = DvidClient('zhaot-ws1', 9000, '194d')
    dvid.set_split_task_processed("task__http-++emdata1.int.janelia.org-8500+api+node+b6bc+bodies+sparsevol+17159670")
    p = dvid.read_split_task_property("task__http-++emdata1.int.janelia.org-8500+api+node+b6bc+bodies+sparsevol+17159670")
    print(p)
    
    print(dvid.has_split_result("task__http-++emdata1.int.janelia.org-8700+api+node+f46b+pb26-27-2-trm-eroded32_ffn-20170216-2_celis_cx2-2048_r10_0_seeded_64blksz_vol+sparsevol+87839"))
    dvid.set_split_result_processed("task__http-++emdata1.int.janelia.org-8700+api+node+f46b+pb26-27-2-trm-eroded32_ffn-20170216-2_celis_cx2-2048_r10_0_seeded_64blksz_vol+sparsevol+87839")
    print(dvid.is_split_result_processed("task__http-++emdata1.int.janelia.org-8700+api+node+f46b+pb26-27-2-trm-eroded32_ffn-20170216-2_celis_cx2-2048_r10_0_seeded_64blksz_vol+sparsevol+87839"))
    #dvid.print_split_result()
    #dvid.clear_split_result()
#     dvid.write_key('result_split_property', 'test', 'test')

    #dvid._conn.request("DELETE", '/api/node/4d3e/task_split/key/head__8b8ec933b673fb8a5e9c0abe819bf5d9')
    #dvid._conn.request("DELETE", '/api/node/4d3e/task_split/key/head__9f2d3aa27cd0e3c3149c01baae438040')
    #dvid._conn.request("DELETE", '/api/node/4d3e/task_split/key/head__82a437eabc6c55d8517c9c8eec948659')
    #r = dvid._conn.getresponse()
    #print r.status
    #print r.msg
#     keys = dvid.read_split_task_keys()
#     print(keys)
#     for key in keys:
#         print(dvid.has_key(key = key, keyvalue = dvidenv.get_split_result()))
#     dvid.print_split_task()/
#     dvid.print_split_result()
    #dvid.clear_split_task()
   # except Exception as e:
   #     print e
    #reader.print_split_result()
