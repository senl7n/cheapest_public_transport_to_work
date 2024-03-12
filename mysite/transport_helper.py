import json
import random

from py2neo import Graph


class Helper:
    def __init__(self, db_host="bolt://localhost:7687", db_user="neo4j", db_password="123456789"):
        self.graph = Graph(db_host, auth=(db_user, db_password))
        self.stopNames = self.graph.run("MATCH (s:stopName) RETURN s.name AS name").data()
        self.routeNames = self.graph.run("MATCH (l:routeName) RETURN l.name AS name, l.price AS price").data()
        self.graph_data = {}
        self.stations = self.load_data_from_json()

        # define the graph based on the data in the database
        for stop in self.stopNames:
            stop_name = stop['name']
            self.graph_data[stop_name] = {}

            connected_stations = self.graph.run("""
                MATCH (s:stopName {name: $stop_name})-[r:ROUTE]->(dest:stopName)
                MATCH (l:routeName {name: l.name})
                RETURN dest.name AS destination, l.name AS route, l.price AS price
            """, stop_name=stop_name).data()

            for connection in connected_stations:
                dest_name = connection['destination']
                route_name = connection['route']
                price = connection['price']

                if dest_name not in self.graph_data[stop_name]:
                    self.graph_data[stop_name][dest_name] = {}

                self.graph_data[stop_name][dest_name][route_name] = price

    # use dijkstra algorithm to find the cheapest way with line switching cost
    def cheapest_way(self, start, end):
        cheapest_paths = {start: (None, 0, None)}  # {node: (predecessor, weight, line)}
        current_node = start
        visited = set()

        while current_node != end:
            visited.add(current_node)
            destinations = set(self.graph_data[current_node]) - visited
            weight_to_current_node, current_line = cheapest_paths[current_node][1], cheapest_paths[current_node][2]

            for next_node in destinations:
                for line, cost in self.graph_data[current_node][next_node].items():
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

    def quickest_way(self, start, end):
        quickest_paths = {start: (None, 0, None)}  # {node: (predecessor, time, line)}
        current_node = start
        visited = set()

        while current_node != end:
            visited.add(current_node)
            destinations = set(self.graph_data[current_node]) - visited
            time_to_current_node, current_line = quickest_paths[current_node][1], quickest_paths[current_node][2]

            for next_node in destinations:
                for line, _ in self.graph_data[current_node][next_node].items():
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
        # path_info is used to store the line used for each station
        path = []
        path_info = {}
        while current_node is not None:
            path.append(current_node)
            next_node = quickest_paths[current_node][0]
            line_used = quickest_paths[current_node][2]
            path_info[current_node] = line_used
            current_node = next_node
        path = path[::-1]

        return path, path_info

    def calculate_total_cost_and_transfers(self, cheapest_path, path_info):
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
                cost = self.graph_data[start_station][end_station][line_used]
                total_cost += cost

        return total_cost, transfer_points

    def calculate_total_time_and_transfers(self, quickest_path, path_info):
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

    def get_ordered_lines(self, path_info, path):
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

        ordered_cheapest_path = " -> ".join(path)

        return ordered_cheapest_path, ordered_unique_lines

    def load_data_from_json(self, source_file="station_data.json"):
        with open(source_file, 'r', encoding='utf-8') as f:
            stations = json.loads(f.read())
            return stations

if __name__ == "__main__":
    csv_file_path = '../choosed_bus_stops.csv'
    helper = Helper()
    # get the start and end station
    start_station = input("Please type the start station: ")
    end_station = input("Please type the end station: ")

    # find the cheapest way
    cheapest_path, path_info = helper.cheapest_way(start_station, end_station)

    # calculate the total cost and transfer points

    total_cost, transfer_points = helper.calculate_total_cost_and_transfers(cheapest_path, path_info)

    if len(transfer_points) == 0:
        transfer_points.append("None")

    # find the quickest way
    quickest_path, path_info = helper.quickest_way(start_station, end_station)

    # calculate the total time and transfer points

    total_time, transfer_points = helper.calculate_total_time_and_transfers(quickest_path, path_info)

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
