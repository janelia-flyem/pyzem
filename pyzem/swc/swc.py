import networkx as nx
import math

class SwcNode:
    def __init__(self, nid = None, ntype = None, radius = None, pos = None):
        self._id = nid
        self._radius = radius
        self._pos = pos
        self._type = ntype
        
    def distance(self, tn):
        """
        Returns the distance to another node.
        
        Parameters
        ----------
        tn : SwcNode
        """
        if tn:
            dx = self._pos[0] - tn._pos[0]
            dy = self._pos[1] - tn._pos[1]
            dz = self._pos[2] - tn._pos[2]
            d2 = dx * dx + dy * dy + dz * dz
            
            return math.sqrt(d2)
        
        return 0.0
        
    def radius(self):
        return self._radius
    
    def scale(self, sx, sy, sz, adjusting_radius = True):
        self._pos[0] *= sx
        self._pos[1] *= sy
        self._pos[2] *= sz
        
        if adjusting_radius:
            self._radius *= math.sqrt(sx * sy)
        
    def to_swc_str(self):
        return '%d %d %g %g %g %g' % (self._id, self._type, self._pos[0], self._pos[1], self._pos[2], self._radius)
                          
    def __str__(self):
        return '%d (%d): %s, %g' % (self._id, self._type, str(self._pos), self._radius)
        
class SwcTree:
    def __init__(self):
        self._tree = nx.DiGraph()

    def clear(self):
        self._tree.clear()
        
    def is_comment(self, line):
        return line.strip().startswith('#')
        
    def root(self):
        rootArray = []
        idList = self._tree.successors(-1)
        for nid in idList:
            rootArray.append(self.node(nid))
        
        return rootArray
            
    def node(self, nid):
        gn = self._tree.node[nid]
        if gn:
            return gn['node']
    
    def parent_id(self, nid):
        parent_id = self._tree.predecessors(nid)
        if len(parent_id) > 0:
            return parent_id[0]
        
        return -1
    
    def parent_node(self, nid):
        parent_id = self._tree.predecessors(nid)
        if len(parent_id) > 0:
            parent_id = parent_id[0]
            if parent_id >= 0:
                return self.node(parent_id)
    
    def load(self, path):
        self.clear()
        with open(path, 'r') as fp:
            lines = fp.readlines()
            for line in lines:
                if not self.is_comment(line):
#                     print line
                    data = map(float, line.split())
                    if len(data) == 7:
                        nid = int(data[0])
                        ntype = int(data[1])
                        pos = data[2:5]
                        radius = data[5]
                        parent_id = data[6]
                        self._tree.add_edge(parent_id, nid)
                        self._tree.node[nid]['node'] = SwcNode(nid = nid, ntype = ntype, radius = radius, pos = pos)
            fp.close()
                        
    def save(self, path):
        with open(path, 'w') as fp:
            nodeList = self._tree.nodes(data = True)
            for nid, data in nodeList:
                if data:
                    tn = data['node']
                    fp.write('%s %d\n' % (tn.to_swc_str(), self.parent_id(nid)))
            fp.close()
                             
    def has_regular_node(self):
        idList = self._tree.successors(-1)
        return len(idList) > 0
    
    def max_id(self):
        nodes = self._tree.nodes()
        return max(nodes)
    
    def node_count(self, regular = True):
        nodes = self._tree.nodes()
        if regular:
            count = 0
            for n in nodes:
                if n >= 0:
                    count += 1
        else:
            count = len(nodes)
                    
        return count
    
    def parent_distance(self, nid):
        d = 0
        tn = self.node(nid)
        if tn:
            parent_tn = self.parent_node(nid)
            if parent_tn:
                d = tn.distance(parent_tn)
                
        return d
    
    def scale(self, sx, sy, sz, adjusting_radius = True):
        nodeList = self._tree.nodes(data = True)
        for nid, data in nodeList:
            if data:
                tn = data['node']
                tn.scale(sx, sy, sz, adjusting_radius)
        
    def length(self):
        nodes = self._tree.nodes()
        result = 0.0
        for nid in nodes:
            result += self.parent_distance(nid)
                
        return result

    def radius(self, nid):
        return self.node(nid).radius()
    
    def backtrace_radius(self, nid, path_length):
        radius = 0.0
        remain_length = path_length
        current_id = nid
        plen = 0
        while current_id >= 0:
            plen = self.parent_distance(nid)
            remain_length -= plen
            if remain_length < 0:
                break
            
            current_id = self.parent_id(nid)
        
        if current_id >= 0:
            if plen == 0:
                radius = self.radius(current_id)
            else:
                a = -remain_length / plen
                r = self.radius(current_id)
                pr = self.radius(self.parent_id(current_id))
                print a
                radius = r * a + pr * (1 - a)
            
        return radius
            
            
                        
if __name__ == '__main__':
    print('testing ...')
    swc = SwcTree()
    swc.load('/Users/zhaot/Work/neutube/neurolabi/data/_benchmark/swc/fork.swc')
    print(swc._tree.nodes(data = True))
    print(swc._tree.nodes())
    print(swc._tree.edges())
    print(swc.root())
    tn = swc.node(2)
    print(tn)
    print(swc.has_regular_node())
    print(swc.max_id())
    print(swc.node_count())
    print(swc.parent_distance(2))
#     swc.scale(2, 2, 2)
#     print(swc.parent_distance(2))
#     swc.save('/Users/zhaot/Work/neutube/neurolabi/data/test.swc')
    print(swc.length())
    print(swc.backtrace_radius(2, 1))

                        