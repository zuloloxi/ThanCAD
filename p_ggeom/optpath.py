"""
 function Dijkstra(Graph, source):
 2      for each vertex v in Graph:           // Initializations
 3          dist[v] := infinity ;              // Unknown distance function from source to v
 4          previous[v] := undefined ;         // Previous node in optimal path from source
 5      end for ;
 6      dist[source] := 0 ;                    // Distance from source to source
 7      Q := the set of all nodes in Graph ;
        // All nodes in the graph are unoptimized - thus are in Q
 8      while Q is not empty:                 // The main loop
 9          u := vertex in Q with smallest dist[] ;
10          if dist[u] = infinity:
11              break ;                        // all remaining vertices are inaccessible from source
12          end if ;
13          remove u from Q ;
14          for each neighbor v of u:         // where v has not yet been removed from Q.
15              alt := dist[u] + dist_between(u, v) ;
16              if alt < dist[v]:             // Relax (u,v,a)
17                  dist[v] := alt ;
18                  previous[v] := u ;
19                  decrease-key v in Q;      // Reorder v in the Queue
20              end if ;
21          end for ;
22      end while ;
23      return dist[] ;
24  end Dijkstra.


1  S := empty sequence
2  u := target
3  while previous[u] is defined:
4      insert u at the beginning of S
5      u := previous[u]
"""

def findShortest(graph, source):
    """Find the shortest path between source and each one of all the vertices of the graph.

    The vertices which are inaccessible from source have infinity as their distance."""
    assert source in graph
    dist = {}
    previous = {}
    infinity = 1.0e100
    for v in graph:           # Initializations
        dist[v] = infinity                     # Unknown (for the moment) optimal path distance from vertex v to source
        previous[v] = None                     # Previous node in the optimal path from source to vertex v
    dist[source] = 0.0                         # Distance from source to source is zero
    Q = set(graph)                             # The set of all nodes in graph
    #All nodes in the graph are unoptimized - thus are in Q
    while len(Q) > 0:         # The main loop
        _, u = min((dist[v],v) for v in Q)
        if dist[u] >= infinity: break          #all remaining vertices are inaccessible from source
        Q.remove(u)
        for v in graph[u]:
            if v not in Q: continue            # where v has not yet been removed from Q.
            alt = dist[u] + graph.dist(u, v)
            if alt < dist[v]:                  # Relax (u,v,a)
                dist[v] = alt
                previous[v] = u
    return dist, previous


def routeTo(previous, target):
    """Finds the route between source vertex and and a target vertex.

    A call to findShortest(graph, source) with some source vertex, has computed the optimal
    paths from the source vertex to all other vertices of the graph.
    previous[v]: Previous node in the optimal path from source to vertex v, as computed by findSortest().
    S: The optimal path from source vertex to target vertex: source, v1, v2, v3, ..., vn-1, vn, target.
    """
    S = []
    u = target
    while u != None:
        S.insert(0, u)
        u = previous[u]
    return S


class GraphShortest(object):
    "A minimal graph object, to satisfy findShortest()."
    def __init__(self):
        self.graph = {}             #Contains the links of all nodes, as names: dict: string -> list of strings

    def __contains__(self, aa):
        "Check if node is in the graph."
        return aa in self.graph

    def __iter__(self):
        "Return an iterator to the nodes."
        return self.graph.iterkeys()

    def __getitem__(self, aa):
        "Return the links of aa."
        return self.graph[aa]

    def dist(self, aa, ab):
        """Return the distance between aa and ab, where it is known that the link aa -> ab exists.

        Here we assume that two linked vertices have distance 1."""
        return 1.0
