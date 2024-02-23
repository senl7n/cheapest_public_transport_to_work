import random

from py2neo import Graph

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
    path_info = {}
    while current_node is not None:
        path.append(current_node)
        next_node = cheapest_paths[current_node][0]
        line_used = cheapest_paths[current_node][2]  # get the line used
        path_info[current_node] = line_used
        current_node = next_node
    path = path[::-1]

    return path, path_info


def quickest_way(graph_structure, start, end):
    quickest_paths = {start: (None, 0, None)}  # {node: (predecessor, time, line)}
    current_node = start
    visited = set()

    while current_node != end:
        visited.add(current_node)
        destinations = set(graph_structure[current_node]) - visited
        time_to_current_node, current_line = quickest_paths[current_node][1], quickest_paths[current_node][2]

        for next_node in destinations:
            for line, _ in graph_structure[current_node][next_node].items():
                # Add time only if switching lines
                time_for_line = random.randint(3, 6)
                new_time = time_to_current_node + time_for_line

                # Add additional time if there is a line change
                if current_line and line != current_line:
                    new_time += random.randint(5, 10)  # additional time for line change

                if next_node not in quickest_paths or quickest_paths[next_node][1] > new_time:
                    quickest_paths[next_node] = (current_node, new_time, line)

        next_destinations = {node: quickest_paths[node] for node in quickest_paths if node not in visited}
        if not next_destinations:
            return None

        # next node is the destination with the lowest time
        current_node = min(next_destinations, key=lambda k: next_destinations[k][1])

    # get the complete path
    path = []
    path_info = {}
    while current_node is not None:
        path.append(current_node)
        next_node = quickest_paths[current_node][0]
        time_used = quickest_paths[current_node][1]  # get the time used
        path_info[current_node] = time_used
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

# if there is no transfer point, append "None"
if len(transfer_points) == 0:
    transfer_points.append("None")

# get the lines in order
lines_in_order = [line for station, line in path_info.items() if line is not None]

unique_lines_in_order = []
seen_lines = set()
for line in lines_in_order:
    if line not in seen_lines:
        unique_lines_in_order.append(line)
        seen_lines.add(line)

# reverse the list
reversed_unique_lines = unique_lines_in_order[::-1]
ordered_unique_lines = " -> ".join(reversed_unique_lines)

ordered_cheapest_path = " -> ".join(cheapest_path)

# print the result
print(f"Cheapest Route: {ordered_cheapest_path}")
print(f"Start Station: {start_station}; Transfer Station: {' | '.join(transfer_points)}; End Station: {end_station}")
print(f"Line Used: {ordered_unique_lines}")
print(f"Price: {total_cost}")

# find the quickest way
quickest_path, path_info = quickest_way(graph_data, start_station, end_station)


# calculate the total time and transfer points
def calculate_total_time_and_transfers(quickest_path, path_info):
    total_time = 0
    current_line = None
    transfer_points = []

    for i in range(len(quickest_path) - 1):
        start_station = quickest_path[i]
        end_station = quickest_path[i + 1]
        line_used = path_info[start_station]

        if line_used != current_line:
            if current_line is not None:  # if not the first line
                for j in range(i, len(quickest_path)):
                    if path_info[quickest_path[j]] != current_line:
                        transfer_points.append(quickest_path[j - 1])
                        break
            current_line = line_used
            time_for_line = random.randint(3, 6)
            total_time += time_for_line

            if current_line is not None:  # if not the first line
                total_time += random.randint(5, 10)  # additional time for line change

    return total_time, transfer_points


total_time, transfer_points = calculate_total_time_and_transfers(quickest_path, path_info)

# if there is no transfer point, append "None"
if len(transfer_points) == 0:
    transfer_points.append("None")

# get the lines in order
lines_in_order = [line for station, line in path_info.items() if line is not None]

unique_lines_in_order = []
seen_lines = set()
for line in lines_in_order:
    if line not in seen_lines:
        unique_lines_in_order.append(line)
        seen_lines.add(line)

# reverse the list
reversed_unique_lines = unique_lines_in_order[::-1]
ordered_unique_lines = " -> ".join(str(line) for line in reversed_unique_lines)

ordered_quickest_path = " -> ".join(quickest_path)

# print the result
print(f"Quickest Route: {ordered_quickest_path}")
print(f"Start Station: {start_station}; Transfer Station: {' | '.join(transfer_points)}; End Station: {end_station}")
print(f"Line Used: {ordered_unique_lines}")
print(f"Total Time: {total_time}")
