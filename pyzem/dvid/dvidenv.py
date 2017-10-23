from __future__ import print_function
import json
import urllib

REF_KEY = '->'

def get_split_task():
    return 'task_split'

def get_split_result():
    return 'result_split'

def get_split_task_property():
    return 'task_split_property'

def get_split_result_property():
    return 'result_split_property'

class DvidUrl(object):
    def __init__(self, env = None):
        self._env = env

    def host(self):
        return self._env._host

    def port(self):
        return self._env._port

    def join(self, *args):
        newargs = [str(x).rstrip('/').lstrip('/') for x in args]
        #newargs = map(lambda x: '/' + x if (x[0] != '/') else x, newargs)
        #print newargs
        
        return "/".join(newargs)

    def get_env(self):
        return self._env
    
    def get_url(self, *args):
        return self.join(self.get_server_url(), self.join(*args))

    def get_server_url(self):
        return self._env.get_server_address()


    def get_skeleton_path(self, id):
        return get_keyvalue_path(self._env.get_skeleton_name, str(id) + '_swc')

    def get_skeleton_url(self, id):
        return self.get_url(self.get_skeleton_path(id))

    def get_node_path(self):
        return '/api/node/' + self._env.get_uuid()

    def get_node_url(self):
        return self.get_url(self.get_node_path())

    def get_node_info_path():
        return self.get_repo_path() + '/info'

    def get_data_path(self, dataname):
        return self.get_node_path() + '/' + dataname

    def get_split_task_property_path(self, key = None):
        if key:
            return self.get_keyvalue_path(get_split_task_property(), key)
        else:
            return self.get_data_path(get_split_task_property())

    def get_split_task_path(self, key = None):
        if key:
            return self.get_keyvalue_path(get_split_task(), key)
        else:
            return self.get_data_path(get_split_task())

    def get_split_result_path(self, key = None):
        if key:
            return self.get_keyvalue_path(get_split_result_property(), key)
        else:
            return self.join(self.get_node_path(), get_split_result())

    def get_split_result_property_path(self, key = None):
        if key:
            return self.get_keyvalue_path(get_split_result_property(), key)
        else:
            return self.get_data_path(get_split_result_property())

    def get_split_result_url(self):
        return self.get_url(self.get_split_result_path())

    def get_keys_path(self, dataname):
        return self.get_data_path(dataname) + '/keys'

    def get_keyvalue_path(self, dataname, key):
        return self.get_data_path(dataname) + '/key/' + key

    def get_keyvalue_url(self, dataname, key):
        return self.get_url(self.get_keyvalue_path(dataname, key))

    def get_split_seed_url(self, command = 'keys'):
        if self._env.get_labelvol():
            return self.get_node_url() + '/' + self._env.get_split_seed() + '/' + command



class DvidEnv(object):
    def __init__(self, host = None, port = None, uuid = None,
            labelvol = None, labelblk = None):
        self._host = host
        self._port = port
        self._uuid = uuid
        self._labelvol = labelvol
        self._labelblk = labelblk

    def __str__(self):
        return self.get_neutu_input()
    
    def is_valid(self):
        return self._host and self._uuid
    
    def set_labelvol(self, name):
        self._labelvol = name

    def get_uuid(self):
        return self._uuid

    def get_server_address(self):
        url = self._host
        if self._port:
            url += ":" + str(self._port)

        if not url.startswith("http://"):
            url = "http://" + url

        return url

    def get_neutu_input(self):
        ninput = "http:" + self._host
        if self._port:
            ninput += ":" + str(self._port)
        
        ninput += ":" + self._uuid
        if self._labelvol:
            ninput += ":" + self._labelvol
        return ninput
        
    def load_server_config(self, config):
        if "dvid-server" in config:
            dvidServer = config["dvid-server"]
            p = urllib.parse.urlsplit(dvidServer)
            print(p)
            if p.netloc:
                self._host = p.netloc
            else:
                self._host = p.path
            self._port = None

            self._uuid = config["uuid"]
            print(config.get("labelvol"))
            self.set_labelvol(config.get("labelvol"))

    def get_bodydata_name(self, name):
        finalName = None
        if self._labelvol:
            if self._labelvol == 'bodies':
                finalName = name
            else:
                finalName = self._label + '_' + name
        return finalName
    
    def get_skeleton_name(self):
        return self.get_bodydata_name("skeletons")
    
    def get_thumbnail_name(self):
        return self.get_bodydata_name("thumbnails")
    
    def get_body_annotation_name(self):
        return self.get_bodydata_name("annotations")

    def get_labelvol(self):
        return self._labelvol

    def get_split_seed(self):
        if self._labelvol:
            if self._labelvol == 'bodies':
                return 'splits'
            else:
                return self._labelvol + "_" + 'splits'

        return None

    def is_valid(self):
        return self._host and self._uuid

if __name__ == "__main__":
    du = DvidUrl(DvidEnv(host = "emdata1.int.janelia.org", port = 8700, uuid = "4320", labelvol = "pb26-27-2-trm-eroded32_ffn-20170216-2_celis_cx2-2048_r10_0_seeded_64blksz_vol"))
    print(du.join('test', 'key'))
    print(du.get_url('test', 'key'))
    print(du.get_split_seed_url('keys'))
    print(du.get_node_path())
    print(du.get_node_url())
    print(du.get_keys_path('test'))
    print(du.get_keyvalue_path('test', 'key1'))
    print(du.get_split_task_path())
    print(du.join(du.get_split_task_path(), 'keys'))
    print(du.get_split_task_property_path())
    print(du.get_split_result_property_path('test'))
    print(du.get_split_task_property_path('test'))
    print(du.get_split_result_property_path())
