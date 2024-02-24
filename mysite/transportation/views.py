from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


def process_route(request):
    if request.method == 'POST':
        start_station = request.POST.get('start')
        end_station = request.POST.get('end')

        # Check if the user provided both start and end stations.
        if start_station and end_station:
            return HttpResponse("Route processed. Start station: {}. End station: {}.".format(start_station, end_station))
        else:
            # If the user didn't provide both start and end stations, return an error message.
            return render(request, 'index.html', {'error_message': 'Please enter both start and end stations.'})
