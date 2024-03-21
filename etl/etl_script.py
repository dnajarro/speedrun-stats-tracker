import subprocess
import time
import requests
import datetime

# ER = Elden Ring
# SRT = Spyro Reignited Trilogy
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
    runs = []
    while len_data != 0:
        r = requests.get(
            f"https://www.speedrun.com/api/v1/runs?max={max}&offset={offset}&game={game_id}")
        data = r.json()
        len_data = len(data['data'])
        offset += offset_increment
        runs.extend(data['data'])
        # Sleep to not exceed 100 requests/min
        time.sleep(0.02)
    return runs


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
er_anyperc_id = "02qr00pk"
er_anyperc_glitchless_id = "w20e4yvd"
er_remembrances_glitchless_id = "9d8nl33d"

# SMO API calls
smo_id = "76r55vd8"
smo_anyperc_id = "w20w1lzd"
smo_100perc_id = "n2y5jwek"

# srt_id = "m1mx0y46" Determining which runs are part of SRT 1 Any% NBS vs. other categories is difficult and the API doesn't provide a clear distinction in the JSON

# Spyro API calls
spyro_id = "576rje18"
spyro_anyperc_id = "lvdo8ykp"
spyro_120perc_id = "7wkp1gkr"

# Lies of P API calls
lop_id = "4d7n7wl6"
lop_anyperc_id = "mke1p392"
lop_allergobosses_id = "xk9z63x2"

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
print("Total LoP runs submitted:", len(lop_all_runs))
print("No. of LoP runs verified since last week:", len(lop_newest_verified_runs))
print("LoP Any% Top 10 player data:", lop_anyperc_players_data)
print("LoP All Ergo Bosses Top 10 player data:", lop_allergobosses_players_data)
print("LoP Any% Top 10 run times:", lop_anyperc_top10_run_times)
print("LoP All Ergo Bosses Top 10 run times:",
      lop_allergobosses_top10_run_times)

print("Completed Game Search....")

# define configuration parameters for connecting to source database
source_config = {
    'dbname': 'source_db',
    'user': 'postgres',
    'password': 'secret',
    # use the service name from docker-compose.yaml as hostname
    'host': 'source_postgres'
}

# define configuration parameters for connecting to destination database
destination_config = {
    'dbname': 'destination_db',
    'user': 'postgres',
    'password': 'secret',
    # use the service name from docker-compose.yaml as hostname
    'host': 'destination_postgres'
}

# uses pg_dump command to dump the data from source database to SQL file
dump_command = [
    'pg_dump',
    '-h', source_config['host'],
    '-U', source_config['user'],
    '-d', source_config['dbname'],
    '-f', 'data_dump.sql',
    # avoid being prompted for password every time
    '-w'
]

# set the PGPASSWORD environment variable to avoid password prompt
subprocess_env = dict(PGPASSWORD=source_config['password'])

# execute dump command
# subprocess.run(dump_command, env=subprocess_env, check=True)

# use psql to load the dumped SQL file into the destination database
load_command = [
    'psql',
    '-h', destination_config['host'],
    '-U', destination_config['user'],
    '-d', destination_config['dbname'],
    '-a', '-f', 'data_dump.sql'
]

# set the PGPASSWORD environment variable for the destination database
subprocess_env = dict(PGPASSWORD=destination_config['password'])

# execute the load command
# subprocess.run(load_command, env=subprocess_env, check=True)

print("Ending ETL script...")
