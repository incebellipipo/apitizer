import json
from flask import Flask
from flask_restful import Api
from flask_cors import CORS

from apitizer import img_parser

app = Flask(__name__)
api = Api(app)

CORS(app)

with open('config/config.json') as f:
    config = json.load(f)

parser = img_parser.ImageParser(config)


@app.route("/", methods=['GET'])
def daily():
    return parser.get_results()


app.run()

