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
        if args:
            if args[0].startswith('/'):
                if newargs:
                    newargs[0] = '/' + newargs[0]

        return "/".join(newargs)

    def get_env(self):
        return self._env

    def get_server_url(self):
        return self._env.get_server_address()

    def get_url(self, *args):
        return self.join(self.get_server_url(), self.join(*args))

    def get_skeleton_path(self, body_id):
        return self.get_keyvalue_path(self._env.get_skeleton_name(), str(body_id) + '_swc')

    def get_skeleton_url(self, body_id):
        return self.get_url(self.get_skeleton_path(body_id))

    def get_node_path(self):
        return '/api/node/' + self._env.get_uuid()

    def get_repo_path(self):
        return '/api/repo/' + self._env.get_uuid()

    def get_node_url(self):
        return self.get_url(self.get_node_path())

    def get_node_info_path(self):
        return self.get_repo_path() + '/info'

    def get_data_path(self, dataname):
        return self.get_node_path() + '/' + dataname

    def get_data_url(self, dataname):
        return self.get_url(self.get_data_path(dataname))

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
            return self.join('/', self.get_node_path(), get_split_result())

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

    def get_body_size_path(self, body_id, is_supervoxel = False):
        path = self.join(self.get_data_path(self._env.get_bodydata_name()), "size", str(body_id))
        if is_supervoxel:
            path += "?supervoxels=true"
        return path

    def get_sparsevol_size_path(self, body_id, is_supervoxel = False):
        path = self.join(self.get_data_path(self._env.get_bodydata_name()), "sparsevol-size", str(body_id))
        if is_supervoxel:
            path += "?supervoxels=true"
        return path

    def get_bookmark_path(self, user):
        path = self.join(self.get_data_path(self._env.get_bookmark_name()),"tag", "user:" + user)
        return path

    def get_bookmark_element_path(self, pos):
        path = self.join(self.get_data_path(self._env.get_bookmark_name()), 'element', str(pos[0]) + '_' + str(pos[1]) + '_' + str(pos[2]))
        return path

    def get_bookmark_element_url(self, pos):
        return self.get_url(self.get_bookmark_element_path(pos=pos))

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

    def load_source(self, source):
        tokens = source.split(':')
        if len(tokens) > 3:
            if tokens[0] == 'http':
                self._host = tokens[1]
                self._port = int(tokens[2])
                self._uuid = tokens[3]

            if len(tokens) > 4:
                self._labelvol = tokens[4]


    def is_valid(self):
        return self._host and self._uuid

    def set_labelvol(self, name):
        self._labelvol = name

    def set_segmentation(self, name):
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
            if config.has_key("labelvol"):
                self.set_labelvol(config.get("labelvol"))
            if config.has_key("segmentation"):
                self.set_segmenation(config.get("segmentation"))
        else:
            self._host = config.get("address")
            self._port = config.get("port")
            self._uuid = config.get("uuid")
            self._labelvol = config.get("body_label")

    def get_bodydata_name(self, name = None):
        finalName = None
        if self._labelvol:
            if self._labelvol == 'bodies':
                finalName = name
            else:
                if name:
                    finalName = self._labelvol + '_' + name
                else:
                    finalName = self._labelvol
        return finalName

    def get_skeleton_name(self):
        return self.get_bodydata_name("skeletons")

    def get_thumbnail_name(self):
        return self.get_bodydata_name("thumbnails")

    def get_body_annotation_name(self):
        return self.get_bodydata_name("annotations")

    def get_labelvol(self):
        return self._labelvol

    def get_bookmark_name(self):
        return "bookmark_annotations"

    def get_split_seed(self):
        if self._labelvol:
            if self._labelvol == 'bodies':
                return 'splits'
            else:
                return self._labelvol + "_" + 'splits'

        return None

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
    print(du.get_body_size_path(1))
    print(du.get_body_size_path(1, is_supervoxel=True))
    print(du.get_url(du.get_body_size_path(1)))
    print(du.get_sparsevol_size_path(1, is_supervoxel=True))
    print(du.get_bookmark_path(user="zhaot"))
    print(du.get_bookmark_element_path(pos=[1, 2, 3]))
    print(du.get_bookmark_element_url(pos=[1, 2, 3]))
    print(du.get_data_path('test'))

    denv = DvidEnv()
    denv.load_source("http:emdata1.int.janelia.org:8500:b6bc:bodies")
    print(denv)
