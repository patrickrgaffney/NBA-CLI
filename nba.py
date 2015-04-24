#!/usr/bin/env python3

from datetime import date
import requests
import json
import argparse
from game_data import Game
from os import _exit

year = date.today().strftime("%Y") # &Y is four-digits
day = date.today().strftime("%d") # %d is zero-padded
month = date.today().strftime("%m") # %m is zero-padded
today = month + day + year

parser = argparse.ArgumentParser() # parser for CLI arguments
parser.add_argument("-d", "--date", help="date for NBA scores, ex: mmddyyyy, default: today")
args = parser.parse_args()

if args.date:
    if len(args.date) != 8: # must be valid date syntax
        raise ValueError("date syntax: mmddyyyy, ex: 01071992")
    elif args.date[4:8] > year:
        raise ValueError("future dates cannot be outside of the current season")
    month = args.date[0:2]
    day = args.date[2:4]
    year = args.date[4:8]

games_url = "http://stats.nba.com/stats/scoreboardV2?DayOffset=0&LeagueID=00&gameDate=" + \
    month + "%2F" + day + "%2F" + year

today_live_scores_url = "http://data.nba.com/data/v2014/json/mobile_teams/nba/2014/scores/00_todays_scores.json"

# request the games_url and parse the JSON
response = requests.get(games_url)
response.raise_for_status() # raise exception if invalid response
games_json = response.json()["resultSets"][0]["rowSet"]
team_data = response.json()["resultSets"][1]["rowSet"]

def test_for_games():
    """Test to see if the json blob is null, if so, there are no games on specified date, exit."""
    if games_json:
        pass
    else:
        print("There are no NBA games on this day.  Life is meaningless.")
        _exit(1)

test_for_games()

# load all the data from the json object into the class
games_list = [Game(game_num, team_data[i], team_data[i + 1]) for game_num, i in zip(games_json, range(0, 15, 2))]

def test_first_game_status(game_status, date):
    """Test the first game of the day's status to see if it has started yet."""
    if game_status == 1:
        return False
    elif game_status == 2:
        return True
    else: #status == 3
        if date == today:
            return True
        else:
            return False
if (test_first_game_status(games_json[0][3], month + day + year)):
    live_response = requests.get(today_live_scores_url)
    live_response.raise_for_status() # raise exception if invalid response
    live_scores = live_response.json()["gs"]["g"]

    for game, i in zip(games_list, range(0, 16, 1)):
        game.set_scores(live_scores[i])

[print(game) for game in games_list]
