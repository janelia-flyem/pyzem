import os;
from pyzem.dvid import dvidenv
import subprocess;

class Skeletonizer:
    def __init__(self):
        self.dvidEnv = None
        self.processMap = {}
        self.executable = "/opt/bin/neutu"

    def setDvidEnv(self, env):
        self.dvidEnv = env

    def getDvidEnv(self):
        return self.dvidEnv

    def setExecutable(self, exe):
        self.executable = exe

    def skeletonize(self, bodyId, bg = False, forceUpdate = False):
        if bodyId < 1:
            raise Exception("Invalid body ID")

        if self.dvidEnv and self.dvidEnv.is_valid():
            neutuInput = self.dvidEnv.get_neutu_input()
            print(neutuInput)
            args = [self.executable, "--command", "--skeletonize", "--bodyid", str(bodyId), neutuInput]
            if forceUpdate:
                args.append("--force")
            print(args)
            p = subprocess.Popen(args)
            if not bg:
                p.wait()
            return p
        else:
            raise Exception("Invalid DVID env")

if __name__ == "__main__":
    skeletonizer = Skeletonizer()
    dvidEnv = dvidenv.DvidEnv(host = "emdata1.int.janelia.org", port = 8500, uuid = "b6bc", labelvol="bodies")
    skeletonizer.setDvidEnv(dvidEnv) 
    skeletonizer.setExecutable("/Users/zhaot/Work/neutube/neurolabi/neuTube_Debug_FlyEM_Qt5/neutu_d.app/Contents/MacOS/neutu_d")

    #conn.request("DELETE", dvidUrl.getSkeletonEndPoint(15363212))
    skeletonizer.skeletonize(13054149, bg = False, forceUpdate = True)
    print("Done")


