from py2neo import Graph, Node, Relationship

graph = Graph("bolt://localhost:7687", auth=("neo4j", "123456789"))

# get all stations and lines
stations = graph.run("MATCH (s:Station) RETURN s.name AS name").data()
lines = graph.run("MATCH (l:Line) RETURN l.name AS name, l.cost AS cost").data()


# use dijkstra algorithm to find the cheapest way
def shortest_path():
    return


# define the graph based on the data in the database
# graph_data = {}
# for station in stations:
#     graph_data[station['name']] = {}
#     belonging_lines = graph.run(f"MATCH (s:Station {{name: '{station['name']}'}})-[:BELONGS_TO]->(l:Line) RETURN "
#                                 f"l.name AS name, l.cost AS cost").data()
#     for line in belonging_lines:
#         for dest in stations:
#             if dest['name'] != station['name']:
#                 graph_data[station['name']][dest['name']] = line['cost']

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

# get the start and end station
start_station = input("Please type the start station: ")
end_station = input("Please type the end station: ")
