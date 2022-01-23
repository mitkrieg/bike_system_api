from datetime import datetime as dt
from logging import exception
from .models import Rider, Station, Bike, Trip, setup_db
from flask_moment import Moment
from flask_cors import CORS
from flask import Flask, Response, request, abort, jsonify

# from .auth.auth import AuthError, requires_auth

####### Settings ########

ITEMS_PER_PAGE = 10

####### App + DB Config #######

app = Flask(__name__)
setup_db(app)

CORS(app)

####### PAGINATION METHOD ########
def paginate(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE

    items = [item.format() for item in selection]

    return items[start:end]


####### ROUTES #######

### BIKES ###
@app.route("/")
def tester():
    return jsonify({"success": "true", "message": "this tests the APP"})


@app.route("/bikes")
def get_bikes():

    try:
        bikes = Bike.query.order_by(Bike.id).all()
        current_page = paginate(request, bikes)
    except:
        abort(422)

    if len(current_page) == 0:
        abort(404)

    return jsonify(
        {
            "success": "true",
            "bikes": current_page,
            "total_num_bikes": len(bikes),
            "page": request.args.get("page", 1, type=int),
        }
    )


@app.route("/bikes", methods=["POST"])
def create_bike():

    body = request.get_json()

    model = body.get("model", None)
    manufactured_at = body.get("manufactured_at", None)
    electric = body.get("electric", None)
    current_station_id = body.get("current_station_id", None)

    if current_station_id is None or current_station_id not in [
        station.id for station in Station.query.all()
    ]:
        print("station not found")
        abort(404)

    station = Station.query.get(current_station_id)

    if station.capacity >= len(station.bikes):
        print("too many bikes at station")
        abort(400)

    try:

        bike = Bike(
            model=model,
            manufactured_at=manufactured_at,
            electric=electric,
            current_station_id=current_station_id,
        )

        bike.insert()

        bikes = Bike.query.order_by(Bike.id).all()
        current_page = paginate(request, bikes)

        if len(current_page) == 0:
            abort(404)

        return jsonify(
            {
                "success": "true",
                "created_bike_id": bike.id,
                "bikes": current_page,
                "total_num_bikes": len(bikes),
                "page": request.args.get("page", 1, type=int),
            }
        )
    except:
        abort(422)


@app.route("/bikes/<bike_id>", methods=["DELETE"])
def delete_bike(bike_id):
    bike = Bike.query.get(bike_id)

    if bike is None:
        abort(404)

    try:
        bike.delete()
        remaining_bikes = Bike.query.all()
        current_page = paginate(request, remaining_bikes)

        return jsonify(
            {
                "success": True,
                "deleted": bike_id,
                "bikes": current_page,
                "total_bikes": len(remaining_bikes),
            }
        )
    except:
        abort(500)


@app.route("/bikes/<bike_id>", methods=["PATCH"])
def update_bike(bike_id):

    body = request.get_json()

    model = body.get("model", None)
    manufactured_at = body.get("manufactured_at", None)
    electric = body.get("electric", None)
    current_station_id = body.get("current_station_id", None)
    needs_maintenance = body.get("needs_maintenance", None)

    try:
        bike = Bike.query.get(bike_id)
        if bike is None:
            abort(404)

        if model is not None:
            bike.model = model

        if manufactured_at is not None:
            bike.manufactured_at = manufactured_at

        if electric is not None:
            bike.electric = electric

        if current_station_id is None or current_station_id not in [
            station.id for station in Station.query.all()
        ]:
            print("station not found")
            abort(404)

        station = Station.query.get(current_station_id)

        if station.capacity >= len(station.bikes):
            print("too many bikes at station")
            abort(400)

        bike.current_station_id = current_station_id

        if needs_maintenance is not None:
            bike.needs_maintenance = needs_maintenance

        bike.update()

        return jsonify({"success": True, "bike_updated": bike.format()})

    except Exception as error:
        print(error)
        abort(422)


### Stations ###
@app.route("/stations")
def get_stations():

    try:
        stations = Station.query.order_by(Station.id).all()
        current_page = paginate(request, stations)
    except Exception as e:
        print(e)
        abort(422)

    if len(current_page) == 0:
        abort(404)

    return jsonify(
        {
            "success": "true",
            "stations": current_page,
            "total_num_stations": len(stations),
            "page": request.args.get("page", 1, type=int),
        }
    )


@app.route("/stations", methods=["POST"])
def create_station():

    body = request.get_json()

    name = body.get("name", None)
    capacity = body.get("capacity", None)
    latitude = body.get("latitude", None)
    longitude = body.get("longitude", None)

    try:

        station = Station(
            name=name,
            capacity=capacity,
            latitude=latitude,
            longitude=longitude,
        )

        station.insert()

        stations = Station.query.order_by(Station.id).all()
        current_page = paginate(request, stations)

        if len(current_page) == 0:
            abort(404)

        return jsonify(
            {
                "success": "true",
                "created_station_id": station.id,
                "station": current_page,
                "total_num_stations": len(stations),
                "page": request.args.get("page", 1, type=int),
            }
        )
    except:
        abort(422)


@app.route("/station/<station_id>", methods=["DELETE"])
def delete_station(station_id):
    station = Station.query.get(station_id)

    if station is None:
        abort(404)

    try:
        station.delete()
        remaining_stations = Station.query.all()
        current_page = paginate(request, remaining_stations)

        return jsonify(
            {
                "success": True,
                "deleted": station_id,
                "stations": current_page,
                "total_stations": len(remaining_stations),
            }
        )
    except:
        abort(500)


@app.route("/station/<station_id>", methods=["PATCH"])
def update_station(station_id):

    body = request.get_json()

    name = body.get("name", None)
    capacity = body.get("capacity", None)
    latitude = body.get("latitude", None)
    longitude = body.get("longitude", None)
    active = body.get("active", None)

    try:
        station = Station.query.get(station_id)
        if station is None:
            abort(404)

        if name is not None:
            station.name = name

        if capacity is not None:
            station.capacity = capacity

        if latitude is not None:
            station.latitude = latitude

        if longitude is not None:
            station.longitude = longitude

        if active is not None:
            station.active = active

        station.update()

        return jsonify({"success": True, "station_updated": station.format()})

    except Exception as error:
        print(error)
        abort(422)


##### ERROR HANDLERS ######


@app.errorhandler(400)
def bad_request(error):
    return (
        jsonify(
            {
                "success": False,
                "error": 400,
                "message": "Malformed request. Please try again",
            }
        ),
        400,
    )


@app.errorhandler(404)
def not_found(error):
    return (
        jsonify(
            {
                "success": False,
                "error": 404,
                "message": "Resource Not Found",
            }
        ),
        404,
    )


@app.errorhandler(422)
def bad_request(error):
    print(error)
    return (
        jsonify(
            {
                "success": False,
                "error": 422,
                "message": "Unprocessable",
            }
        ),
        422,
    )


@app.errorhandler(500)
def bad_request(error):
    print(error)
    return (
        jsonify(
            {
                "success": False,
                "error": 500,
                "message": "Internal Service Error",
            }
        ),
        500,
    )


# @app.errorhandler(AuthError)
# def bad_request(error):
#     return (
#         jsonify(
#             {
#                 "success": False,
#                 "error": error.status_code,
#                 "message": error.error,
#             }
#         ),
#         error.status_code,
#     )
