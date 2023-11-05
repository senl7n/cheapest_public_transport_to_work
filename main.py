from py2neo import Graph, Node, Relationship
import heapq

graph = Graph("bolt://localhost:7687", auth=("neo4j", "123456789"))

# get all stations and lines
stations = graph.run("MATCH (s:Station) RETURN s.name AS name").data()
lines = graph.run("MATCH (l:Line) RETURN l.name AS name, l.cost AS cost").data()


# use dijkstra algorithm to find the cheapest way
def shortest_path():
    return
