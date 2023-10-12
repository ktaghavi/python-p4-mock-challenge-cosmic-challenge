#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.get('/scientists')
def get_all_scientists():
    scientists = Scientist.query.all()
    data = [scientist.to_dict(rules=('-missions',)) for scientist in scientists]

    return make_response(
        jsonify(data),
        200
    )

@app.get('/scientists/<int:id>')
def get_scientist_by_id(id):
    scientist = Scientist.query.filter(Scientist.id == id).first()

    if not scientist:
        return make_response(
            jsonify({"error": "Scientist not found"}),
            404
        )
    
    return make_response(
        jsonify(scientist.to_dict()),
        200
    )

@app.post('/scientists')
def post_scientist():
    data = request.get_json()

    try:
        new_scientist = Scientist(
            name=data.get('name'),
            field_of_study=data.get('field_of_study'),
        )
        db.session.add(new_scientist)
        db.session.commit()

        return make_response(
            jsonify(new_scientist.to_dict(rules=('-missions',))),
            201
        )
    except ValueError:
        return make_response(
            jsonify({"error": "Scientist not found"}),
            406
        )

@app.patch('/scientists/<int:id>')
def patch_scientist_by_id(id):
    scientist = Scientist.query.filter(Scientist.id == id).first()
    data = request.get_json()

    if not scientist:
        return make_response(
            jsonify({"errors": ["validation errors"]}),
            404
        )
    try:
        for field in data:
            setattr(scientist, field, data[field])
        db.session.add(scientist)
        db.session.commit()

        return make_response(
            jsonify(scientist.to_dict(rules=('-missions',))),
            202
        )
    except ValueError:
        return make_response(
            jsonify({"error": "Scientist not found"}),
            406
        )

@app.delete('/scientists/<int:id>')
def delete_scientist(id):
    scientist = Scientist.query.filter(id == id).first()

    if not scientist:
        return make_response(
            jsonify({"error": "Scientist not found"}),
            404
        )
    db.session.add(scientist)
    db.session.commit()

    return make_response(jsonify({}), 204)

###########################################################

@app.get('/planets')
def get_all_planets():
    planets = Planet.query.all()
    data = [planet.to_dict(rules=('-missions',)) for planet in planets]

    return make_response(
        jsonify(data),
        200
    )

@app.post('/missions')
def post_missions():
    data = request.get_json()

    try:
        new_mission = Mission(
            name=data.get('name'),
            scientist_id=data.get('scientist_id'),
            planet_id=data.get('planet_id')
        )
        db.session.add(new_mission)
        db.session.commit()

        return make_response(
            jsonify(new_mission.to_dict(rules=('-scientist.missions', '-planet.missions'))),
            201
        )
    except ValueError:
        return make_response(
            jsonify({"error": "Scientist not found"}),
            406
        )

if __name__ == '__main__':
    app.run(port=5555, debug=True)
