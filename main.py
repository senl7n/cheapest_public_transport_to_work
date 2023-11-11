from py2neo import Graph, Node, Relationship

graph = Graph("bolt://localhost:7687", auth=("neo4j", "123456789"))

# get all stations and lines
stations = graph.run("MATCH (s:Station) RETURN s.name AS name").data()
lines = graph.run("MATCH (l:Line) RETURN l.name AS name, l.cost AS cost").data()


# use dijkstra algorithm to find the cheapest way with line switching cost
def cheapest_way(graph_structure, start, end):
    cheapest_paths = {start: (None, 0, None)}  # {node: (predecessor, weight, line)}
    current_node = start
    visited = set()

    while current_node != end:
        visited.add(current_node)
        destinations = set(graph_structure[current_node]) - visited
        weight_to_current_node, current_line = cheapest_paths[current_node][1], cheapest_paths[current_node][2]

        for next_node in destinations:
            for line, cost in graph_structure[current_node][next_node].items():
                # Add cost only if switching lines
                new_cost = weight_to_current_node
                if line != current_line:
                    new_cost += cost

                if next_node not in cheapest_paths or cheapest_paths[next_node][1] > new_cost:
                    cheapest_paths[next_node] = (current_node, new_cost, line)

        next_destinations = {node: cheapest_paths[node] for node in cheapest_paths if node not in visited}
        if not next_destinations:
            return None

        # next node is the destination with the lowest weight
        current_node = min(next_destinations, key=lambda k: next_destinations[k][1])

    # get the complete path
    path = []
    path_info = {}  # This will store the path and the line used for each segment
    while current_node is not None:
        path.append(current_node)
        next_node = cheapest_paths[current_node][0]
        line_used = cheapest_paths[current_node][2]  # get the line used
        path_info[current_node] = line_used
        current_node = next_node
    path = path[::-1]

    return path, path_info


# define the graph based on the data in the database
graph_data = {}

for station in stations:
    station_name = station['name']
    graph_data[station_name] = {}

    connected_stations = graph.run(f"""
        MATCH (s:Station {{name: '{station_name}'}})-[r:ROUTE]->(dest:Station)
        MATCH (l:Line {{name: r.line}})
        RETURN dest.name AS destination, l.name AS line, l.cost AS cost
    """).data()

    for connection in connected_stations:
        dest_name = connection['destination']
        line_name = connection['line']
        cost = connection['cost']

        if dest_name not in graph_data[station_name]:
            graph_data[station_name][dest_name] = {}

        graph_data[station_name][dest_name][line_name] = cost

print("graph_data: ", graph_data)

# get the start and end station
start_station = input("Please type the start station: ")
end_station = input("Please type the end station: ")

# find the cheapest way
cheapest_path, path_info = cheapest_way(graph_data, start_station, end_station)


# calculate the total cost and transfer points
def calculate_total_cost_and_transfers(cheapest_path, path_info, graph_data):
    total_cost = 0
    current_line = None
    transfer_points = []

    for i in range(len(cheapest_path) - 1):
        start_station = cheapest_path[i]
        end_station = cheapest_path[i + 1]
        line_used = path_info[start_station]

        if line_used != current_line:
            if current_line is not None:  # if not the first line
                for j in range(i, len(cheapest_path)):
                    if path_info[cheapest_path[j]] != current_line:
                        transfer_points.append(cheapest_path[j - 1])
                        break
            current_line = line_used
            cost = graph_data[start_station][end_station][line_used]
            total_cost += cost

    return total_cost, transfer_points


total_cost, transfer_points = calculate_total_cost_and_transfers(cheapest_path, path_info, graph_data)

# print the result
print(f"cheapest route: {cheapest_path}")
print(f"transfer points: {transfer_points}")
print(f"price: {total_cost}")