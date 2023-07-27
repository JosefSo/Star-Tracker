import json
import math


class Node:
    def __init__(self, node_id: int, pos: tuple = None, r: float = -1, b: float = -1):
        self.edges = 0
        self.id = node_id
        self.r = r
        self.b = b
        if pos is not None:
            x, y = pos
            self.pos = float(x), float(y)
        else:
            self.pos = None

    def getId(self) -> int:
        return self.id

    def setId(self, id: int):
        self.id = id

    def getLocation(self) -> tuple:
        return self.pos

    def setLocation(self, x: float, y: float):
        self.pos = (x, y)

    def getR(self) -> float:
        return self.r

    def getB(self) -> float:
        return self.b

    def __repr__(self):
        return f"id:{self.id} edges: {self.edges} pos:{self.pos} radius:{self.r} brightness: {self.b}"


class Edge:
    def __init__(self, p1: int, p2: int, dist: float = -1, m: float = -1, n: float = -1):
        self.p1 = p1
        self.p2 = p2
        self.d = dist
        self.m, self.n = m, n

    def getP1(self) -> int:
        return self.p1

    def getP2(self) -> int:
        return self.p2

    def getDist(self) -> float:
        return self.d

    def __repr__(self):
        return f"id1:{self.p1} id2: {self.p2} distance:{self.d} "


class Graph():

    def __init__(self, file_name: str = '', dir: str = ''):
        self.nodes = {}
        self.edges = {}
        self.mc = 0
        self.min_dist = math.inf
        self.avgB = 0
        self.maxR= 0
        self.avgR = 0
        if dir != '':
            file_name = f'{dir}/{file_name}'
        file_name = file_name.split('.')[0]
        if file_name != "":
            with open(f'{file_name}.json', 'r') as f:
                dict = json.load(f)
            nodes = dict.get("Nodes")
            for n in nodes:
                id = (int)(n["id"])
                pos = ()
                r = (float)(n["r"])
                b = (float)(n["b"])
                if "x" in n.keys():
                    pos = ((float)(n["x"]), (float)(n["y"]))
                node = Node(id, pos, r, b)
                self.add_node(node)
            edges = dict.get("Edges")
            for n in edges:
                self.add_edge((int)(n["p1"]), (int)(n["p2"]))

    def dist(self, p1: int, p2: int) -> float:
        if self.nodes[p1].getLocation() is None or self.nodes[p2].getLocation() is None:
            return -1
        x1, y1 = self.nodes[p1].getLocation()
        x2, y2 = self.nodes[p2].getLocation()
        dx = (x2 - x1)
        dy = (y2 - y1)
        return math.sqrt(math.pow(dx, 2) + math.pow(dy, 2))

    def equationAndDist(self, src: int, dest: int) -> tuple:
        x1, y1 = self.nodes[src].getLocation()
        x2, y2 = self.nodes[dest].getLocation()
        dx = (x2 - x1)
        dy = (y2 - y1)
        d = math.sqrt(math.pow(dx, 2) + math.pow(dy, 2))
        if x2 == x1:
            m = 0
            n = x1
        else:
            m = dy / dx
            n = y2 - (m * x2)
        return m, n, d

    def distNodeToPoint(self, v: int, p: tuple) -> float:
        x1, y1 = self.nodes[v].getLocation()
        x2, y2 = p
        dx = (x2 - x1)
        dy = (y2 - y1)
        return math.sqrt(math.pow(dx, 2) + math.pow(dy, 2))

    def v_size(self) -> int:
        return len(self.nodes)

    def e_size(self) -> int:
        sum = 0
        for e in self.edges.values():
            sum += len(e)
        return (int)(sum / 2)

    def get_all_nodes(self) -> list:
        ans = []
        for i in self.nodes.values():
            ans.append(i)
        return ans

    def get_all_edges(self) -> list:
        ans = []
        for i in self.edges.keys():
            for j in self.edges[i].keys():
                if i <= j:
                    ans.append(self.edges[i][j])
        return ans

    def all_edges_of_node(self, id: int) -> bool or dict:
        if id not in self.nodes.keys():
            return False
        allout = {}
        for i in self.edges[id].keys():
            if isinstance(self.edges.get(id).get(i), Edge):
                if self.edges.get(id).get(i) is not None:
                    allout[i] = self.edges.get(id).get(i).getDist()
        return allout

    def all_edges_of_node(self, id: int) -> bool or dict:
        if id not in self.nodes.keys():
            return False
        allout = {}
        for i in self.edges[id].keys():
            if isinstance(self.edges.get(id).get(i), Edge):
                if self.edges.get(id).get(i) is not None:
                    allout[i] = self.edges.get(id).get(i).getDist()
        return allout

    def all_edges_of_node(self, id: int) -> bool or dict:
        if id not in self.nodes.keys():
            return False
        allout = {}
        for i in self.edges[id].keys():
            if isinstance(self.edges.get(id).get(i), Edge):
                if self.edges.get(id).get(i) is not None:
                    allout[i] = self.edges.get(id).get(i).getDist()
        return allout

    def get_mc(self) -> int:
        return self.mc

    def get_min_dist(self) -> float:
        return self.min_dist

    def add_edge(self, id1: int, id2: int) -> bool:
        if self.edges.get(id1).get(id2) is None and id1 in self.nodes and id2 in self.nodes:
            m, n, d = self.equationAndDist(id1, id2)
            edge = Edge(id1, id2, d, m, n)
            if edge.getDist() < self.min_dist:
                self.min_dist = edge.getDist()

            self.edges.get(id1)[id2] = edge
            self.edges.get(id2)[id1] = edge
            self.nodes[id1].edges = self.nodes[id1].edges + 1
            self.nodes[id2].edges = self.nodes[id2].edges + 1

            self.mc = self.mc + 1
            return True
        return False

    # def add_node(self, node_id: int,pos: tuple=None,r:float=-1,b:float=-1) -> bool:
    #     if self.nodes.get(node_id) is None:
    #         node = Node(node_id, pos,r,b)
    #         self.nodes[node_id]=node
    #         self.edges[node_id]={}
    #         self.mc = self.mc + 1
    #         return True
    #     return False

    def add_node(self, n: Node) -> bool:
        if self.nodes.get(n.getId()) is None:
            sumb = self.v_size() * self.avgB
            sumb += n.getB()
            sumr = self.v_size() * self.avgR
            sumr += n.getR()
            self.nodes[n.getId()] = n
            self.edges[n.getId()] = {}
            self.mc = self.mc + 1
            if n.getR()>self.maxR:
                self.maxR = n.getR()
            self.avgB = sumb / self.v_size()
            self.avgR = sumr / self.v_size()
            return True
        return False

    def remove_node(self, node_id: int) -> bool:
        if node_id not in self.nodes.keys():
            return False
        self.mc = self.mc + len(self.edges[node_id])
        indexes = []
        for i in self.edges.get(node_id).keys():
            indexes.append(i)
        for i in indexes:
            self.remove_edge(node_id, i)
        del self.edges[node_id]
        del self.nodes[node_id]
        self.mc = self.mc + 1
        return True

    def remove_edge(self, node_id1: int, node_id2: int) -> bool:
        if self.edges.get(node_id1).get(node_id2) is None or self.nodes[node_id1] is None or self.nodes[
            node_id2] is None:
            return False
        del self.edges.get(node_id1)[node_id2]
        del self.edges.get(node_id2)[node_id1]
        self.nodes[node_id1].edges = self.nodes[node_id1].edges - 1
        self.nodes[node_id2].edges = self.nodes[node_id2].edges - 1
        self.mc = self.mc + 1
        return True

    def save_to_json(self, file_name: str) -> bool:
        class JsonGraph():
            def __init__(self, g: Graph):
                self.Edges = []
                for e in g.get_all_edges():
                    edge = {}
                    edge["p1"] = e.getP1()
                    edge["p2"] = e.getP2()
                    self.Edges.append(edge)
                self.Nodes = []
                for n in g.nodes.values():
                    node = {}
                    node["id"] = n.getId()
                    if (n.getLocation() is not None):
                        x, y = n.getLocation()
                        node["x"] = x
                        node["y"] = y
                    node["r"] = n.getR()
                    node["b"] = n.getB()

                    self.Nodes.append(node)

        toSave = JsonGraph(self)
        with open(file_name + ".json", "w") as f:
            json.dump(toSave, fp=f, indent=4, default=lambda o: o.__dict__)
        return True

    def __str__(self):
        return f"Graph: |V|={self.v_size()}, |E|={self.e_size()}"
# p1=Node(1,(0,3),8,9)
# p2=Node(2,(0,8),5,29)
# p3=Node(3,(3,8),7,9)
# g= Graph('yyy')
# print(g.get_all_nodes())
# print(g.get_all_edges())
# g1= Graph()
# print(g1.add_node(p1))
# print(g1.add_node(p2))
# print(g1.add_node(p3))
# print(g1.add_edge(1,2))
# print(g1.add_edge(3,2))
# print(g1.add_edge(1,3))
# g1.remove_edge(3,1)
# print(g1.get_all_nodes())
# print(g1.get_all_edges())
# g1.save_to_json("yyy")

