#!/usr/bin/env python3
import os
from flask import Flask, jsonify
from stravalib import unithelper
from stravalib.client import Client

init_error = None
application = Flask(__name__)

try:
    token_filename = os.environ['STRAVA_ACCESS_TOKEN_FILE']
    access_token = open(token_filename, 'r').read()
    year_goal = int(os.environ['YEAR_GOAL'])
except Exception as e:
    init_error = str(e)

@application.route("/api/v1/cycle")
def cycle():
    try:
        if init_error:
            return jsonify(error=init_error), 500

        client = Client()
        client.access_token = access_token
        stats = client.get_athlete_stats()
        ride_total = float(unithelper.miles(stats.ytd_ride_totals.distance))

        return jsonify(
            ytd=ride_total,
            goal=year_goal
        )
    except Exception as e:
        return jsonify(error = str(e)), 500

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=80)
