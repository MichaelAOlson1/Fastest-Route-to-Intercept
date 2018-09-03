import json
import requests
import re

# Constants
GOOGLE_MAPS_API = "https://maps.googleapis.com/maps/api/directions/json?" 
start = ["XXX", "XXX"]
stop = ["XXX", "XXX"]
third_point = ["XXX", "XXX"]

# Returns a JSON-formatted string from the Google APi
def url_request(start, stop):
    return requests.get(GOOGLE_MAPS_API + \
                        "origin=" + start[0] + "," \
                                  + start[1] + \
                        "&destination=" + stop[0] + "," \
                                        + stop[1] + \
                        "&travelMode=DRIVING" + \
                        "&avoid=tolls")

def sub_route(start, stop):
    min_distance = float(999999.99)
    min_candidate = float(999999.99)
    min_location = ("0.0", "0.0")
    print "Entered sub_route...", start, stop
    if not json.loads(url_request(start, stop).text):
        return min_candidate, min_location
    if not json.loads(url_request(start, stop).text)['routes']:
        return min_candidate, min_location
    data = json.loads(url_request(start, stop).text)['routes'][0]
    legs = data['legs'][0]
    route_distance = float(re.sub("[a-zA-Z\ ]", "", legs['distance']['text']))
    
    for step in legs['steps']:   
        # Check if endpoints are over 10 miles apart (again)
        if re.sub("[0-9. ]", "", step['distance']['text']) == "mi":
            if float(re.sub("[a-zA-Z\ ]", "", step['distance']['text'])) > 10.0:
                print "Possibly problematic endpoints - over 10 miles apart:"
                print "(", step['start_location']['lat'], ",", step['start_location']['lng'], ")", \
                      ", (", step['end_location']['lat'], ",", step['end_location']['lng'], ")"
    
    # Print directions
    print re.sub('<[^>]+>', ' ', step['html_instructions'])

    # Determine route from third point to a point in the route
    point_in_route = (str(step['end_location']['lat']), str(step['end_location']['lng']))
    data = json.loads(url_request(third_point, point_in_route).text)
    if data is not None:
        if data['routes']:
            distance = data['routes'][0]['legs'][0]['distance']['text']
            min_candidate = float(re.sub("[a-zA-Z\ ]", "", distance))
            if min_candidate < min_distance:
                min_distance = min_candidate
                min_location = point_in_route
    return min_candidate, min_location


# MAIN
# Route the primary route
data = json.loads(url_request(start, stop).text)['routes'][0]
legs = data['legs'][0]
route_distance = float(re.sub("[a-zA-Z\ ]", "", legs['distance']['text']))
print "Total route distance = ", route_distance

# Find the shortest distance from third point
min_distance = float(999999.99)
for step in legs['steps']:
    # Check if endpoints are over 10 miles apart
    if re.sub("[0-9. ]", "", step['distance']['text']) == "mi":
        if float(re.sub("[a-zA-Z\ ]", "", step['distance']['text'])) > 10.0:
            min_candidate, location = sub_route((str(step['start_location']['lat']), \
                                                 str(step['start_location']['lng'])), \
                                                (str(step['end_location']['lat']), \
                                                 str(step['end_location']['lng'])))
            if min_candidate < min_distance:
                min_distance = min_candidate
                min_location = location
            continue

    # Print directions
    print re.sub('<[^>]+>', ' ', step['html_instructions']), step['start_location']

    # Determine route from third point to a point in the route
    point_in_route = (str(step['end_location']['lat']), str(step['end_location']['lng']))
    data = json.loads(url_request(third_point, point_in_route).text)
    if data is not None:
        if data['routes']:
            distance = data['routes'][0]['legs'][0]['distance']['text']
            min_candidate = float(re.sub("[a-zA-Z\ ]", "", distance))
            if min_candidate < min_distance:
                min_distance = min_candidate
                min_location = point_in_route

print "Minimum distance: ", min_distance, "miles, Located at: ", min_location


