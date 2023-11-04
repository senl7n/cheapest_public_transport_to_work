from py2neo import Graph, Node, Relationship
import heapq

graph = Graph("bolt://localhost:7687", auth=("neo4j", "123456789"))

# use dijkstra algorithm to find the cheapest way
