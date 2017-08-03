import timer
import threading
import time

from dvid import dvidenv
from dvid import dvidio
from compute import bodysplit

split = bodysplit.BodySplit('/Users/zhaot/Work/neutube/neurolabi/neuTube_Debug_FlyEM/neutu_d.app/Contents/MacOS/neutu_d', dvidenv.DvidEnv(host = 'localhost', port=8000, uuid='4d3e'))
print split._neutu
#split.run('task__http-++emdata1.int.janelia.org-8500+api+node+b6bc+bodies+sparsevol+12007338')

dc = dvidio.DvidClient(host = 'localhost', port=8000, uuid='4d3e')
splitTaskList = dc.read_split_task_keys()
print splitTaskList

#dc.clear_split_task()
#dc.clear_split_result()
#exit()

def process():
    while True:
        splitTaskList = dc.read_split_task_keys()
        print splitTaskList
        for task in splitTaskList:
            split.run(task)
        time.sleep(10)

process()
#threading.Timer(1, process).start()

