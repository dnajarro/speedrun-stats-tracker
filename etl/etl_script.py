import subprocess
import time
import requests
import datetime
import sqlalchemy
import pandas as pd
from sqlalchemy.orm import sessionmaker

# ER = Elden Ring
# SMO = Super Mario Odyssey
# LOP = Lies of P

# TODO:
# 1. Read through the Speedrun.com API documentation to determine what API calls we want to make and what we want to store in the databases. DONE
# 2. Write new init.sql file to initialize the database with the correct schema
# 3. Rewrite the etl_script.py file to extract data from the API and load it into database; remove second database.
# 4. Test code.
# 5. Further modify etl_script.py to pull all desired data and test again. DONE
# 6. Create simple web application to display and organize data.
# 7. Pull data from database to web application.
# 8. Test code.

# Calls API to get all verified, rejected, and under-review runs for a given game. Returns list of runs.


def get_all_submitted_runs(game_id):
    len_data = -1
    max = 200
    offset_increment = 200
    offset = 0
    max_offset = 10000
    runs = []
    # request the data from newest to oldest
    while len_data != 0 and offset + max < max_offset:
        r = requests.get(
            f"https://www.speedrun.com/api/v1/runs?max={max}&offset={offset}&game={game_id}&orderby=submitted&direction=desc&embed=players")
        data = r.json()
        len_data = len(data['data'])
        offset += offset_increment
        runs.extend(data['data'])
        # Sleep to not exceed 100 requests/min
        time.sleep(0.05)
    # request the data from oldest runs to newest, specifically for games with lots of runs, like SMO
    if offset + max >= max_offset:
        offset = 0
        while len_data != 0 and offset_increment + max < max_offset:
            r = requests.get(
                f"https://www.speedrun.com/api/v1/runs?max={max}&offset={offset}&game={game_id}&orderby=submitted&direction=asc&embed=players")
            data = r.json()
            len_data = len(data['data'])
            offset += offset_increment
            runs.extend(data['data'])
            # Sleep to not exceed 100 requests/min
            time.sleep(0.05)
    return runs


# Takes in a list of run data and isolates player data into a list of dictionaries containing
# game_id, player_id1, player_name1, player_id2, player_name2 for all players based on run. Returns list of dictionaries.
def get_all_player_data(run_data):
    player_data = []
    for run in run_data:
        player_id2 = None
        player_name2 = None
        if len(run['players']['data']) > 1:
            player_id2 = run['players']['data'][1]['id']
            player_name2 = run['players']['data'][1]['names']['international']
        player = {
            "game_id": run['game'],
            "player_id1": run['players']['data'][0]['id'],
            "player_name1": run['players']['data'][0]['names']['international'],
            "player_id2": player_id2,
            "player_name2": player_name2
        }
        player_data.append(player)
    return player_data


# Calls API to get all speedrun categories associated with a given game. Takes game_id and game_name arguments and returns a list of dictionaries representing each category
# containing game_id, category_id, and category_name.
def get_all_run_categories(game_id, game_name):
    r = requests.get(
        f"https://www.speedrun.com/api/v1/games/{game_id}/categories"
    )
    data = r.json()
    categories = []
    for category in data['data']:
        category_info = {"game_id": game_id,
                         "game_name": game_name,
                         "category_id": category['id'],
                         "category_name": category['name']}
        categories.append(category_info)
    return categories


# Combines category data, player data, and run data to create dictionary. Dictionary is intended to be converted into a pandas dataframe to easily load into database
def combine_id_data(id_dict, all_runs, category_data, player_data):
    ids = []
    types = []
    label_names = []
    for category in category_data:
        game_id = category['game_id']
        game_name = category['game_name']
        if game_id not in ids:
            ids.append(game_id)
            types.append('Game')
            label_names.append(game_name)
        category_id = category['category_id']
        category_name = category['category_name']
        if category_id not in ids:
            ids.append(category_id)
            types.append('Category')
            label_names.append(category)
    for player in player_data:
        player_id1 = player['player_id1']
        player_name1 = player['player_name1']
        if player_id1 not in ids:
            ids.append(player_id1)
            types.append('Player')
            label_names.append(player_name1)
        if player['player_id2'] is not None:
            player_id2 = player['player_id2']
            player_name2 = player['player_name2']
            if player_id2 not in ids:
                ids.append(player_id2)
                types.append('Player')
                label_names.append(player_name2)


# Calls API to get top 10 verified times for a given category of runs for a given game. Includes player info in embed for better player identification. Returns JSON response.
def get_top_10(game_id, category_id):
    r = requests.get(
        f"https://www.speedrun.com/api/v1/leaderboards/{game_id}/category/{category_id}?top=10&embed=players")
    data = r.json()
    return data


# Calls API to get 50 most recently verified runs for a given game, regardless of category, and returns a list of runs that were verified in the last week. Returns list of runs.
def get_newest_runs(game_id):
    r = requests.get(
        f"https://www.speedrun.com/api/v1/runs?max=50&game={game_id}&status=verified&orderby=verify-date&direction=desc")
    data = r.json()
    recently_verified = []
    for run in data['data']:
        verify_date = datetime.datetime.strptime(
            run['status']['verify-date'], "%Y-%m-%dT%XZ")
        today = datetime.datetime.now()
        if verify_date > (today - datetime.timedelta(days=7)):
            recently_verified.append(run)
    return recently_verified


# Takes in Top 10 data with player embedding, matches player id's for each run in Top 10 with gamertag. Returns list of key (placement)-value (list of players) pairs.
def get_player_data_from_top10(top10_data):
    placements_with_gamertag = []
    players = top10_data['data']['players']['data']
    for run in top10_data['data']['runs']:
        place = run['place']
        placement = {place: []}
        for player in run['run']['players']:
            player_id = player['id']
            for player in players:
                if player_id == player['id']:
                    placement[place].append(
                        player['names']['international'])
            if len(placements_with_gamertag) == 0 or place not in placements_with_gamertag[-1]:
                placements_with_gamertag.append(placement)
    return placements_with_gamertag


# Takes in Top 10 data, isolates the times for each run in the Top 10. Returns a list of key (placement)- value (time in seconds) pairs
def get_run_times_from_top10(top10_data):
    placement_times = []
    for run in top10_data['data']['runs']:
        place = run['place']
        placement_times.append({place: run['run']['times']['primary_t']})
    return placement_times

# Set up a connection to PostgreSQL


def wait_for_postgres(host, max_retries=5, delay_seconds=5):
    retries = 0
    while retries < max_retries:
        try:
            result = subprocess.run(
                ["pg_isready", "-h", host], check=True, capture_output=True, text=True)
            if "accepting connections" in result.stdout:
                print("Successfully connected to PostgreSQL!")
                return True
        except subprocess.CalledProcessError as e:
            print(f"Error connecting to PostgreSQL: {e}")
            retries += 1
            print(
                f"Retrying in {delay_seconds} seconds... (Attempt {retries}/{max_retries})")
            time.sleep(delay_seconds)
    print("Max retries reached. Exiting.")
    return False


# connect to database
# if not wait_for_postgres(host="source_postgres"):
    # exit(1)

print("Starting ETL script...")
print("Extracting game data...")

# Elden Ring API calls
er_id = "nd28z0ed"
elden_ring_name = "Elden Ring"
er_anyperc_id = "02qr00pk"
er_anyperc_glitchless_id = "w20e4yvd"
er_remembrances_glitchless_id = "9d8nl33d"

# SMO API calls
smo_id = "76r55vd8"
smo_name = "Super Mario Odyssey"
smo_anyperc_id = "w20w1lzd"
smo_100perc_id = "n2y5jwek"

# srt_id = "m1mx0y46" Determining which runs are part of SRT 1 Any% NBS vs. other categories is difficult and the API doesn't provide a clear distinction in the JSON

# Spyro API calls
spyro_id = "576rje18"
spyro_name = "Spyro The Dragon"
spyro_anyperc_id = "lvdo8ykp"
spyro_120perc_id = "7wkp1gkr"

# Lies of P API calls
lop_id = "4d7n7wl6"
lop_name = "Lies of P"
lop_anyperc_id = "mke1p392"
lop_allergobosses_id = "xk9z63x2"

# Extracting id data

er_categories = get_all_run_categories(er_id)
smo_categories = get_all_run_categories(smo_id)
spyro_categories = get_all_run_categories(spyro_id)
lop_categories = get_all_run_categories(lop_id)
er_all_runs = get_all_submitted_runs(er_id)
er_all_players = get_all_player_data(er_all_runs)
smo_all_runs = get_all_submitted_runs(smo_id)
smo_all_players = get_all_player_data(smo_all_runs)
spyro_all_runs = get_all_submitted_runs(spyro_id)
spyro_all_players = get_all_player_data(spyro_all_runs)
lop_all_runs = get_all_submitted_runs(lop_id)
lop_all_players = get_all_player_data(lop_all_runs)


# Extracting Elden Ring data

# List of all submitted runs
er_all_runs = get_all_submitted_runs(er_id)
# List of newest verified runs
er_newest_verified_runs = get_newest_runs(er_id)
# Data on top 10 runs for ER Any%
er_anyperc_top10_data = get_top_10(er_id, er_anyperc_id)
# Data on top 10 runs for ER Any% Glitchless
er_anyperc_glitchless_top10_data = get_top_10(er_id, er_anyperc_glitchless_id)
# Data on top 10 runs for ER All Remembrances
er_remembrances_glitchless_top10_data = get_top_10(
    er_id, er_remembrances_glitchless_id)
# Player data on top 10 runs for ER Any%
er_anyperc_players_data = get_player_data_from_top10(er_anyperc_top10_data)
# Player data on top 10 runs for ER Any% Glitchless
er_anyperc_glitchless_players_data = get_player_data_from_top10(
    er_anyperc_glitchless_top10_data)
# Player data on top 10 runs for ER All Remembrances Glitchless
er_remembrances_glitchless_players_data = get_player_data_from_top10(
    er_remembrances_glitchless_top10_data)
# Run times for top 10 ER Any%
er_anyperc_top10_run_times = get_run_times_from_top10(er_anyperc_top10_data)
# Run times for top 10 ER Any% Glitchless
er_anyperc_glitchless_top10_run_times = get_run_times_from_top10(
    er_anyperc_glitchless_top10_data)
# Run times for top 10 ER All Remembrances Glitchless
er_remembrances_glitchless_top10_run_times = get_run_times_from_top10(
    er_remembrances_glitchless_top10_data)

# Printing to console
print("Total ER runs submitted:", len(er_all_runs))
print("No. of new verified runs since last week:", len(er_newest_verified_runs))
print("ER Any% Top 10 player data:", er_anyperc_players_data)
print("ER Any% Top 10 Glitchless player data:",
      er_anyperc_glitchless_players_data)
print("ER All Remembrances Glitchless Top 10 player data:",
      er_remembrances_glitchless_players_data)
print("ER Any% Top 10 Run Times:", er_anyperc_top10_run_times)
print("ER Any% Top 10 Glitchless Run times:",
      er_anyperc_glitchless_top10_run_times)
print("ER All Remembrances Glitchless run times:",
      er_remembrances_glitchless_top10_run_times)


# Extracting SMO data

# Because API limits offset up to 10000, it's not possible to extract more than 20k runs
# from a game without going by category
# smo_all_runs = get_all_submitted_runs(smo_id)
# List of newest verified runs
smo_newest_verified_runs = get_newest_runs(smo_id)
# Data on top 10 runs for SMO Any%
smo_anyperc_top10_data = get_top_10(smo_id, smo_anyperc_id)
# Data on top 10 runs for SMO 100%
smo_100perc_top10_data = get_top_10(smo_id, smo_100perc_id)
# Player data for SMO Any% top 10 runs
smo_anyperc_players_data = get_player_data_from_top10(smo_anyperc_top10_data)
# Player data for SMO 100% top 10 runs
smo_100perc_players_data = get_player_data_from_top10(smo_100perc_top10_data)
# Run times for top 10 SMO Any%
smo_anyperc_top10_run_times = get_run_times_from_top10(smo_anyperc_top10_data)
# Run times for top 10 SMO 100%
smo_100perc_top10_run_times = get_run_times_from_top10(smo_100perc_top10_data)

# Printing to console
# print(len(smo_all_runs))
print("Total SMO runs submitted:",
      "Over 20,000 🤷 the API won't let me see more than that")
print("SMO No. of new verified runs since last week:",
      len(smo_newest_verified_runs))
print("SMO Any% Top 10 player data:", smo_anyperc_players_data)
print("SMO 100% Top 10 player data:", smo_100perc_players_data)
print("SMO Any% Top 10 run times:", smo_anyperc_top10_run_times)
print("SMO 100% Top 10 run times:", smo_100perc_top10_run_times)

# Extracting Spyro data

# List of all submitted runs
spyro_all_runs = get_all_submitted_runs(spyro_id)
# List of newest verified runs
spyro_newest_verified_runs = get_newest_runs(spyro_id)
# Data on top 10 runs for Spyro Any%
spyro_anyperc_top10_data = get_top_10(spyro_id, spyro_anyperc_id)
# Data on top 10 runs for Spyro 120%
spyro_120perc_top10_data = get_top_10(spyro_id, spyro_120perc_id)
# Player data for top 10 runs for Spyro Any%
spyro_anyperc_players_data = get_player_data_from_top10(
    spyro_anyperc_top10_data)
# Player data for top 10 runs for Spyro 120%
spyro_120perc_players_data = get_player_data_from_top10(
    spyro_120perc_top10_data)
# Run times for top 10 Spyro Any%
spyro_anyperc_top10_run_times = get_run_times_from_top10(
    spyro_anyperc_top10_data)
# Run times for top 10 Spyro 120%
spyro_120perc_top10_run_times = get_run_times_from_top10(
    spyro_120perc_top10_data)

# Printing to console
print("Total Spyro runs submitted:", len(spyro_all_runs))
print("No. of new verified runs since last week:",
      len(spyro_newest_verified_runs))
print("Spyro Any% Top 10 player data:", spyro_anyperc_players_data)
print("Spyro 120% Top 10 player data:", spyro_120perc_players_data)
print("Spyro Any% Top 10 run times:", spyro_anyperc_top10_run_times)
print("Spyro 120% Top 10 run times:", spyro_120perc_top10_run_times)

# Extracting Lies of P data

# List of all submitted runs
lop_all_runs = get_all_submitted_runs(lop_id)
# List of newest verified runs
lop_newest_verified_runs = get_newest_runs(lop_id)
# Data on top 10 runs for LoP Any%
lop_anyperc_top10_data = get_top_10(lop_id, lop_anyperc_id)
# Data on top 10 runs for LoP All Bosses
lop_allergobosses_top10_data = get_top_10(lop_id, lop_allergobosses_id)
# Player data for top 10 runs for LoP Any%
lop_anyperc_players_data = get_player_data_from_top10(lop_anyperc_top10_data)
# Player data for top 10 runs for LoP All Ergo Bosses
lop_allergobosses_players_data = get_player_data_from_top10(
    lop_allergobosses_top10_data)
# Run times for top 10 runs for LoP Any%
lop_anyperc_top10_run_times = get_run_times_from_top10(lop_anyperc_top10_data)
# Run times for top 10 runs for LoP All Ergo Bosses
lop_allergobosses_top10_run_times = get_run_times_from_top10(
    lop_allergobosses_top10_data)
print("Total LoP runs submitted:", lop_all_runs, len(lop_all_runs))
print("No. of LoP runs verified since last week:", len(lop_newest_verified_runs))
print("LoP Any% Top 10 player data:", lop_anyperc_players_data)
print("LoP All Ergo Bosses Top 10 player data:", lop_allergobosses_players_data)
print("LoP Any% Top 10 run times:", lop_anyperc_top10_run_times)
print("LoP All Ergo Bosses Top 10 run times:",
      lop_allergobosses_top10_run_times)

print("Completed Extraction and Transformation....")

# Top Ten columns
top_ten_run_id = []
top_ten_player_id1 = []
top_ten_player_id2 = []
top_ten_game_name = []
top_ten_placement = []
top_ten_player_name1 = []
top_ten_player_name2 = []
top_ten_category = []
top_ten_runtime = []
top_ten_verification_date = []
top_ten_retrieval_date = []

# All Runs columns
all_runs_run_id = []
all_runs_player_id1 = []
all_runs_player_id2 = []
all_runs_game_name = []
all_runs_player_name1 = []
all_runs_player_name2 = []
all_runs_category = []
all_runs_runtime = []
all_runs_retrieval_date = []

# Ids columns
id = []
type = []
label_name = []

for run in er_all_runs:
    all_runs_run_id.append(run['id'])
    all_runs_player_id1.append(run['players']['data'][0]['id'])
    if len(run['players']) > 1:
        all_runs_player_id2.append(run['players']['data'][1]['id'])
    all_runs_game_name.append('Elden Ring')
    all_runs_category.append(run['category'])
    all_runs_runtime.append(run['times']['primary_t'])
    all_runs_retrieval_date.append(datetime.datetime.now())
    id.append(run['game'])
    type.append('game')
    label_name.append('Elden Ring')
    id.append(run['category'])
    type.append('category')
    # TODO: match category id's with all game category names and then add category name to label_name

for run in er_anyperc_glitchless_top10_data['runs']:
    top_ten_run_id.append(run['run']['id'])
    top_ten_player_id1.append(run['run']['players'][0]['id'])
    if len(run['run']['players']) > 1:
        top_ten_player_id2.append(run['run']['players'][1]['id'])

# # define configuration parameters for connecting to source database
# extraction_data_config = {
#     'dbname': 'speedrun_db',
#     'user': 'postgres',
#     'password': 'secret',
#     # use the service name from docker-compose.yaml as hostname
#     'host': 'speedrun_postgres'
# }

# # define configuration parameters for connecting to destination database
# destination_config = {
#     'dbname': 'destination_db',
#     'user': 'postgres',
#     'password': 'secret',
#     # use the service name from docker-compose.yaml as hostname
#     'host': 'destination_postgres'
# }

# # uses pg_dump command to dump the data from source database to SQL file
# dump_command = [
#     'pg_dump',
#     '-h', extraction_data_config['host'],
#     '-U', extraction_data_config['user'],
#     '-d', extraction_data_config['dbname'],
#     '-f', 'data_dump.sql',
#     # avoid being prompted for password every time
#     '-w'
# ]

# set the PGPASSWORD environment variable to avoid password prompt
# subprocess_env = dict(PGPASSWORD=extraction_data_config['password'])

# execute dump command
# subprocess.run(dump_command, env=subprocess_env, check=True)

# use psql to load the dumped SQL file into the destination database
# load_command = [
#     'psql',
#     '-h', destination_config['host'],
#     '-U', destination_config['user'],
#     '-d', destination_config['dbname'],
#     '-a', '-f', 'data_dump.sql'
# ]

# set the PGPASSWORD environment variable for the destination database
# subprocess_env = dict(PGPASSWORD=destination_config['password'])

# execute the load command
# subprocess.run(load_command, env=subprocess_env, check=True)

print("Ending ETL script...")
