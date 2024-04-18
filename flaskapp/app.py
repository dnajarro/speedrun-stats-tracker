from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import select, and_
from flask_cors import CORS
from os import environ
from datetime import datetime, timedelta
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from io import BytesIO
import matplotlib.pyplot as plt
import base64
import time


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
CORS(app)   # Enable CORS for all routes
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL')
# db = SQLAlchemy(app)
db.init_app(app)
time.sleep(5)


class TopTen(db.Model):
    __tablename__ = 'top_ten'
    run_id = db.Column(db.String(50), primary_key=True)
    game_name = db.Column(db.String(50), unique=False, nullable=False)
    category_id = db.Column(db.String(100), unique=False, nullable=False)
    placement = db.Column(db.Integer, unique=False, nullable=False)
    player_id1 = db.Column(db.String(50), unique=True, nullable=True)
    player_name1 = db.Column(db.String(50), unique=True, nullable=False)
    player_id2 = db.Column(db.String(50), unique=True, nullable=True)
    player_name2 = db.Column(db.String(50), unique=True, nullable=True)
    runtime = db.Column(db.Integer, unique=False, nullable=False)
    verification_date = db.Column(db.DateTime, unique=False, nullable=False)
    retrieval_date = db.Column(db.DateTime, unique=False, nullable=False)

    def json(self):
        return {
            'run_id': self.run_id,
            'game_name': self.game_name,
            'category_id': self.category_id,
            'placement': self.placement,
            'player_id1': self.player_id1,
            'player_name1': self.player_name1,
            'player_id2': self.player_id2,
            'player_name2': self.player_name2,
            'runtime': self.runtime,
            'verification_date': self.verification_date,
            'retrieval_date': self.retrieval_date
        }


class AllRuns(db.Model):
    __tablename__ = 'all_runs'
    run_id = db.Column(db.String(50), primary_key=True)
    game_name = db.Column(db.String(50), unique=False, nullable=False)
    category_id = db.Column(db.String(100), unique=False, nullable=False)
    category_name = db.Column(db.String(100), unique=False, nullable=False)
    player_id1 = db.Column(db.String(50), unique=True, nullable=True)
    player_name1 = db.Column(db.String(50), unique=True, nullable=False)
    player_id2 = db.Column(db.String(50), unique=True, nullable=True)
    player_name2 = db.Column(db.String(50), unique=True, nullable=True)
    runtime = db.Column(db.Integer, unique=False, nullable=False)
    retrieval_date = db.Column(db.DateTime, unique=False, nullable=False)

    def json(self):
        return {
            'run_id': self.run_id,
            'game_name': self.game_name,
            'category_id': self.category_id,
            'category_name': self.category_name,
            'player_id1': self.player_id1,
            'player_name1': self.player_name1,
            'player_id2': self.player_id2,
            'player_name2': self.player_name2,
            'runtime': self.runtime,
            'retrieval_date': self.retrieval_date
        }


class Ids(db.Model):
    __tablename__ = 'ids'
    id = db.Column(db.String(50), primary_key=True)
    speedrun_id = db.Column(db.String(50))
    id_type = db.Column(db.String(50))
    label_name = db.Column(db.String(50))

    def json(self):
        return {'id': self.id, 'speedrun_id': self.speedrun_id, 'id_type': self.id_type, 'label_name': self.label_name}

# # create a test route


@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'The server is running'})

# route to retrieve all runs


@app.route('/api/flask/allruns', methods=['GET'])
def get_all_runs():
    try:
        er_name = 'Elden Ring'
        smo_name = 'Super Mario Odyssey'
        spyro_name = 'Spyro the Dragon'
        lop_name = 'Lies of P'

        response = {
            er_name: [], smo_name: [],
            spyro_name: [], lop_name: []
        }

        stmt = select(AllRuns)
        result = db.session.execute(stmt)
        for run in result.scalars():
            response[run.game_name].append(run.json())
        return make_response(jsonify(response), 200)
    except Exception as e:
        return make_response(jsonify({'message': 'error getting runs', 'error': str(e)}), 500)


# route to retrieve recent runs from last week


@app.route('/api/flask/recentruns', methods=['GET'])
def get_last_week_runs():
    try:
        er_name = 'Elden Ring'
        smo_name = 'Super Mario Odyssey'
        spyro_name = 'Spyro the Dragon'
        lop_name = 'Lies of P'

        response = {
            er_name: [], smo_name: [],
            spyro_name: [], lop_name: []
        }
        one_week_ago = datetime.now() - timedelta(days=6, hours=23)
        result = db.session.query(AllRuns).filter(and_(
            AllRuns.retrieval_date > one_week_ago, AllRuns.retrieval_date <= datetime.now())).all()
        for run in result:
            response[run.game_name].append(run.json())
        return make_response(jsonify(response), 200)
    except Exception as e:
        return make_response(jsonify({'message': 'error getting runs', 'error': str(e)}), 500)


# route to retrieve all top ten results


@app.route('/api/flask/toptens', methods=['GET'])
def get_top_ten():
    try:
        er_anyperc = 'Elden Ring Any%'
        er_anyperc_glitchless = 'Elden Ring Any% Glitchless'
        er_remembrances_glitchless = 'Elden Ring All Remembrances Glitchless'

        smo_anyperc = 'Super Mario Odyssey Any%'
        smo_100perc = 'Super Mario Odyssey 100%'

        spyro_anyperc = 'Spyro Any%'
        spyro_120perc = 'Spyro 120%'

        lop_anyperc = 'Lies of P Any%'
        lop_allergobosses = 'Lies of P All Ergo Bosses'

        er_anyperc_id = "02qr00pk"
        er_anyperc_glitchless_id = "w20e4yvd"
        er_remembrances_glitchless_id = "9d8nl33d"

        smo_anyperc_id = "w20w1lzd"
        smo_100perc_id = "n2y5jwek"

        spyro_anyperc_id = "lvdo8ykp"
        spyro_120perc_id = "7wkp1gkr"

        lop_anyperc_id = "mke1p392"
        lop_allergobosses_id = "xk9z63x2"

        category_dict = {
            er_anyperc_id: er_anyperc,
            er_anyperc_glitchless_id: er_anyperc_glitchless,
            er_remembrances_glitchless_id: er_remembrances_glitchless,
            smo_anyperc_id: smo_anyperc,
            smo_100perc_id: smo_100perc,
            spyro_anyperc_id: spyro_anyperc,
            spyro_120perc_id: spyro_120perc,
            lop_anyperc_id: lop_anyperc,
            lop_allergobosses_id: lop_allergobosses
        }

        response = {
            er_anyperc: [],
            er_anyperc_glitchless: [],
            er_remembrances_glitchless: [],
            smo_anyperc: [],
            smo_100perc: [],
            spyro_anyperc: [],
            spyro_120perc: [],
            lop_anyperc: [],
            lop_allergobosses: []
        }

        stmt = select(TopTen).order_by(TopTen.placement)
        result = db.session.execute(stmt)
        for run in result.scalars():
            response[category_dict[run.category_id]].append(run.json())
        return make_response(jsonify(response), 200)
    except Exception as e:
        return make_response(jsonify({'message': 'error getting runs', 'error': str(e)}), 500)

# route to retrieve all first place results


@app.route('/api/flask/firstplace', methods=['GET'])
def get_first_places():
    try:
        er_anyperc = 'Elden Ring Any%'
        er_anyperc_glitchless = 'Elden Ring Any% Glitchless'
        er_remembrances_glitchless = 'Elden Ring All Remembrances Glitchless'

        smo_anyperc = 'Super Mario Odyssey Any%'
        smo_100perc = 'Super Mario Odyssey 100%'

        spyro_anyperc = 'Spyro Any%'
        spyro_120perc = 'Spyro 120%'

        lop_anyperc = 'Lies of P Any%'
        lop_allergobosses = 'Lies of P All Ergo Bosses'

        er_anyperc_id = "02qr00pk"
        er_anyperc_glitchless_id = "w20e4yvd"
        er_remembrances_glitchless_id = "9d8nl33d"

        smo_anyperc_id = "w20w1lzd"
        smo_100perc_id = "n2y5jwek"

        spyro_anyperc_id = "lvdo8ykp"
        spyro_120perc_id = "7wkp1gkr"

        lop_anyperc_id = "mke1p392"
        lop_allergobosses_id = "xk9z63x2"

        category_dict = {
            er_anyperc_id: er_anyperc,
            er_anyperc_glitchless_id: er_anyperc_glitchless,
            er_remembrances_glitchless_id: er_remembrances_glitchless,
            smo_anyperc_id: smo_anyperc,
            smo_100perc_id: smo_100perc,
            spyro_anyperc_id: spyro_anyperc,
            spyro_120perc_id: spyro_120perc,
            lop_anyperc_id: lop_anyperc,
            lop_allergobosses_id: lop_allergobosses
        }

        response = {
            er_anyperc: [],
            er_anyperc_glitchless: [],
            er_remembrances_glitchless: [],
            smo_anyperc: [],
            smo_100perc: [],
            spyro_anyperc: [],
            spyro_120perc: [],
            lop_anyperc: [],
            lop_allergobosses: []
        }
        stmt = select(TopTen).where(
            TopTen.placement == 1).order_by(TopTen.retrieval_date)
        result = db.session.execute(stmt)
        for run in result.scalars():
            if run.category_id in category_dict:
                response[category_dict[run.category_id]].append(run.json())
        return make_response(jsonify(response), 200)
    except Exception as e:
        return make_response(jsonify({'message': 'error getting runs', 'error': str(e)}), 500)

# route to create the graph for first place time progression


@app.route('/api/flask/firstplace/graph', methods=['GET'])
def get_first_place_time_graph():
    try:
        er_anyperc_id = "02qr00pk"
        er_anyperc = 'Elden Ring Any%'
        er_anyperc_glitchless = 'Elden Ring Any% Glitchless'
        er_remembrances_glitchless = 'Elden Ring All Remembrances Glitchless'

        smo_anyperc = 'Super Mario Odyssey Any%'
        smo_100perc = 'Super Mario Odyssey 100%'

        spyro_anyperc = 'Spyro Any%'
        spyro_120perc = 'Spyro 120%'

        lop_anyperc = 'Lies of P Any%'
        lop_allergobosses = 'Lies of P All Ergo Bosses'

        er_anyperc_glitchless_id = "w20e4yvd"
        er_remembrances_glitchless_id = "9d8nl33d"

        smo_anyperc_id = "w20w1lzd"
        smo_100perc_id = "n2y5jwek"

        spyro_anyperc_id = "lvdo8ykp"
        spyro_120perc_id = "7wkp1gkr"

        lop_anyperc_id = "mke1p392"
        lop_allergobosses_id = "xk9z63x2"

        first_place_dict = {
            er_anyperc_id: {},
            er_anyperc_glitchless_id: {},
            er_remembrances_glitchless_id: {},
            smo_anyperc_id: {},
            smo_100perc_id: {},
            spyro_anyperc_id: {},
            spyro_120perc_id: {},
            lop_anyperc_id: {},
            lop_allergobosses_id: {}
        }

        category_dict = {
            er_anyperc_id: er_anyperc,
            er_anyperc_glitchless_id: er_anyperc_glitchless,
            er_remembrances_glitchless_id: er_remembrances_glitchless,
            smo_anyperc_id: smo_anyperc,
            smo_100perc_id: smo_100perc,
            spyro_anyperc_id: spyro_anyperc,
            spyro_120perc_id: spyro_120perc,
            lop_anyperc_id: lop_anyperc,
            lop_allergobosses_id: lop_allergobosses
        }

        stmt = select(TopTen).where(
            TopTen.placement == 1).order_by(TopTen.retrieval_date)
        result = db.session.execute(stmt)
        for run in result.scalars():
            if run.category_id in category_dict:
                if run.retrieval_date not in first_place_dict[run.category_id]:
                    first_place_dict[run.category_id][run.retrieval_date] = []
                    if len(first_place_dict[run.category_id]) > 1:
                        prev_retrieval_date = first_place_dict[run.category_id].keys(
                        )[-2]
                        prev_runtimes = first_place_dict[run.category_id][prev_retrieval_date]
                        first_place_dict[run.category_id][run.retrieval_date] = [
                            x for x in prev_runtimes]
                first_place_dict[run.category_id][run.retrieval_date].append(
                    run.runtime)
        for category_id in first_place_dict.keys():
            for retrieval_date in first_place_dict[category_id].keys():
                min_time = min(
                    first_place_dict[category_id][retrieval_date])
                first_place_dict[category_id][retrieval_date] = [
                    min_time]
        fig, ax = plt.subplots(1, 1)
        ax.set_title('Fastest times for each category each week')
        ax.set_xlabel('Retrieval date')
        ax.set_ylabel('Runtime (s)')
        retrieval_dates = []
        for category_id in first_place_dict.keys():
            runtimes = []
            retrieval_dates = list(first_place_dict[category_id].keys())
            retrieval_dates.sort()
            for retrieval_date in retrieval_dates:
                runtimes.append(
                    first_place_dict[category_id][retrieval_date][0])
            category_name = category_dict[category_id]
            category_words = category_name.split(" ")
            condensed_category = ""
            if len(category_words) > 2:
                for i in range(len(category_words)):
                    if i % 2 == 0 and i > 0:
                        condensed_category += "\n"
                    elif i > 0:
                        condensed_category += " "
                    condensed_category += category_words[i]
            else:
                condensed_category = category_dict[category_id]
            ax.plot(retrieval_dates, runtimes, 'o-',
                    label=condensed_category)

        fig.legend(loc=7)
        fig.tight_layout()
        fig.subplots_adjust(right=0.75)
        buffer = BytesIO()
        FigureCanvasAgg(fig).print_png(buffer)

        img = base64.b64encode(buffer.getvalue()).decode()
        return make_response(jsonify({'img': img}), 200)
    except Exception as e:
        return make_response(jsonify({'message': 'error getting first place time graph', 'error': str(e)}), 500)

# route to create the graph for the number of runs submitted since first recorded


@app.route('/api/flask/allruns/graph', methods=['GET'])
def get_runs_graph():
    try:
        er_name = 'Elden Ring'
        smo_name = 'Super Mario Odyssey'
        spyro_name = 'Spyro the Dragon'
        lop_name = 'Lies of P'

        all_runs_dict = {
            er_name: {}, smo_name: {},
            spyro_name: {}, lop_name: {}
        }

        stmt = select(AllRuns).order_by(AllRuns.retrieval_date)
        result = db.session.execute(stmt)
        for run in result.scalars():
            if run.game_name in all_runs_dict:
                if run.retrieval_date not in all_runs_dict[run.game_name]:
                    all_runs_dict[run.game_name][run.retrieval_date] = 0
                    if len(all_runs_dict[run.game_name]) > 1:
                        prev_retrieval_date = all_runs_dict[run.game_name].keys(
                        )[-2]
                        prev_runs = all_runs_dict[run.game_name][prev_retrieval_date]
                        all_runs_dict[run.game_name][run.retrieval_date] = prev_runs
                all_runs_dict[run.game_name][run.retrieval_date] += 1
        fig, ax = plt.subplots(1, 1)
        ax.set_title('Number of runs submitted by game each week')
        ax.set_xlabel('Retrieval date')
        ax.set_ylabel('Number of runs')
        for game_name in all_runs_dict.keys():
            num_runs = []
            retrieval_dates = list(all_runs_dict[game_name].keys())
            retrieval_dates.sort()
            for retrieval_date in retrieval_dates:
                num_runs.append(all_runs_dict[game_name][retrieval_date])
            ax.plot(retrieval_dates, num_runs, 'o-', label=game_name)
        fig.legend(loc=7)
        fig.tight_layout()
        fig.subplots_adjust(right=0.7)
        buffer = BytesIO()
        FigureCanvasAgg(fig).print_png(buffer)

        img = base64.b64encode(buffer.getvalue()).decode()
        return make_response(jsonify({'img': img}), 200)
    except Exception as e:
        return make_response(jsonify({'message': 'error getting number of runs submitted graph', 'error': str(e)}), 500)
