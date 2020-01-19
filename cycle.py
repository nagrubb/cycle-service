#!/usr/bin/env python3
import os
from flask import Flask, jsonify
from stravalib import unithelper
from stravalib.client import Client
from stravalib.exc import AccessUnauthorized

def read_environ_file(env_name):
    filename = os.environ[env_name]
    return open(filename, 'r').read()

def get_access_token():
    client = Client()
    refreshed_token_info = client.refresh_access_token(
        client_id, client_secret, refresh_token)
    new_access_token = refreshed_token_info['access_token']
    if refresh_token != refreshed_token_info['refresh_token']:
        print(
            'Refresh token does not match existing, this will most definitely cause issues in the future')
    return new_access_token

init_error = None
application = Flask(__name__)

try:
    client_id = read_environ_file("STRAVA_CLIENT_ID_FILE")
    client_secret = read_environ_file("STRAVA_CLIENT_SECRET_FILE")
    refresh_token = read_environ_file("STRAVA_REFRESH_TOKEN_FILE")
    year_goal = int(os.environ['YEAR_GOAL'])
except Exception as e:
    init_error = str(e)

@application.route("/api/v1/cycle")
def cycle():
    try:
        if init_error:
            return jsonify(error=init_error), 500

        access_token = get_access_token()
        client = Client(access_token)
        stats = client.get_athlete_stats()
        print(stats)
        ride_total = float(unithelper.miles(stats.ytd_ride_totals.distance))

        return jsonify(
            ytd=ride_total,
            goal=year_goal
        )
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=80)
