from models import Rider, Station, Bike, Trip, setup_db
from flask_moment import Moment
from flask_cors import CORS
from flask import Flask, Response, request, abort, jsonify


####### App + DB Config #######

app = Flask(__name__)
setup_db(app)

CORS(app)


####### ROUTES #######



if __name__ == '__main__':
    app.run(debug=True)