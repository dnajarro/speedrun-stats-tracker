from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import select, and_
from flask_cors import CORS
from os import environ
from datetime import datetime, timedelta
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
        one_week_ago = datetime.now() - timedelta(days=7)
        result = db.session.query(AllRuns).filter(and_(
            AllRuns.retrieval_date > one_week_ago, AllRuns.retrieval_date <= datetime.now())).all()
        for run in result:
            response[run.game_name].append(run.json())
        return make_response(jsonify(response), 200)
    except Exception as e:
        return make_response(jsonify({'message': 'error getting runs', 'error': str(e)}), 500)


# route to retrieve all top ten results


@app.route('/api/flask/topten', methods=['GET'])
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
