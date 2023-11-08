from py2neo import Graph, Node, Relationship

graph = Graph("bolt://localhost:7687", auth=("neo4j", "123456789"))

# get all stations and lines
stations = graph.run("MATCH (s:Station) RETURN s.name AS name").data()
lines = graph.run("MATCH (l:Line) RETURN l.name AS name, l.cost AS cost").data()


# use dijkstra algorithm to find the cheapest way
def cheapest_way(graph_structure, start, end):
    cheapest_paths = {start: (None, 0)}  # {node: (predecessor, weight)}
    current_node = start
    visited = set()

    while current_node != end:
        visited.add(current_node)
        destinations = [node for node in graph_structure if node not in visited]
        weight_to_current_node = cheapest_paths[current_node][1]
        print("cheapest paths: ", cheapest_paths)

        for next_node in destinations:
            if next_node in graph_structure[current_node]:  # Check if next_node is a valid destination
                print("cheapest paths: ", cheapest_paths)
                print("current node: ", current_node)
                print("next node: ", next_node)
                weight = graph_structure[current_node][next_node] + weight_to_current_node
                print("weight: ", weight)
                if next_node not in cheapest_paths:
                    cheapest_paths[next_node] = (current_node, weight)
                else:
                    current_shortest_weight = cheapest_paths[next_node][1]
                    if current_shortest_weight > weight:
                        cheapest_paths[next_node] = (current_node, weight)

        next_destinations = {node: cheapest_paths[node] for node in cheapest_paths if node not in visited}
        if not next_destinations:
            return None

        # next node is the destination with the lowest weight
        current_node = min(next_destinations, key=lambda k: next_destinations[k][1])

    # get the complete path
    path = []
    while current_node is not None:
        path.append(current_node)
        next_node = cheapest_paths[current_node][0]
        current_node = next_node
    path = path[::-1]
    return path


# define the graph based on the data in the database
graph_data = {}

for station in stations:
    station_name = station['name']
    graph_data[station_name] = {}

    # find all connections (using ROUTE relationship) and their costs from the current station
    connected_stations = graph.run(f"""
    MATCH (s:Station {{name: '{station_name}'}})-[:ROUTE]->(dest:Station)-[r:BELONGS_TO]->(l:Line)
    WHERE (s)-[:BELONGS_TO]->(l)
    RETURN dest.name AS destination, l.cost AS cost
    """).data()

    for connection in connected_stations:
        dest_name = connection['destination']
        cost = connection['cost']
        graph_data[station_name][dest_name] = cost
print(graph_data)

# # get the start and end station
# start_station = input("Please type the start station: ")
# end_station = input("Please type the end station: ")

# find the cheapest way
cheapest_path = cheapest_way(graph_data, "A", "D")

# print the result
print("cheapest route：", cheapest_path)
print("transfer points：", cheapest_path[1:-1] if len(cheapest_path) > 2 else [])
print(f"price：{sum([graph_data[cheapest_path[i]][cheapest_path[i+1]] for i in range(len(cheapest_path)-1)])}")

# debugging area
test_stations = graph.run("MATCH (s:Station) RETURN s.name AS name LIMIT 10").data()
print("test stations:", test_stations)
print("test lines:", lines)
print("test graph: ", graph_data)
print("test whole path: ", ["A"] + cheapest_path + ["D"])
