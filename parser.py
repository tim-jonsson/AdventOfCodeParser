import requests
import math
import random
from datetime import date
import json

with open('settings.txt', encoding="UTF-8") as f:
    variables = json.load(f)

URL = variables['URL']

HEADER = variables['HEADER']

# Currently the start and end date needs to be calculated by hands as dates are weird. Can probably be automated in the future
# Use https://www.unixtimestamp.com/
# Timestamp for start of week, 00:00:00 on Monday. Must be exact!
START_DATE = 1670799600
# Timestamp for end of week, 23:59:59 on Sunday. Must be exact!
END_DATE = 1671404399



WEEK = date.fromtimestamp(START_DATE).isocalendar()[1]


def get_leaderboard():
    resp = requests.get(url=URL, headers=HEADER, timeout=100)
    json_leaderboard = resp.json()['members']  # Get the json formatted leaderboard
    return json_leaderboard


def get_leaderboard_standings(leaderboard):
    member_info = [get_member_info(member_info)
                   for member_info in leaderboard.values()]
    sorted_member_info = sorted(member_info, key=lambda x: (-x[1], x[0]))
    non_zero_stars = list(filter(lambda x: x[1], sorted_member_info))
    return non_zero_stars


def get_member_info(member_info):
    name = member_info['name'] if member_info['name'] is not None else "Anonymous User"
    star_list = member_info['completion_day_level']
    star_count = sum(map(filter_star_count, star_list.keys(), star_list.values()))
    weight = 1.02578*math.log(2.3963*star_count) if star_count > 0 else 0
    return (name, star_count, weight)

# Makes sure the star was taken during the week and not afterwards
def filter_star_count(day, daily_stars):
    START_DAY = int(date.fromtimestamp(START_DATE).day)
    END_DAY = int(date.fromtimestamp(END_DATE).day)
    star_count = len([star for star in daily_stars.values()
                      if START_DATE <= star['get_star_ts'] <= END_DATE and START_DAY <= int(day) <= END_DAY])
    return star_count


def pick_winners(leaderboard_standings):
    weights = [member[2] for member in leaderboard_standings]
    winner = random.choices(leaderboard_standings, weights=weights, k=1)[0]
    print(
        f"Grattis {winner[0]} till veckans stora pris! Du hade tjänat ihop totalt {winner[1]} stjärnor under vecka. {WEEK}!\n")

    concilliatory_winner_1 = random.choice(leaderboard_standings)
    print(
        f"Grattis {concilliatory_winner_1[0]} till första tröstpriset! Du hade tjänat ihop totalt {concilliatory_winner_1[1]} stjärnor under vecka. {WEEK}!\n")

    concilliatory_winner_2 = random.choice(leaderboard_standings)
    print(
        f"Grattis {concilliatory_winner_2[0]} till andra tröstpriset! Du hade tjänat ihop totalt {concilliatory_winner_2[1]} stjärnor under vecka. {WEEK}!")


if __name__ == "__main__":
    leaderboard = get_leaderboard()
    leaderboard_standings = get_leaderboard_standings(leaderboard)
    pick_winners(leaderboard_standings)
