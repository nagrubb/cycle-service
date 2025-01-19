#!/usr/bin/env python3
import os
import requests
from flask import Flask, jsonify, redirect, request
from pint import Quantity
from redis import Redis
from stravalib import unit_helper
from stravalib.client import Client
from stravalib.exc import AccessUnauthorized
from datetime import datetime
import time
import json

def read_environ_file(env_name):
    filename = os.environ[env_name]
    return open(filename, 'r').read()

init_error = None
application = Flask(__name__)

try:
    client_id = read_environ_file("STRAVA_CLIENT_ID_FILE")
    client_secret = read_environ_file("STRAVA_CLIENT_SECRET_FILE")
    year_goal = int(os.environ['YEAR_GOAL'])
    redis_client = Redis('redis', 6379)

except Exception as e:
    print(e)
    init_error = str(e)

@application.route("/api/cycle/auth")
def auth():
    if init_error:
        return jsonify(error=init_error), 500

    strava_client = Client()
    authorize_url = strava_client.authorization_url(client_id=client_id, redirect_uri='http://localhost:8000/api/cycle/auth/callback')
    return redirect(authorize_url)

@application.route("/api/cycle/auth/callback")
def auth_callback():
    if init_error:
        return jsonify(error=init_error), 500

    code = request.args.get('code')
    strava_client = Client()
    token_response = strava_client.exchange_code_for_token(client_id=client_id, client_secret=client_secret, code=code)
    expires_at = token_response["expires_at"]

    redis_client.set('redis_refresh_token', token_response["refresh_token"])
    redis_client.set('redis_token', json.dumps(token_response), exat=expires_at)

    return jsonify(), 200

def get_strava_client():
    token_json = redis_client.get('redis_token')

    if token_json:
        token = json.loads(token_json)
    else:
        # short term token expired
        refresh_token = redis_client.get('redis_refresh_token')

        if not refresh_token:
            return None

        token_response = client.refresh_access_token(client_id, client_secret, refresh_token)
        redis_client.set('redis_refresh_token', token_response["refresh_token"])
        redis_client.set('redis_token', json.dumps(token_response), exat=expires_at)
        token = token_response

    strava_client = Client()
    strava_client.access_token = token["access_token"]
    return strava_client

@application.route("/api/cycle/goal/progress/year")
def goal_progress_year():
    try:
        if init_error:
            return jsonify(error=init_error), 500

        strava_client = get_strava_client()

        if not strava_client:
            return jsonify(), 401

        first_day_of_cur_year = datetime.now().replace(month=1, day=1)
        activites = strava_client.get_activities(after=first_day_of_cur_year, before=datetime.now())

        distance = 0

        for activity in activites:
            if activity.type == "VirtualRide" or activity.type == "Ride":
                distance += unit_helper.miles(activity.distance)

        ride_total = distance.magnitude

        return jsonify(
            ytd=ride_total,
            goal=year_goal
        )
    except Exception as e:
        return jsonify(error=str(e)), 500

@application.route("/api/cycle/goal/progress/week")
def goal_progress_week():
    try:
        if init_error:
            return jsonify(error=init_error), 500

        strava_client = get_strava_client()

        if not strava_client:
            return jsonify(), 401

        first_day_of_cur_year = datetime.now().replace(month=1, day=1)
    
        # The algorithm assumes activities are returning from most recent order
        activites = strava_client.get_activities(after=first_day_of_cur_year, before=datetime.now())

        distance_by_week = dict()

        for activity in activites:
            if activity.type == "VirtualRide" or activity.type == "Ride":
                week_number = activity.start_date.isocalendar()[1]
                miles = unit_helper.miles(activity.distance).magnitude

                if distance_by_week.get(week_number) is None:
                    distance_by_week[week_number] = miles
                else:
                    distance_by_week[week_number] += miles

        cur_week = datetime.now().isocalendar()[1]
        for num_week in range(2, cur_week + 1):
            last_week_miles = distance_by_week[num_week - 1]
            distance_by_week[num_week] += last_week_miles

        return jsonify(distance_by_week=distance_by_week)
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=80)
