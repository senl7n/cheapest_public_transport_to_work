import heapq


# use dijkstra algorithm to find the cheapest way
def dijkstra(graph, start, end):
    queue = [(0, start, [])]
    seen = set()
    while queue:
        (cost, node, path) = heapq.heappop(queue)
        if node not in seen:
            seen.add(node)
            path = path + [node]
            if node == end:
                return cost, path
            for (next_node, c) in graph[node].items():
                if next_node not in seen:
                    heapq.heappush(queue, (cost + c, next_node, path))


# define the graph
graph = {
    "Line1-A": {"Line1-B": 2},
    "Line1-B": {"Line1-C": 2, "Line3-F": 3},
    "Line1-C": {"Line1-E": 2, "Line2-F": 4},
    "Line1-E": {"Line1-F": 2},
    "Line1-F": {"Line1-G": 2, "Line2-G": 4, "Line3-H": 3},
    "Line1-G": {"Line1-H": 2},
    "Line1-H": {"Line2-D": 4, "Line3-I": 3},
    "Line2-C": {"Line2-F": 4},
    "Line2-F": {"Line2-G": 4, "Line1-G": 2, "Line3-H": 3},
    "Line2-G": {"Line2-H": 4},
    "Line2-H": {"Line2-D": 4, "Line1-H": 2, "Line3-I": 3},
    "Line2-D": {},
    "Line3-B": {"Line3-F": 3},
    "Line3-F": {"Line3-H": 3, "Line1-G": 2, "Line2-G": 4},
    "Line3-H": {"Line3-I": 3, "Line1-H": 2, "Line2-D": 4},
    "Line3-I": {"Line3-J": 3},
    "Line3-J": {"Line3-D": 3},
    "Line3-D": {}
}

cost, path = dijkstra(graph, "Line1-A", "Line3-D")

# find the transfer points
transfer_points = []
for i in range(1, len(path) - 1):
    if path[i].split('-')[0] != path[i+1].split('-')[0]:
        transfer_points.append(path[i].split('-')[1])

print("cheapest route：", path)
print("transfer points：", transfer_points)
print("price：", cost)
