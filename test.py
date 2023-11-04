import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456",
    database="cheapest_public_transport"
)

mycursor = mydb.cursor()

station_ids = input("Please type the station ids: ")
station_ids = station_ids.strip().split(",")

for i in range(len(station_ids)):
    query = f"INSERT INTO `order` (`route_id`,`station_id`,`order`) VALUES (143,{station_ids[i]},{i+1});"
    mycursor.execute(query)
    mydb.commit()