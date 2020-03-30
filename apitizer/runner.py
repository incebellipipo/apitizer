import json
from flask import Flask
from flask import jsonify
from flask_restful import Api
from flask_cors import CORS

from apitizer import data_updater
from apitizer import db_controller

app = Flask(__name__)
api = Api(app)

CORS(app)

with open('config/config.json') as f:
    config = json.load(f)
updater = data_updater.Updater(config)
updater.initiate()

database = db_controller.DatabaseController()


@app.route("/", methods=['GET'])
def today():
    result = database.find_one()
    del result["_id"]
    return result


@app.route("/all", methods=['GET'])
def all():
    query = database.find()
    result = []
    for r in query:
        del r["_id"]
        result.append(r)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0")

