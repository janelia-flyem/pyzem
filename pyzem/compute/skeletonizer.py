import subprocess
from pyzem.dvid import dvidenv

if __name__ == "__main__":
    import command
else:
    from . import command

class Skeletonizer:
    def __init__(self):
        self._dvid_env = None
        self._executable = "neutu"
        self._force_update = False
        self._body_id = None
        self._output = None
        self._state = command.State.not_started

    def setDvidEnv(self, env):
        self._dvid_env = env

    def getDvidEnv(self):
        return self._dvid_env

    def setExecutable(self, exe):
        self._executable = exe
        
    def getCommandArgs(self, bodyId, source, forceUpdate, output = None):
        args = [self._executable, "--command", "--skeletonize", "--bodyid", str(bodyId), source]
        if forceUpdate:
            args.append("--force")

        if output:
            args.append("-o")
            args.append(output)
            
        return args

    def configure(self, config):
        if "dvid" in config:
            self._dvid_env = dvidenv.DvidEnv()
            self._dvid_env.load_server_config(config["dvid"])
        self._body_id = config.get("bodyid")
        self._force_update = config.get("force_update", False)
        self._output = config.get("output", None)
        
    def succeeded(self):
        return self._state == command.State.finished
    
    def run(self, bg = False):
        try:
            self.skeletonize(self._body_id, bg, self._force_update, self._output)
        except:
            self._state = command.State.failed
        
    def skeletonize(self, bodyId, bg = False, forceUpdate = False, output = None):
        self._state = command.State.not_started
        if bodyId < 1:
            raise Exception("Invalid body ID")

        if self._dvid_env and self._dvid_env.is_valid():
            neutuInput = self._dvid_env.get_neutu_input()
            print(neutuInput)
            args = self.getCommandArgs(bodyId, neutuInput, forceUpdate, output)
            print(' '.join(args))
            p = subprocess.Popen(args)
            self._state = command.State.launched
            if not bg:
                p.wait()
                if p.returncode == 0:
                    self._state = command.State.finished
                else:
                    self._state = command.State.failed
            return p
        else:
            raise Exception("Invalid DVID env")

if __name__ == "__main__":
    skeletonizer = Skeletonizer()

    skeletonizer.setExecutable("../../tests/tmp/neutu")
# 
#     #conn.request("DELETE", dvidUrl.getSkeletonEndPoint(15363212))
#     skeletonizer.skeletonize(13054149, bg = False, forceUpdate = True)
    import json
    with open("../../tests/tmp/skeleton.json") as fp:
        config = json.load(fp)
        skeletonizer.configure(config)
        skeletonizer.run(False)
        print(skeletonizer._state)
    
    print("Done")


