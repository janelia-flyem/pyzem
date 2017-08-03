import subprocess

from pyzem.dvid import dvidenv

class BodySplit:
    def __init__(self, neutuPath, server = None):
        self._neutu = neutuPath
        self._server = server

    def setNeuTuPath(path):
        self._neutu = path

    def setServer(server):
        self._server = server

    def run(self, task_key):
        print self._neutu
        du = dvidenv.DvidUrl(self._server)
        task_url = du.get_url(du.get_split_task_path(task_key)) 
        print task_url

        args = [self._neutu, '--command', '--general', '{"command": "split_body"}', task_url, '-o', du.get_node_url()]
        print args
        p = subprocess.Popen(args)
        p.wait()
        return p







