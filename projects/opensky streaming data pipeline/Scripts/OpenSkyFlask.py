#!/usr/bin/env python
import json
from kafka import KafkaProducer
from flask import Flask, request
import requests
import time 
import json

app = Flask(__name__)
producer = KafkaProducer(bootstrap_servers='kafka:29092')


def log_to_kafka(topic, event):
    producer.send(topic, json.dumps(event).encode())

properties = [
    'icao24',
    'callsign',
    'origin_country',
    'time_position',
    'last_contact',
    'longitude',
    'latitude',
    'baro_altitude',
    'on_ground',
    'velocity',
    'true_track',
    'vertical_rate',
    'sensors',
    'geo_altitude',
    'squawk',
    'spi',
    'position_source'
]

# @app.route("/")
# def default_response():
#     default_event = {'event_type': 'default'}
#     log_to_kafka('events', default_event)
#     return "This is the default response!\n"


@app.route("/get_planes")
def get_planes():
    # Try to get api
    response = requests.get("https://opensky-network.org/api/states/all", headers={'User-Agent': 'Mozilla/5.0'})
    if response.status_code == 200:   
        # Log to KAFKA, give success message
#         log_to_kafka("planes", response.text.encode())
        # Print to screen response 
        json_response = json.loads(response.text)
        list_response = json_response['states']
        planes = []
        return_str = ""
        for single_plane in list_response:
            single_plane_dict = dict(zip(properties, single_plane))
#             planes.append(single_plane_dict)
            return_str += str(single_plane_dict)
            return_str += "\n"
        
        return_str+= "\n Total planes: %d.\n" % (len(list_response) - 5)
        return(return_str)
    else:
        return("Error!") 

@app.route("/get_planes_loop")
def get_planes_loop():
    while True:
        # Read in tracked flights
        flights = []
        try:
            log_file = open("tracked_flights", "r")
            flights = log_file.read().splitlines()
            print("Tracking: %s" % flights)
            log_file.close()
        except: 
            print("No flights being tracked.")
        # Repeat every 60 seconds
        response = requests.get("https://opensky-network.org/api/states/all", headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:   
            # Log to KAFKA, give success message
            json_response = json.loads(response.text)
            list_response = json_response['states']
            for single_plane in list_response:
                single_plane_dict = dict(zip(properties, single_plane))
                if single_plane_dict['callsign'].strip() in flights:
                    print("Flight %s" % single_plane_dict['callsign'].strip())
                    print(single_plane_dict)
                log_to_kafka("planes", single_plane_dict)
#                 print("\tLogged Plane %d" % i)
            print("\tDone one loop (%d planes)\n" % len(list_response))
        else:
            return("Error!")
        time.sleep(60)
    return("Exited loop!")

# Get callsign
@app.route("/post_flight", methods=['GET'])
def post_flight():
    # Check if callsign exists
    flight = request.args.get('callsign')
    # Create file or append if it exists
    with open("tracked_flights","a") as log_file:
        # Add new line
        flight = "%s\n" % flight.strip()
        # Write to file
        log_file.write(flight)
        log_file.close()
        # Return
        return("Tracking flight %s" % flight)
    