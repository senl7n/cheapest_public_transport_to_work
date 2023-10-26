import mysql.connector

# Connect to the database
db_connection = mysql.connector.connect(
    host="localhost",
    user="",
    password="",
    database=""
)

# Create a cursor
cursor = db_connection.cursor()

# Get the start and end station names from the user
start_station_name = input("Please type the start station name: ")
end_station_name = input("Please type the end station name: ")

# Get the start and end station IDs from the database
query = "SELECT station_id FROM Stations WHERE station_name = %s"
cursor.execute(query, (start_station_name,))
start_station_id = cursor.fetchone()

cursor.execute(query, (end_station_name,))
end_station_id = cursor.fetchone()

# Check if the start and end stations exist
if not start_station_id or not end_station_id:
    print("The start or end station does not exist.")
else:
    # Get the cheapest route and the cost

    # TODO: Find the cheapest route using Dijkstra's algorithm

    # Print the result

    # Close the cursor and database connection
    cursor.close()
    db_connection.close()
