import argparse

import csv

from datetime import datetime

from math import sin, cos, sqrt, atan2, radians
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np


def safe_float(value, default=0.0):
    try:
        return float(value)
    except ValueError:
        return default

class CitiBikeData:
    def __init__(self, ride_id, rideable_type, started_at, ended_at, start_station_name, start_station_id, end_station_name, end_station_id, start_lat, start_lng, end_lat, end_lng, member_casual):
        self.ride_id = ride_id
        self.rideable_type = rideable_type
        self.started_at = started_at
        self.ended_at = ended_at
        self.start_station_name = start_station_name
        self.start_station_id = start_station_id
        self.end_station_name = end_station_name
        self.end_station_id = end_station_id
        self.start_lat = safe_float(start_lat)
        self.start_lng = safe_float(start_lng)
        self.end_lat = safe_float(end_lat)
        self.end_lng = safe_float(end_lng)
        self.member_casual = member_casual

    def classify_event(self, most_busiest_stations, most_central_stations, most_frequent_routes, average_ride_duration):
        start_time = datetime.fromisoformat(self.started_at)
        end_time = datetime.fromisoformat(self.ended_at)
        duration = (end_time - start_time).seconds / 60
        route = (self.start_station_id, self.end_station_id)

        # Member rides on frequent routes
        if route in most_frequent_routes and self.member_casual == 'member':
            return 'A'
        # Rides on frequent routes
        elif route in most_frequent_routes:
            return 'B'
        # Very short-duration rides at busy stations
        elif duration < (average_ride_duration / 2) and (self.start_station_id in most_busiest_stations or self.end_station_id in most_busiest_stations):
            return 'C'
        # Short-duration rides at busy stations
        elif duration < average_ride_duration and (self.start_station_id in most_busiest_stations or self.end_station_id in most_busiest_stations):
            return 'D'
        # Rides at busy stations
        elif self.start_station_id in most_busiest_stations or self.end_station_id in most_busiest_stations:
            return 'E'
        # Long-duration rides at central stations
        elif duration > average_ride_duration and (self.start_station_id in most_central_stations or self.end_station_id in most_central_stations):
            return 'F'
        # Casual rides at central stations
        elif self.start_station_id in most_central_stations and self.member_casual == 'casual':
            return 'G'
        # Rides at central stations
        elif self.start_station_id in most_central_stations or self.end_station_id in most_central_stations:
            return 'H'
        # Short-duration rides by casual users
        elif duration < average_ride_duration and self.member_casual == 'casual':
            return 'I'
        # Member rides at non-busy stations
        elif self.member_casual == 'member' and (self.start_station_id not in most_busiest_stations and self.end_station_id not in most_busiest_stations):
            return 'J'
        # Rides at non busy stations
        elif self.start_station_id not in most_busiest_stations and self.end_station_id not in most_busiest_stations:
            return 'K'
        else:
            return "Z"

    @staticmethod
    def get_probability_distribution(stock_data_objects, most_busiest_stations, most_central_stations, most_frequent_routes, average_ride_duration):
        event_types = [obj.classify_event(most_busiest_stations, most_central_stations, most_frequent_routes, average_ride_duration) for obj in stock_data_objects]
        event_counts = Counter(event_types)
        total_events = len(event_types)
        distribution = {event: count / total_events for event, count in event_counts.items()}
    
        probability_distribution = ''
        for event, probability in distribution.items():
            probability_distribution += event + " " + str(probability) + " "

        print(probability_distribution)


    @staticmethod
    def create_objects_from_file(file_path):
        citibike_data = []
        with open(file_path, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            header = next(csvreader)
            for row in csvreader:
                citibike_data.append(CitiBikeData(*row))
        return citibike_data

    @staticmethod
    def extract_dataset_information(file_path):
        station_counter = Counter()
        route_counter = Counter()

        total_duration = 0
        ride_count = 0

        with open(file_path, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            header = next(csvreader)
            for row in csvreader:
                start_station_id = row[5]
                end_station_id = row[7]
                station_counter[start_station_id] += 1
                station_counter[end_station_id] += 1

                start_time = datetime.fromisoformat(row[2])
                end_time = datetime.fromisoformat(row[3])
                duration = (end_time - start_time).seconds / 60
                total_duration += duration
                ride_count += 1

                route = (row[5], row[7])
                route_counter[route] += 1


        total_lat, total_lng, count = 0, 0, 0
        with open(file_path, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            header = next(csvreader)
            for row in csvreader:
                total_lat += safe_float(row[8])
                total_lng += safe_float(row[9])
                count += 1
        avg_lat, avg_lng = total_lat / count, total_lng / count

        closest_stations = {}
        with open(file_path, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            header = next(csvreader)
            for row in csvreader:
                lat, lng = safe_float(row[8]), safe_float(row[9])
                distance = ((avg_lat - lat)**2 + (avg_lng - lng)**2)**0.5
                station = row[5]
                closest_stations[station] = distance

        most_central_stations = sorted(closest_stations.items(), key=lambda x: x[1])[:20]

        busiest_stations = station_counter.most_common(20)

        average_ride_duration = total_duration / ride_count

        most_frequent_routs = route_counter.most_common(50)

        return busiest_stations, average_ride_duration, most_frequent_routs, most_central_stations


    @staticmethod
    def generate_event_stream(citi_bike_data_objects, most_busiest_stations, most_central_stations, most_frequent_routes, average_ride_duration):
        event_stream = [data.classify_event(most_busiest_stations, most_central_stations, most_frequent_routes, average_ride_duration) for data in citi_bike_data_objects]
        event_stream_str = ''
        for idx,event in enumerate(event_stream):
            event_stream_str += event + " " + str(idx+1) + " "
        print(event_stream_str)


def main():
    parser = argparse.ArgumentParser(description='Generate an event stream from Citi Bike data.')

    parser.add_argument('--file_name', default="202307-citibike-tripdata.csv", type=str, help='Enther the Citi Bike file name.')
    parser.add_argument('--produce_stream', default=False, action='store_true', help='If set, produce stream.')
    parser.add_argument('--produce_alphabet_probs', default=False, action='store_true', help='If set, produce alphabet probabilities.')
    args = parser.parse_args()

    citibike_data = CitiBikeData.create_objects_from_file(args.file_name)

    most_busiest_stations, average_ride_duration, most_frequent_routes, most_central_stations = CitiBikeData.extract_dataset_information(args.file_name)
    most_busiest_stations = [item[0] for item in most_busiest_stations]
    most_frequent_routes = [item[0] for item in most_frequent_routes]
    most_central_stations = [item[0] for item in most_central_stations]

    if args.produce_stream:
        CitiBikeData.generate_event_stream(citibike_data, most_busiest_stations, most_central_stations, most_frequent_routes, average_ride_duration)

    if args.produce_alphabet_probs:
        CitiBikeData.get_probability_distribution(citibike_data, most_busiest_stations, most_central_stations, most_frequent_routes, average_ride_duration)

if __name__ == "__main__":
    main()
