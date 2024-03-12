import json
import sys

sys.path.insert(0, './transport_helper.py')
from django.shortcuts import render
from django.http import JsonResponse
from transport_helper import Helper

helper = Helper()


# Create your views here.
def index(request):
    return render(request, 'index.html', context={"line_data": helper.stations, "stops": helper.get_all_stops()})


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


def process_route(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        start_station = data.get('start')
        end_station = data.get('end')
        option = data.get('option')
        total_cost = None
        total_time = None

        # Check if the user provided both start and end stations and they are not empty.
        if start_station and end_station and start_station.strip() != "" and end_station.strip() != "":
            try:
                if option == "cheapest":
                    path, path_info = helper.cheapest_way(start_station, end_station)
                    total_cost, transfer_points = helper.calculate_total_cost_and_transfers(path, path_info)
                elif option == "quickest":
                    path, path_info = helper.quickest_way(start_station, end_station)
                    total_time, transfer_points = helper.calculate_total_time_and_transfers(path, path_info)
                else:
                    return JsonResponse({
                        "ret": 0,
                        "msg": "Invalid option. Please provide a valid option."
                    })
            except Exception as e:
                return JsonResponse({
                    "ret": 0,
                    "msg": f"Please enter valid start and end stations."
                })
            else:
                route, line_used = helper.get_ordered_lines(path_info, path)
                transfer_points_str = " -> ".join(transfer_points)
                return JsonResponse({
                    "ret": 1,
                    "msg": f"Route processed.",
                    "start": start_station,
                    "end": end_station,
                    "option": option,
                    "total_cost": None if option == "quickest" else total_cost,
                    "total_time": None if option == "cheapest" else total_time,
                    "transfer_points": transfer_points_str,
                    "route": route,
                    "line_used": line_used
                })
        else:
            # If the user didn't provide both start and end stations or they are empty, return an error message.
            return JsonResponse({
                "ret": 0,
                "msg": "Please enter both start and end stations and they should not be empty."
            })
