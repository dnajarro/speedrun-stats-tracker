from uuid import uuid4
from sqlalchemy import create_engine
import subprocess
import time
import requests
import datetime
import psycopg2
import pandas as pd
import numpy as np


# ER = Elden Ring
# SMO = Super Mario Odyssey
# SPYRO = Spyro the Dragon
# LOP = Lies of P

# Calls API to get all verified, rejected, and under-review runs for a given game. Returns list of runs.

ER_NAME = 'Elden Ring'
SMO_NAME = 'Super Mario Odyssey'
SPYRO_NAME = 'Spyro the Dragon'
LOP_NAME = 'Lies of P'

ER_ID = "nd28z0ed"
SMO_ID = "76r55vd8"
SPYRO_ID = "576rje18"
LOP_ID = "4d7n7wl6"

ER_ANYPERC = 'Elden Ring Any%'
ER_ANYPERC_GLITCHLESS = 'Elden Ring Any% Glitchless'
ER_REMEMBRANCES_GLITCHLESS = 'Elden Ring All Remembrances Glitchless'

SMO_ANYPERC = 'Super Mario Odyssey Any%'
SMO_100PERC = 'Super Mario Odyssey 100%'

SPYRO_ANYPERC = 'Spyro the Dragon Any%'
SPYRO_120PERC = 'Spyro the Dragon 120%'

LOP_ANYPERC = 'Lies of P Any%'
LOP_ALL_ERGO_BOSSES = 'Lies of P All Ergo Bosses'

ER_ANYPERC_ID = "02qr00pk"
ER_ANYPERC_GLITCHLESS_ID = "w20e4yvd"
ER_REMEMBRANCES_GLITCHLESS_ID = "9d8nl33d"

SMO_ANYPERC_ID = "w20w1lzd"
SMO_100PERC_ID = "n2y5jwek"

SPYRO_ANYPERC_ID = "lvdo8ykp"
SPYRO_120PERC_ID = "7wkp1gkr"

LOP_ANYPERC_ID = "mke1p392"
LOP_ALL_ERGO_BOSSES_ID = "xk9z63x2"


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
        if len_data > 0:
            runs.extend(data['data'])
        # Sleep to not exceed 100 requests/min
        time.sleep(0.05)
    # request the data from oldest runs to newest, specifically for games with lots of runs, like SMO
    if offset + max >= max_offset:
        offset = 0
        while len_data != 0 and offset + max < max_offset:
            r = requests.get(
                f"https://www.speedrun.com/api/v1/runs?max={max}&offset={offset}&game={game_id}&orderby=submitted&direction=asc&embed=players")
            data = r.json()
            len_data = len(data['data'])
            offset += offset_increment
            if len_data > 0:
                runs.extend(data['data'])
            # Sleep to not exceed 100 requests/min
            time.sleep(0.05)
    return np.array(runs)


# Takes in a list of run data and isolates player data into a list of dictionaries containing
# game_id, player_id1, player_name1, player_id2, player_name2 for all players based on run. Returns list of dictionaries.
def get_all_player_data(run_data):
    player_data = []
    for run in run_data:
        player_id1 = None
        player_name1 = None
        player_id2 = None
        player_name2 = None
        if len(run['players']['data']) > 0:
            if run['players']['data'][0]['rel'] == 'user':
                player_id1 = run['players']['data'][0]['id']
                player_name1 = run['players']['data'][0]['names']['international']
            else:
                player_name1 = run['players']['data'][0]['name']
            if len(run['players']['data']) > 1:
                if run['players']['data'][1]['rel'] == 'user':
                    player_id2 = run['players']['data'][1]['id']
                    player_name2 = run['players']['data'][1]['names']['international']
                else:
                    player_name2 = run['players']['data'][1]['name']
        player = {
            "game_id": run['game'],
            "player_id1": player_id1,
            "player_name1": player_name1,
            "player_id2": player_id2,
            "player_name2": player_name2
        }
        player_data.append(player)
    return np.array(player_data)


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
    return np.array(categories)


# Combines category data and player data to create dictionary. Dictionary is intended to be converted into a pandas dataframe to easily load into database
def combine_id_data(id_dict, table_ids, table_label_names, category_data, player_data):
    ids = []
    speedrun_ids = []
    types = []
    label_names = []
    for category in category_data:
        game_id = category['game_id']
        game_name = category['game_name']
        category_id = category['category_id']
        category_name = category['category_name']
        if game_id or category_id in table_ids:
            continue
        if game_name or category_name in table_label_names:
            continue
        else:
            id = datetime.datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())
            ids.append(id)
            speedrun_ids.append(game_id)
            types.append('Game')
            label_names.append(game_name)
            speedrun_ids.append(category_id)
            types.append('Category')
            label_names.append(category_name)
    for player in player_data:
        player_id1 = player['player_id1']
        player_name1 = player['player_name1']
        if player_id1 in table_ids:
            continue
        if player_name1 in table_label_names:
            continue
        else:
            id = datetime.datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())
            ids.append(id)
            speedrun_ids.append(player_id1)
            types.append('Player')
            label_names.append(player_name1)
        if player['player_id2'] is not None:
            player_id2 = player['player_id2']
            player_name2 = player['player_name2']
            if player_id2 in table_ids:
                continue
            if player_name2 in table_label_names:
                continue
            else:
                id = datetime.datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())
                ids.append(id)
                speedrun_ids.append(player_id2)
                types.append('Player')
                label_names.append(player_name2)

    id_dict['id'].extend(np.array(ids))
    id_dict['speedrun_id'].extend(np.array(speedrun_ids))
    id_dict['id_type'].extend(np.array(types))
    id_dict['label_name'].extend(np.array(label_names))


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
    return np.array(recently_verified)


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
    return np.array(placements_with_gamertag)


# Takes in Top 10 data, isolates the times for each run in the Top 10. Returns a list of key (placement)- value (time in seconds) pairs
def get_run_times_from_top10(top10_data):
    placement_times = []
    for run in top10_data['data']['runs']:
        place = run['place']
        placement_times.append({place: run['run']['times']['primary_t']})
    return np.array(placement_times)


def get_player_name_by_id(game_players, player_id):
    if player_id is not None:
        for player in game_players:
            if player['player_id1'] == player_id:
                return player['player_name1']
            if player['player_id2'] == player_id:
                return player['player_name2']
    return None


def get_category_name_by_id(game_categories, category_id):
    if category_id is not None:
        for category in game_categories:
            if category['category_id'] == category_id:
                return category['category_name']
    return None


def prepare_id_dataframe(id_dict, table_ids, table_label_names, er_categories, er_players, smo_categories, smo_players, spyro_categories, spyro_players, lop_categories, lop_players):
    id_dict['id'] = []
    id_dict['speedrun_id'] = []
    id_dict['id_type'] = []
    id_dict['label_name'] = []
    combine_id_data(id_dict, table_ids, table_label_names,
                    er_categories, er_players)
    combine_id_data(id_dict, table_ids, table_label_names,
                    smo_categories, smo_players)
    combine_id_data(id_dict, table_ids, table_label_names,
                    spyro_categories, spyro_players)
    combine_id_data(id_dict, table_ids, table_label_names,
                    lop_categories, lop_players)

    id_df = pd.DataFrame(
        id_dict, columns=["id", "speedrun_id", "id_type", "label_name"])
    return id_df


def prepare_top_ten_dict(top_ten_dict, table_run_ids, table_top_ten_run_ids, top_ten_runs, game_categories, all_players, game_name):
    top_ten_run_id = []
    top_ten_game_name = []
    top_ten_category_id = []
    top_ten_category_name = []
    top_ten_placement = []
    top_ten_player_id1 = []
    top_ten_player_id2 = []
    top_ten_player_name1 = []
    top_ten_player_name2 = []
    top_ten_runtime = []
    top_ten_verification_date = []
    top_ten_retrieval_date = []
    top_ten = top_ten_runs['data']['runs']

    for run in top_ten:
        run_id = run['run']['id']
        if run_id in top_ten_run_id or run_id in table_run_ids or run_id in table_top_ten_run_ids:
            continue
        else:
            top_ten_run_id.append(run_id)
            top_ten_game_name.append(game_name)
            category_id = run['run']['category']
            top_ten_category_id.append(category_id)
            category_name = get_category_name_by_id(
                game_categories, category_id)
            top_ten_category_name.append(category_name)
            top_ten_placement.append(run['place'])
            player_id1 = None
            player_name1 = None
            player_id2 = None
            player_name2 = None
            if len(run['run']['players']) > 0:
                if run['run']['players'][0]['rel'] == 'user':
                    player_id1 = run['run']['players'][0]['id']
                else:
                    player_name1 = run['run']['players'][0]['name']
                if len(run['run']['players']) > 1:
                    if run['run']['players'][0]['rel'] == 'user':
                        player_id2 = run['run']['players'][1]['id']
                    else:
                        player_name2 = run['run']['players'][1]['name']
            player_name1 = get_player_name_by_id(all_players, player_id1)
            player_name2 = get_player_name_by_id(all_players, player_id2)
            top_ten_player_id1.append(player_id1)
            top_ten_player_id2.append(player_id2)
            top_ten_player_name1.append(player_name1)
            top_ten_player_name2.append(player_name2)
            top_ten_runtime.append(run['run']['times']['primary_t'])
            top_ten_verification_date.append(run['run']['submitted'])
            top_ten_retrieval_date.append(datetime.datetime.now())

    top_ten_dict['run_id'].extend(top_ten_run_id)
    top_ten_dict['game_name'].extend(top_ten_game_name)
    top_ten_dict['category_id'].extend(top_ten_category_id)
    top_ten_dict['category_name'].extend(top_ten_category_name)
    top_ten_dict['placement'].extend(top_ten_placement)
    top_ten_dict['player_id1'].extend(top_ten_player_id1)
    top_ten_dict['player_name1'].extend(top_ten_player_name1)
    top_ten_dict['player_id2'].extend(top_ten_player_id2)
    top_ten_dict['player_name2'].extend(top_ten_player_name2)
    top_ten_dict['runtime'].extend(top_ten_runtime)
    top_ten_dict['verification_date'].extend(top_ten_verification_date)
    top_ten_dict['retrieval_date'].extend(top_ten_retrieval_date)


def prepare_all_runs_dict(all_runs_dict, table_run_ids, all_runs, game_categories, game_name):
    all_runs_run_id = []
    all_runs_game_name = []
    all_runs_category_id = []
    all_runs_category_name = []
    all_runs_player_id1 = []
    all_runs_player_id2 = []
    all_runs_player_name1 = []
    all_runs_player_name2 = []
    all_runs_runtime = []
    all_runs_retrieval_date = []

    for run in all_runs:
        run_id = run['id']
        if run_id in all_runs_run_id or run_id in table_run_ids:
            continue
        else:
            all_runs_run_id.append(run_id)
            all_runs_game_name.append(game_name)
            category_id = run['category']
            all_runs_category_id.append(category_id)
            category_name = get_category_name_by_id(
                game_categories, category_id)
            all_runs_category_name.append(category_name)
            player_id1 = None
            player_name1 = None
            player_id2 = None
            player_name2 = None
            if len(run['players']['data']) > 0:
                if run['players']['data'][0]['rel'] == 'user':
                    player_id1 = run['players']['data'][0]['id']
                    player_name1 = run['players']['data'][0]['names']['international']
                else:
                    player_name1 = run['players']['data'][0]['name']
                if len(run['players']['data']) > 1:
                    if run['players']['data'][1]['rel'] == 'user':
                        player_id2 = run['players']['data'][1]['id']
                        player_name2 = run['players']['data'][1]['names']['international']
                    else:
                        player_name2 = run['players']['data'][1]['name']
            all_runs_player_id1.append(player_id1)
            all_runs_player_name1.append(player_name1)
            all_runs_player_id2.append(player_id2)
            all_runs_player_name2.append(player_name2)
            all_runs_runtime.append(run['times']['primary_t'])
            all_runs_retrieval_date.append(datetime.datetime.now())

    all_runs_dict['run_id'].extend(all_runs_run_id)
    all_runs_dict['game_name'].extend(all_runs_game_name)
    all_runs_dict['category_id'].extend(all_runs_category_id)
    all_runs_dict['category_name'].extend(all_runs_category_name)
    all_runs_dict['player_id1'].extend(all_runs_player_id1)
    all_runs_dict['player_name1'].extend(all_runs_player_name1)
    all_runs_dict['player_id2'].extend(all_runs_player_id2)
    all_runs_dict['player_name2'].extend(all_runs_player_name2)
    all_runs_dict['runtime'].extend(all_runs_runtime)
    all_runs_dict['retrieval_date'].extend(all_runs_retrieval_date)


print("Starting ETL script...")
print("Beginning Extraction and Transformation...")

# Extracting and transforming id data. Id data needs to be loaded first to be used by the Top Ten and All Runs tables.

print("Extracting data for id table")
categories_tot = 0
categories_calls = 0
all_runs_tot = 0
all_runs_calls = 0
all_players_tot = 0
all_players_calls = 0
id_prep_tot = 0
all_runs_df_tot = 0
all_runs_df_calls = 0
top_ten_df_tot = 0
top_ten_df_calls = 0
er_extract_tot = 0
smo_extract_tot = 0
spyro_extract_tot = 0
lop_extract_tot = 0
er_categories = get_all_run_categories(ER_ID, ER_NAME)
smo_categories = get_all_run_categories(SMO_ID, SMO_NAME)
spyro_categories = get_all_run_categories(SPYRO_ID, SPYRO_NAME)
lop_categories = get_all_run_categories(LOP_ID, LOP_NAME)
print("Category data ready")
er_all_runs = get_all_submitted_runs(ER_ID)
er_all_players = get_all_player_data(er_all_runs)
smo_all_runs = get_all_submitted_runs(SMO_ID)
smo_all_players = get_all_player_data(smo_all_runs)
spyro_all_runs = get_all_submitted_runs(SPYRO_ID)
spyro_all_players = get_all_player_data(spyro_all_runs)
lop_all_runs = get_all_submitted_runs(LOP_ID)
lop_all_players = get_all_player_data(lop_all_runs)
print("Player and run data ready")

id_dict = {}

# Extract data already in tables
conn_url = 'postgresql+psycopg2://postgres:secret@speedrun_db_container:5432/speedrun_db'

engine = create_engine(conn_url)
conn = engine.connect()
id_df = pd.read_sql("SELECT speedrun_id, label_name FROM ids", conn)
all_runs_df = pd.read_sql("SELECT run_id FROM all_runs", conn)
top_ten_df = pd.read_sql("SELECT run_id FROM top_ten", conn)
table_ids = id_df['speedrun_id'].to_numpy()
table_label_names = id_df['label_name'].to_numpy()
table_run_ids = all_runs_df['run_id'].to_numpy()
table_top_ten_run_ids = top_ten_df['run_id'].to_numpy()

conn.close()

id_df = prepare_id_dataframe(id_dict, table_ids, table_label_names, er_categories, er_all_players, smo_categories,
                             smo_all_players, spyro_categories, spyro_all_players, lop_categories, lop_all_players)

print("id dataframe ready")

# Extracting Elden Ring data

print("Extracting ER data")
# List of all submitted runs
er_all_runs = get_all_submitted_runs(ER_ID)
# List of newest verified runs
er_newest_verified_runs = get_newest_runs(ER_ID)
# Data on top 10 runs for ER Any%
er_anyperc_top10_data = get_top_10(ER_ID, ER_ANYPERC_ID)
# Data on top 10 runs for ER Any% Glitchless
er_anyperc_glitchless_top10_data = get_top_10(ER_ID, ER_ANYPERC_GLITCHLESS_ID)
# Data on top 10 runs for ER All Remembrances
er_remembrances_glitchless_top10_data = get_top_10(
    ER_ID, ER_REMEMBRANCES_GLITCHLESS_ID)
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

# Extracting SMO data

# Because API limits offset up to 10000, it's not possible to extract more than 20k runs
# from a game without going by category
print("Extracting SMO data")
smo_all_runs = get_all_submitted_runs(SMO_ID)
# List of newest verified runs
smo_newest_verified_runs = get_newest_runs(SMO_ID)
# Data on top 10 runs for SMO Any%
smo_anyperc_top10_data = get_top_10(SMO_ID, SMO_ANYPERC_ID)
# Data on top 10 runs for SMO 100%
smo_100perc_top10_data = get_top_10(SMO_ID, SMO_100PERC_ID)
# Player data for SMO Any% top 10 runs
smo_anyperc_players_data = get_player_data_from_top10(smo_anyperc_top10_data)
# Player data for SMO 100% top 10 runs
smo_100perc_players_data = get_player_data_from_top10(smo_100perc_top10_data)
# Run times for top 10 SMO Any%
smo_anyperc_top10_run_times = get_run_times_from_top10(smo_anyperc_top10_data)
# Run times for top 10 SMO 100%
smo_100perc_top10_run_times = get_run_times_from_top10(smo_100perc_top10_data)

# Extracting Spyro data

print("Extracting Spyro data")
# List of all submitted runs
spyro_all_runs = get_all_submitted_runs(SPYRO_ID)
# List of newest verified runs
spyro_newest_verified_runs = get_newest_runs(SPYRO_ID)
# Data on top 10 runs for Spyro Any%
spyro_anyperc_top10_data = get_top_10(SPYRO_ID, SPYRO_ANYPERC_ID)
# Data on top 10 runs for Spyro 120%
spyro_120perc_top10_data = get_top_10(SPYRO_ID, SPYRO_120PERC_ID)
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

# Extracting Lies of P data

# List of all submitted runs
print("Extracting LoP data")
lop_all_runs = get_all_submitted_runs(LOP_ID)
# List of newest verified runs
lop_newest_verified_runs = get_newest_runs(LOP_ID)
# Data on top 10 runs for LoP Any%
lop_anyperc_top10_data = get_top_10(LOP_ID, LOP_ANYPERC_ID)
# Data on top 10 runs for LoP All Bosses
lop_allergobosses_top10_data = get_top_10(LOP_ID, LOP_ALL_ERGO_BOSSES_ID)
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

print("Completed Extraction...")

print("Preparing All Runs dataframe")

all_runs_dict = {}

all_runs_dict['run_id'] = []
all_runs_dict['game_name'] = []
all_runs_dict['category_id'] = []
all_runs_dict['category_name'] = []
all_runs_dict['player_id1'] = []
all_runs_dict['player_name1'] = []
all_runs_dict['player_id2'] = []
all_runs_dict['player_name2'] = []
all_runs_dict['runtime'] = []
all_runs_dict['retrieval_date'] = []

# Elden Ring All Runs
prepare_all_runs_dict(
    all_runs_dict, table_run_ids, er_all_runs, er_categories, ER_NAME)
# SMO All Runs
prepare_all_runs_dict(all_runs_dict, table_run_ids, smo_all_runs,
                      smo_categories, SMO_NAME)
# Spyro All Runs
prepare_all_runs_dict(
    all_runs_dict, table_run_ids, spyro_all_runs, spyro_categories, SPYRO_NAME)
# Lies of P All Runs
prepare_all_runs_dict(
    all_runs_dict, table_run_ids, lop_all_runs, lop_categories, LOP_NAME)

all_runs_df = pd.DataFrame(all_runs_dict, columns=['run_id', 'game_name', 'category_id', 'category_name', 'player_id1',
                           'player_name1', 'player_id2', 'player_name2', 'runtime', 'retrieval_date'])

print("Preparing Top Ten dataframe")

top_ten_dict = {}

top_ten_dict['run_id'] = []
top_ten_dict['game_name'] = []
top_ten_dict['category_id'] = []
top_ten_dict['category_name'] = []
top_ten_dict['placement'] = []
top_ten_dict['player_id1'] = []
top_ten_dict['player_name1'] = []
top_ten_dict['player_id2'] = []
top_ten_dict['player_name2'] = []
top_ten_dict['runtime'] = []
top_ten_dict['verification_date'] = []
top_ten_dict['retrieval_date'] = []

# Elden Ring Any% Top Ten
prepare_top_ten_dict(top_ten_dict, table_run_ids, table_top_ten_run_ids, er_anyperc_top10_data,
                     er_categories, er_all_players, ER_NAME)
# Elden Ring Any% Glitchless
prepare_top_ten_dict(top_ten_dict, table_run_ids, table_top_ten_run_ids, er_anyperc_glitchless_top10_data,
                     er_categories, er_all_players, ER_NAME)
# Elden Ring All Remembrances Glitchless Top Ten
prepare_top_ten_dict(top_ten_dict, table_run_ids, table_top_ten_run_ids, er_remembrances_glitchless_top10_data,
                     er_categories, er_all_players, ER_NAME)
# SMO Any% Top Ten
prepare_top_ten_dict(
    top_ten_dict, table_run_ids, table_top_ten_run_ids, smo_anyperc_top10_data, smo_categories, smo_all_players, SMO_NAME)
# SMO 100% Top Ten
prepare_top_ten_dict(
    top_ten_dict, table_run_ids, table_top_ten_run_ids, smo_100perc_top10_data, smo_categories, smo_all_players, SMO_NAME)
# Spyro Any% Top Ten
prepare_top_ten_dict(top_ten_dict, table_run_ids, table_top_ten_run_ids, spyro_anyperc_top10_data,
                     spyro_categories, spyro_all_players, SPYRO_NAME)
# Spyro 120% Top Ten
prepare_top_ten_dict(top_ten_dict, table_run_ids, table_top_ten_run_ids, spyro_120perc_top10_data,
                     spyro_categories, spyro_all_players, SPYRO_NAME)
# Lies of P Any% Top Ten
prepare_top_ten_dict(
    top_ten_dict, table_run_ids, table_top_ten_run_ids, lop_anyperc_top10_data, lop_categories, lop_all_players, LOP_NAME)
# Lies of P All Ergo Bosses Top Ten
prepare_top_ten_dict(top_ten_dict, table_run_ids, table_top_ten_run_ids, lop_allergobosses_top10_data,
                     lop_categories, lop_all_players, LOP_NAME)
top_ten_df = pd.DataFrame(top_ten_dict, columns=['run_id', 'game_name', 'category_id', 'category_name', 'placement',
                                                 'player_id1', 'player_name1', 'player_id2', 'player_name2', 'runtime', 'verification_date', 'retrieval_date'])
print("Completed Transformation...")
print("Beginning Load...")
engine = create_engine(conn_url)
conn = engine.connect()
ids_table_name = "ids"
all_runs_table_name = "all_runs"
top_ten_table_name = "top_ten"

try:
    id_frame = id_df.to_sql(ids_table_name, engine,
                            index=False, if_exists='append')
    all_runs_frame = all_runs_df.to_sql(
        all_runs_table_name, engine, index=False, if_exists='append')
    top_ten_frame = top_ten_df.to_sql(
        top_ten_table_name, engine, index=False, if_exists='append')
except ValueError as vx:
    print(vx)
except Exception as ex:
    print(ex)
else:
    print("All tables have been loaded successfully.")
finally:
    conn.close()
    print("close database successfully")

print("Ending ETL script...")
