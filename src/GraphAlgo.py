import GraphInterface
from GraphAlgoInterface import GraphAlgoInterface
from DiGraph import DiGraph
import matplotlib.pyplot as plt
import copy
import math
import json
import sys


class GraphAlgo(GraphAlgoInterface):
    """
      A class that contains algorithms that could be done on graphs
    ...

    Attributes
    ----------
    graph : DiGraph
        object representing a graph

    edgesList :  list
        all edges represented by tuple => (src, dest, weight)

    nodesDict : dict
        all nodes represented by dict => {id:pos}

    Methods
    -------
    get_graph()
        Returns a graph that implements GraphInterface

    load_from_json(file_name: str)
        loads a graph object to class from json
        Returns true if successful

    save_to_json(file_name: str)
        Saves the graph in JSON format to a file
        Returns true if successful

    shortest_path( src: int, dest: int)
        calculate the shortest path from node src to node dest using Dijkstra's Algorithm
        Returns The distance of the path, and a list of the nodes ids that the path goes through

    connected_component(node_id: int)
        Finds the Strongly Connected Component(SCC) that node node_id is a part of.
        Returns The list of nodes in the SCC

    connected_component()
        Finds all the Strongly Connected Component(SCC) in the graph.
        Returns The list all SCC

    def plot_graph()
        Plots the graph.
        If the nodes have a position, the nodes will be placed there.
        Otherwise, they will be placed spraed on a circle.
    """

    def __init__(self, graph=None):
        """
        Parameters
        ----------
            graph : a class that implements GraphInterface
            
            edgesList :  list of all edges represented by tuple => (src, dest, weight)

            nodesDict : dict of all nodes represented by dict => {id:pos}

        """
        self.graph = graph if graph is not None else DiGraph()
        self.edgesList = []
        self.nodesDict = {}
        self.loadGraph = False
        # TODO manage edgesList nodesDict

    def get_graph(self) -> GraphInterface:
        """
        Returns
        -------
        GraphInterface
            the directed graph on which the algorithm works on.
        """
        return self.graph

    def set_graph(self, g: DiGraph) -> None:
        """
        Returns
        -------
        GraphInterface
            the directed graph on which the algorithm works on.
        """
        self.graph = g
        self.loadGraph = False

    def load_from_json(self, filePath: str) -> bool:
        """
        loads a graph from a text file

        Parameters
        ----------
        filePath: str
            address to the text file
        
        makeTuple: bool
            if 

        Returns
        -------
        bool
            a flag used to indicate if the graph's load was successful
        """
        try:
            self.nodesDict = {}
            self.edgesList = []
            g = DiGraph()
            with open(filePath, "r") as graphJson:
                graphObj = json.load(graphJson)

                # init nodes
                for node in graphObj["Nodes"]:
                    # init pos
                    pos = None
                    if 'pos' in node and node["pos"] is not None:
                        coordinate = node["pos"].split(",")
                        pos = (float(coordinate[0]), float(coordinate[1]))
                        self.nodesDict.update({node['id']: pos})
                    else:
                        self.nodesDict.update({node['id']: None})

                    # add node to graph
                    g.add_node(node["id"], pos)

                # init edges
                for edge in graphObj["Edges"]:
                    self.edgesList.append((edge["src"], edge["dest"]))

                    g.add_edge(edge["src"], edge["dest"], edge["w"])

                graphJson.close()
                self.graph = g
                self.loadGraph = True
                return True

        except IOError as e:
            print("Couldn't open or read the file (%s)." % e)
            return False

    def save_to_json(self, filePath: str) -> bool:
        """
        Saves the graph in JSON format to a file

        Parameters
        ----------
        filePath: str
            address to the out file

        Returns
        -------
        bool
            a flag used to indicate if the graph's load was successful

        """
        # make graphObj suitable for json format
        graphObj = {"Nodes": [], "Edges": []}
        g = self.graph

        # TODO check if graph can be null
        if g is None:
            return False

        nodes = g.get_all_v()
        for key in nodes:
            a = nodes[key]
            posTuple = nodes[key]["pos"]

            pos = None
            if posTuple is not None:
                pos = ','.join(map(str, posTuple))

            graphObj["Nodes"].append({"id": key, "pos": pos})

            neighbors = g.all_out_edges_of_node(key)
            for neiKey in neighbors:
                graphObj["Edges"].append({'src': key, 'w': neighbors[neiKey], 'dest': neiKey})

        try:
            with open(filePath, 'w') as graphJson:
                json.dump(graphObj, graphJson, indent=4)

                graphJson.close()

                return True

        except IOError as e:
            print("Couldn't open or write to file (%s)." % e)
            return False
        json.load(graphJson)

    def shortest_path(self, src: int, dest: int) -> (float, list):
        """
        calculate the shortest path from node src to node dest using Dijkstra's Algorithm
        Parameters
        ----------
        src: int
            The start node id

        dest: int
            The end node id

        Returns
        -------
        float
            The distance of the path
        list
            a list of the nodes ids that the path goes through

        """
        # if the graph is none.
        if self.graph is None:
            return float('inf'), []

        # if one of those nodes is not in the graph.
        if src not in self.graph.nodes.keys() or dest not in self.graph.nodes.keys():
            return float('inf'), []

        self.dijkstra(src, dest)

        if self.graph.nodes[dest]["tag"] == sys.maxsize:
            return float('inf'), []

        temp = self.graph.nodes[dest]
        path = [dest]

        while temp["prev"] is not None:
            path.append(temp["prev"])
            temp = self.graph.nodes[temp["prev"]]

        path.reverse()
        path_length = self.graph.nodes[dest]["tag"]

        # before the end, the variables that holds info in this function need to be set to default.
        for node in self.graph.nodes.keys():
            self.graph.nodes[node]["tag"] = 0
            self.graph.nodes[node]["prev"] = None

        return path_length, path

    def connected_component(self, node_id: int) -> list:
        """
         Finds the Strongly Connected Component(SCC) that node node_id is a part of.

        Parameters
        ----------
        node_id: int
            node unique key

        Returns
        -------
        list
            a list of nodes in the
        """
        # empty graph, or node in that graph.
        if self.graph.v_size() == 0 or node_id not in self.graph.nodes.keys() or self.graph is None:
            return []
        # f there is only one node in the graph.
        if self.graph.v_size() == 1:
            return [node_id]

        # else, call tge heavy shit!!
        scc_of_graph = self.connected_components()

        # check at the returned SCC where node_id is.
        # check at the returned SCC's where id1 is.
        for component in scc_of_graph:
            if node_id in component:
                return component

        # when finished, set back the values used to deafult.
        for node in self.graph.nodes.keys():
            self.graph.nodes[node]["for_scc"] = {"index": -1, "low_link": node, "on_stack": False}

        return []

    def connected_components(self) -> list[list]:
        """
        Finds all the Strongly Connected Component(SCC) in the graph.

        Returns
        -------
        list
            a list all SCC (s list of lists),
            or an empty list if the graph is None.
        """

        # empty graph, or node in that graph.
        if self.graph is None or self.graph.v_size() == 0:
            return []

        # initialize some variables
        index = 0
        stack = []
        sc_comp = []

        # helper function.
        # recursive function that dfs over the tree.
        # it does it with some changes to fit our goal of finding SCC
        def strong_connect(node_id: int) -> list:
            nonlocal index
            nonlocal stack
            nonlocal sc_comp

            self.graph.nodes[node_id]["for_scc"]["index"] = index
            self.graph.nodes[node_id]["for_scc"]["low_link"] = index
            index += 1
            stack.append(node_id)
            self.graph.nodes[node_id]["for_scc"]["on_stack"] = True

            # Consider successors of node_id
            for neighbor in self.graph.edges["From"][node_id].keys():
                if self.graph.nodes[neighbor]["for_scc"]["index"] == -1:
                    # Successor w has not yet been visited; recurse on it
                    sc_comp.append(strong_connect(neighbor))
                    self.graph.nodes[node_id]["for_scc"]["low_link"] = min(
                        self.graph.nodes[node_id]["for_scc"]["low_link"],
                        self.graph.nodes[neighbor]["for_scc"]["low_link"])
                elif self.graph.nodes[neighbor]["for_scc"]["on_stack"]:
                    # Successor neighbor is in stack, and hence in the current SCC
                    # If w is not on stack, then (node_id, neighbor) is an edge pointing to an SCC already found and must be ignored
                    # Note: The next line may look odd - but is correct.
                    # It says w.index not w.lowlink; that is deliberate and from the original paper
                    self.graph.nodes[node_id]["for_scc"]["low_link"] = min(
                        self.graph.nodes[node_id]["for_scc"]["low_link"],
                        self.graph.nodes[neighbor]["for_scc"]["index"])

            # if node_id is a root node, pop the stack and generate an SCC
            if self.graph.nodes[node_id]["for_scc"]["low_link"] == self.graph.nodes[node_id]["for_scc"]["index"]:
                temp = []

                while True:
                    w = stack.pop()
                    self.graph.nodes[w]["for_scc"]["on_stack"] = False
                    temp.append(w)
                    if node_id == w:
                        break

                # it will return the SCC for node_id
                # for element in temp:
                #     if element == []:
                #         temp.remove(element)
                return temp

        for node in self.graph.nodes.keys():
            if self.graph.nodes[node]["for_scc"]["index"] == -1:
                sc_comp.append(strong_connect(node))

        ans = []

        for component in sc_comp:
            if component is not None and component.__sizeof__() != 0:
                ans.append(component)

        # when finished set back the values used to deafult.
        for node in self.graph.nodes.keys():
            self.graph.nodes[node]["for_scc"] = {"index": -1, "low_link": node, "on_stack": False}

        return ans

    def plot_graph(self, setTimer: bool = False, graphName: str = None) -> None:
        """
        Plots the graph.
        If the nodes have a position, the nodes will be placed there.
        Otherwise, they will be placed in a random but elegant manner.
        @return: None
        """
        # graph data
        if self.loadGraph:
            nodes = self.nodesDict
            edges = self.edgesList
        else:
            nodes = copy.deepcopy(self.graph.get_all_v())
            for key in nodes:
                nodes.update({key: nodes[key]['pos']})
            edges = self.graph.get_all_e()

        nodeSize = len(nodes)

        if graphName is None:
            graphName = 'Graph with '+ str(nodeSize) + ' Nodes, and ' + str(len(edges)) + 'Edges'
        plt.ylabel('y axes')
        plt.xlabel('x axes')
        plt.title(graphName)
        # TODO is ok?
        if len(nodes) == 0:
            return

        # plot graph
        if nodeSize > 1000:

            # TODO if node have no pos

            self.spreadEvenly(nodes)

            # draw edges
            for e in edges:
                # edge data
                src = e[0]
                dest = e[1]
                # w = e[2]

                # get coordinates
                srcX = nodes[src][0]
                srcY = nodes[src][1]
                destX = nodes[dest][0]
                destY = nodes[dest][1]

                # TODO check if line right
                # draw nodes and edges
                lineX, lineY = [srcX, destX], [srcY, destY]
                plt.plot(lineX, lineY, color='k', zorder=0, marker='o')

                # TODO draw nodes with no edges
                # draw nodes with no edges

        else:
            # TODO make func return border
            borders = self.spreadInCircle(nodes)

            # ---draw graph---

            # node size
            windowLen = min(borders[0], borders[1])

            nodeRadius = windowLen / (25)

            for key in nodes:
                # draw nodes
                x = nodes[key][0]
                y = nodes[key][1]

                circle = plt.Circle((x, y), label=key, edgecolor='k', facecolor='r', radius=nodeRadius / 2, zorder=5)
                plt.gcf().gca().add_artist(circle)

            # draw edges
            for e in edges:
                # edge data
                src = e[0]
                dest = e[1]
                # w = e[2]

                # get coordinates
                srcX = nodes[src][0]
                srcY = nodes[src][1]
                destX = nodes[dest][0]
                destY = nodes[dest][1]

                # draw a line (for a non-directed edge)
                if self.isDirectedE(src, dest):
                    lineX, lineY = [srcX, destX], [srcY, destY]
                    plt.plot(lineX, lineY, color='k', zorder=0)

                # draw an arrow (for a directed edge)
                else:
                    arrowLen = math.hypot(destY - srcY, destX - srcX)
                    if arrowLen != 0:
                        cosAngle = (destX - srcX) / arrowLen
                        sinAngle = (destY - srcY) / arrowLen
                        dx = (arrowLen - 2 * nodeRadius) * cosAngle
                        dy = (arrowLen - 2 * nodeRadius) * sinAngle
                        plt.arrow(srcX, srcY, dx, dy, head_width=nodeRadius, width=nodeRadius / 10, zorder=0)

        # TODO check if was already closed
        if setTimer:
            plt.show(block=False)
            plt.pause(1)
            plt.close()
        else:
            plt.show()

    def old_plot_graph(self) -> None:
        """
        Plots the graph.
        If the nodes have a position, the nodes will be placed there.
        Otherwise, they will be placed in a random but elegant manner.
        @return: None
        """
        if self.graph is None:
            return None

        # get nodes
        g = self.graph
        assert (isinstance(g, DiGraph))
        nodes = g.get_all_v()

        # initialize vars calculation
        i = 1
        maxX = maxY = -9999999
        minX = minY = 9999999

        # set a dict of nodes locations {id: pos}
        locations = {}
        for key in nodes:
            pos = nodes[key]['pos']

            # if node's location in None
            if pos is None:
                # calculate position of each node
                maxX = maxY = 2
                minY = minX = -2
                angle = math.radians(i * 360 / len(nodes))
                pos = (2 * math.cos(angle), 2 * math.sin(angle))

                i += 1

            # if node's location initialize
            else:
                nodeX, nodeY = float(pos[0]), float(pos[1])
                pos = tuple(pos)
                maxX, minX = max(maxX, nodeX), min(minX, nodeX)
                maxY, minY = max(maxY, nodeY), min(minY, nodeY)

            locations[key] = pos

        # set window size
        dx = (maxX - minX) / 4
        dy = (maxY - minY) / 4
        plt.xlim([minX - dx, maxX + dx])
        plt.ylim([minY - dy, maxY + dy])

        # draw graph
        r = min((maxY - minY), (maxX - minX)) * (3 / 80)
        for key in locations:
            # draw nodes
            x = float(locations[key][0])
            y = float(locations[key][1])
            circle = plt.Circle((x, y), label=key, edgecolor='k', facecolor='r', radius=r / 2, zorder=5)
            plt.gcf().gca().add_artist(circle)

            # draw edges
            for neiKey in g.all_out_edges_of_node(key).keys():
                # slope = (neiY - y) / (neiX - x)
                # arrowY = y + arrowLen * (slope / math.sqrt(1 + slope * slope))
                # arrowX = x + arrowLen * (1 / math.sqrt(1 + slope * slope))
                neiX = float(locations[neiKey][0])
                neiY = float(locations[neiKey][1])

                # draw a line (for a non-directed edge)
                if self.isDirectedE(neiKey, key):
                    lineX, lineY = [x, neiX], [y, neiY]
                    plt.plot(lineX, lineY, color='k', zorder=0)

                # draw an arrow (for a directed edge)
                else:
                    distance = math.hypot((neiY - y), (neiX - x))
                    cosAngle = (neiX - x) / distance
                    sinAngle = (neiY - y) / distance
                    dx = (distance - 2 * r) * cosAngle
                    dy = (distance - 2 * r) * sinAngle
                    plt.arrow(x, y, dx, dy, head_width=r, width=r / 10, zorder=0)

        plt.show()

    def spreadEvenly(self, nodes: dict) -> None:

        # set borders
        nSize = len(nodes)
        sqrtNodes = math.ceil(math.sqrt(nSize))
        plt.xlim([0, sqrtNodes])
        plt.ylim([0, sqrtNodes])

        # set positions
        row = i = 0
        while row < sqrtNodes:
            col = 0
            while col < sqrtNodes and i < nSize:
                if nodes[i] is None:
                    pos = (row + 0.5, col + 0.5)
                    nodes.update({i: pos})
                i += 1
                col += 1
            row += 1

    def spreadInCircle(self, nodes: dict) -> list:
        nSize = len(nodes)
        maxX = maxY = float('-inf')
        minX = minY = float('inf')

        # set positions
        hasLocations = False
        i, circleRadius, center = 0, math.sqrt(nSize), (0, 0)
        while i < nSize:
            pos = nodes[i]
            if pos is None:

                # if part of nodes have locations
                if not hasLocations:
                    windowLen = [0, 0]
                    border = min(windowLen[0], windowLen[1])
                    maxX = maxY = circleRadius
                    minX = minY = -circleRadius
                elif border > 0:
                    circleRadius = border
                    windowLen = [maxX - minX, maxY - minY]

                # calculate nodes positions
                center = (windowLen[0] / 2, windowLen[1] / 2)
                angle = math.radians(i * 360 / len(nodes))

                pos = (circleRadius * math.cos(angle) + center[0], circleRadius * math.sin(angle) + center[1])
                nodes[i] = pos
            else:
                maxX, minX = max(maxX, pos[0]), min(minX, pos[0])
                maxY, minY = max(maxY, pos[1]), min(minY, pos[1])

                hasLocations = True

            i += 1

        # set window size
        windowLen = [maxX - minX, maxY - minY]
        xMargin = windowLen[0] / 4
        yMargin = windowLen[0] / 4
        plt.xlim([minX - xMargin, maxX + xMargin])
        plt.ylim([minY - yMargin, maxY + yMargin])

        return windowLen

    def isDirectedE(self, src, dest) -> bool:
        return src in self.graph.edges['To'][dest] and src in self.graph.edges['From'][dest]

    def dfs(self, visited, node_id: int):
        if node_id not in visited:
            visited.add(node_id)
            for neighbor in self.graph.edges["From"][node_id]:
                self.dfs(visited, neighbor)

    # TODO is argument dest_node is needed
    def dijkstra(self, src_node, dest_node):
        """
            implementation of the Dijkstra algorithm for finding a shortest path
            from source to destination. applicable on directed weighted graphs.

            Parameters:
                src_node: int
                        the node we want to start from.
                dest_node: int
                        the node we want to go to.

            no returns. we make changes on the nodes variables and use it outside.
                dest_node.tag will be the weight of the shortest path.
                dest_node.prev will be the previous node in the shortest path.
        """
        # initially, all nodes are unvisited
        q = []

        # set all nodes distance to infinity,
        # and all prev to None.
        for node in self.graph.nodes.keys():
            self.graph.nodes[node]["tag"] = sys.maxsize
            self.graph.nodes[node]["prev"] = None
            q.append(node)

        # set the src_node to zero.
        self.graph.nodes[src_node]["tag"] = 0
        curr = src_node

        while len(q) > 0:
            # choose the minimum weigh in the graph edges
            temp = sys.maxsize
            for node in self.graph.nodes.keys():
                if self.graph.nodes[node]["tag"] < temp and node in q:
                    temp = self.graph.nodes[node]["tag"]
                    curr = node
            # in case all other node are not reachable
            if temp == sys.maxsize:
                curr = q.pop()
            else:
                q.remove(curr)
            # relaxation on the neighbors of curr.
            v_neighbors = {k: v for (k, v) in self.graph.edges["From"].items() if curr == k}
            for neighbor in v_neighbors[curr].keys():
                if (self.graph.nodes[curr]["tag"] + v_neighbors[curr][neighbor]) < self.graph.nodes[neighbor]["tag"]:
                    # update the distance
                    self.graph.nodes[neighbor]["tag"] = self.graph.nodes[curr]["tag"] + v_neighbors[curr][neighbor]
                    # update parent node
                    self.graph.nodes[neighbor]["prev"] = curr
