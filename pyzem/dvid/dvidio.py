import os
import sys

from optparse import OptionParser
import json
import requests
import dvidenv
import datetime

class DvidClient:
    def __init__(self, host = None, port = None, uuid = None, env = None):
        if env:
            self._url = dvidenv.DvidUrl(env)
        else:
            self._url = dvidenv.DvidUrl(dvidenv.DvidEnv(host = host, port = port, uuid = uuid))
    
    def hasSkeleton(self, id):
        r = requests.get(self._url.get_skeleon_url(id))
        return s.status_code == 200

    def print_split_result(self):
        url = self._url.join(self._url.get_split_result_url(), 'keyrange', 'task__0/task__z')
        print url
        r = requests.get(self._url.join(self._url.get_split_result_url(), 'keyrange', 'task__0/task__z'))
        print r.text

        resultList = json.loads(r.text)
        for result in resultList:
            r = requests.get(self._url.join(self._url.get_split_result_url(), 'key', result))
            resultJson = json.loads(r.text)
            print resultJson[dvidenv.REF_KEY]
            r = requests.get(self._url.join(self._url.get_node_url(), resultJson[dvidenv.REF_KEY]))
            print r.text
            
    def clear_split_task(self):
        keys = self.read_keys(path = self._url.get_split_task_path())
        for key in keys:
            url = self._url.get_url(self._url.get_split_task_path(), 'key', key)
            try:
                r = requests.delete(url)
            except Exception as e:
                print "request failed"
                print url 

    def clear_split_result(self):
        keys = self.read_keys(path = self._url.get_split_result_path())
        for key in keys:
            url = self._url.get_url(self._url.get_split_result_path(), 'key', key)
            try:
                r = requests.delete(url)
            except Exception as e:
                print "request failed"
                print url 

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
        
    def print_split_task(self):
        r = requests.get(self._url.get_url(self._url.get_split_task_path(), 'keyrange/task__0/task__z'))
        taskList = json.loads(r.text)
        for task in taskList:
            r = requests.get(self._url.get_url(self._url.get_split_task_path(), 'key', task))
            taskJson = json.loads(r.text)
            if taskJson.has_key('->'):
#                 print taskJson['->']
                data = self.read_path(taskJson['->'])
#                 print data
                taskJson = json.loads(data)
            print task
            print '  signal:', taskJson.get('signal')
            print '  #seeds:', len(taskJson.get('seeds'))
            print '  Age:', self.read_split_task_age(task)
    
    def decode_response(self, r):
        return json.loads(r.text)

    def read_path(self, path):
        r = requests.get(self._url.join(self._url.get_node_url(), path))
        return r.text

    def read_keys(self, path = None, keyvalue = None, range = None):
        print keyvalue
        if keyvalue:
            path = self._url.get_data_path(keyvalue)
            
        print path
        if path:
            if not range:
                url = self._url.get_url(path, 'keys')
                print url
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
            print 'No', key
            pass
        
        return None

    def delete_split_task(self, key):
        self.delete_key(dvidenv.get_split_task(), key)
        
    def delete_split_result(self, key):
        self.delete_key(dvidenv.get_split_result(), key)

    def delete_key(self, dataname, key):
        try:
            requests.delete(self._url.get_keyvalue_url(dataname, key))
        except Exception:
            pass

    def read_split_task_property(self, key):
        return json.loads(self.read_key(self.get_split_task_property_path(key)))
    
    def write_key(self, name, key, data):
        requests.post(self._url.get_keyvalue_url(name, key), data)

    def mark_split_task(self, key):
        data = {'timestamp': str(datetime.datetime.now())}
        self.write_key(dvidenv.get_split_task_property(), key, json.dumps(data))

    def mark_split_result(self, key):
        data = {'timestamp': str(datetime.datetime.now())}
        self.write_key(dvidenv.get_split_result_property(), key, json.dumps(data))

    def read_split_task_time_stamp(self, key):
        text = self.read_key(keyvalue = dvidenv.get_split_task_property(), key = key)
        try:
            d = json.loads(text)
            if d.has_key('timestamp'):
                return datetime.datetime.strptime(d['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
        except Exception as e:
            pass

        return None

    def read_split_result_time_stamp(self, key):
        d = json.loads(self.read_key(keyvalue = dvidenv.get_split_result_property(), key = key))
        if d.has_key('timestamp'):
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
            age = dt.seconds / 60
        return age
    
    def update_ref_set(self, data = None, key = None, result = None):
        if result is not None:
            keyJson = json.loads(self.read_key(keyvalue = data, key = key))
            if keyJson and keyJson.has_key(dvidenv.REF_KEY):
                ref = keyJson[dvidenv.REF_KEY]
                refKey = ref.split('/')[-1]
                result.add(refKey)
                self.update_ref_set(result = result, data = data, key = refKey)

class DvidService:
    def __init__(self, host = None, port = None, uuid = None):
        self._reader = DvidReader(host, port, uuid)
        
        
class DvidService:
    def __init__(self, host = None, port = None, uuid = None):
        self._reader = DvidReader(host, port, uuid)

    #def get_split_task_list(self):

class Librarian:
    def __init__(self, host = None, port = None):
        self._host = host
        self._port = port
    
if __name__ == '__main__':
    dvid = DvidClient('zhaot-ws1', 9000, '194d')
    #dvid.print_split_result()
    #dvid.clear_split_result()
#     dvid.write_key('result_split_property', 'test', 'test')

    #dvid._conn.request("DELETE", '/api/node/4d3e/task_split/key/head__8b8ec933b673fb8a5e9c0abe819bf5d9')
    #dvid._conn.request("DELETE", '/api/node/4d3e/task_split/key/head__9f2d3aa27cd0e3c3149c01baae438040')
    #dvid._conn.request("DELETE", '/api/node/4d3e/task_split/key/head__82a437eabc6c55d8517c9c8eec948659')
    #r = dvid._conn.getresponse()
    #print r.status
    #print r.msg
    keys = dvid.read_split_task_keys()
    print keys
    for key in keys:
        print dvid.has_key(key = key, keyvalue = dvidenv.get_split_result())
#     dvid.print_split_task()/
#     dvid.print_split_result()
    #dvid.clear_split_task()
   # except Exception as e:
   #     print e
    #reader.print_split_result()
