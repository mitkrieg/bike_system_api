from datetime import datetime as dt
from logging import exception

from sqlalchemy import func
from models import Rider, Station, Bike, Trip, setup_db
from flask_moment import Moment
from flask_cors import CORS
from flask import Flask, Response, request, abort, jsonify
from auth import AuthError, requires_auth

# from .auth.auth import AuthError, requires_auth

####### Settings ########

ITEMS_PER_PAGE = 10


def create_app():
    ####### App + DB Config #######

    app = Flask(__name__)
    setup_db(app)

    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization, true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS"
        )
        return response

    ####### PAGINATION METHOD ########
    def paginate(request, selection):
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * ITEMS_PER_PAGE
        end = start + ITEMS_PER_PAGE

        items = [item.format() for item in selection]

        return items[start:end]

    ####### ROUTES #######

    ### BIKES ###

    # GET List of Bikes paginated
    @app.route("/bikes")
    @requires_auth(permission="get:bikes")
    def get_bikes(payload):

        try:
            bikes = Bike.query.order_by(Bike.id).all()
            current_page = paginate(request, bikes)
        except:
            abort(422)

        # If no bikes return 404
        if len(current_page) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "bikes": current_page,
                "total_num_bikes": len(bikes),
                "page": request.args.get("page", 1, type=int),
            }
        )

    # create bike
    @app.route("/bikes", methods=["POST"])
    @requires_auth(permission="edit:bikes")
    def create_bike(payload):

        # get data from json
        body = request.get_json()

        model = body.get("model", None)
        manufactured_at = body.get("manufactured_at", None)
        electric = body.get("electric", None)
        current_station_id = body.get("current_station_id", None)

        # if station does not exist return 404
        if current_station_id not in [station.id for station in Station.query.all()]:
            abort(404)

        station = Station.query.get(current_station_id)

        # if station capcity is exceeded by adding a bike return 400
        if station.capacity <= len(station.bikes):
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

            # if no bikes on page return 404
            if len(current_page) == 0:
                abort(404)

            return jsonify(
                {
                    "success": True,
                    "created_bike_id": bike.id,
                    "bikes": current_page,
                    "total_num_bikes": len(bikes),
                    "page": request.args.get("page", 1, type=int),
                }
            )
        except:
            abort(422)

    # delete a bike
    @app.route("/bikes/<bike_id>", methods=["DELETE"])
    @requires_auth(permission="edit:bikes")
    def delete_bike(payload, bike_id):
        bike = Bike.query.get(bike_id)

        # if bike not found return 404
        if bike is None:
            abort(404)

        try:
            bike.delete()
            remaining_bikes = Bike.query.all()
            current_page = paginate(request, remaining_bikes)

            return jsonify(
                {
                    "success": True,
                    "deleted_bike_id": int(bike_id),
                    "bikes": current_page,
                    "total_num_bikes": len(remaining_bikes),
                    "page": request.args.get("page", 1, type=int),
                }
            )
        except:
            abort(500)

    # update bikes
    @app.route("/bikes/<bike_id>", methods=["PATCH"])
    @requires_auth(permission="edit:bikes")
    def update_bike(payload, bike_id):

        # get info from request
        body = request.get_json()

        model = body.get("model", None)
        manufactured_at = body.get("manufactured_at", None)
        electric = body.get("electric", None)
        current_station_id = body.get("current_station_id", None)
        needs_maintenance = body.get("needs_maintenance", None)

        # get bike object
        bike = Bike.query.get(bike_id)

        # return 404 if bike not in database
        if bike is None:
            abort(404)

        # update info only when present request
        if model is not None:
            bike.model = model

        if manufactured_at is not None:
            bike.manufactured_at = manufactured_at

        if electric is not None:
            bike.electric = electric

        if current_station_id is not None:

            # if station does not exist return 404
            if current_station_id not in [
                station.id for station in Station.query.all()
            ]:
                abort(404)

            station = Station.query.get(current_station_id)

            # If there is too many bikes at station return 400
            if station.capacity <= len(station.bikes):
                abort(400)

            bike.current_station_id = current_station_id

        if needs_maintenance is not None:
            bike.needs_maintenance = needs_maintenance

        try:
            bike.update()

            return jsonify({"success": True, "bike_updated": bike.format()})

        except Exception as error:
            abort(422)

    ### Stations ###

    # get all stations
    @app.route("/stations")
    @requires_auth(permission="get:stations")
    def get_stations(payload):

        try:
            stations = Station.query.order_by(Station.id).all()
            current_page = paginate(request, stations)
        except Exception as e:
            abort(422)

        # return 404 if none found on page
        if len(current_page) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "stations": current_page,
                "total_num_stations": len(stations),
                "page": request.args.get("page", 1, type=int),
            }
        )

    # get a specific station and bikes at that station
    @app.route("/stations/<station_id>/bikes")
    @requires_auth(permission="get:stations")
    def get_bikes_at_station(payload, station_id):

        station = Station.query.get(station_id)

        # return 404 if station not found
        if station is None:
            abort(404)

        # gets bikes at station
        bikes = [bike.format() for bike in station.bikes]

        return jsonify(
            {
                "success": True,
                "station_info": station.format(),
                "bikes": bikes,
                "num_bikes": len(bikes),
            }
        )

    # create new station
    @app.route("/stations", methods=["POST"])
    @requires_auth(permission="edit:stations")
    def create_station(payload):

        # retreive request and data
        body = request.get_json()

        name = body.get("name", None)
        capacity = body.get("capacity", None)
        latitude = body.get("latitude", None)
        longitude = body.get("longitude", None)

        try:
            # create new station
            station = Station(
                name=name,
                capacity=capacity,
                latitude=latitude,
                longitude=longitude,
            )

            station.insert()

            stations = Station.query.order_by(Station.id).all()
            current_page = paginate(request, stations)

            # if none found on page return 404
            if len(current_page) == 0:
                abort(404)

            return jsonify(
                {
                    "success": True,
                    "created_station_id": station.id,
                    "stations": current_page,
                    "total_num_stations": len(stations),
                    "page": request.args.get("page", 1, type=int),
                }
            )
        except:
            abort(422)

    # delete station
    @app.route("/stations/<station_id>", methods=["DELETE"])
    @requires_auth(permission="edit:stations")
    def delete_station(payload, station_id):
        station = Station.query.get(station_id)

        # if station not found return 404
        if station is None:
            abort(404)

        try:
            station.delete()
            remaining_stations = Station.query.all()
            current_page = paginate(request, remaining_stations)

            return jsonify(
                {
                    "success": True,
                    "deleted_station_id": int(station_id),
                    "stations": current_page,
                    "page": request.args.get("page", 1, type=int),
                    "total_num_stations": len(remaining_stations),
                }
            )
        except:
            abort(422)

    # update selected station
    @app.route("/stations/<station_id>", methods=["PATCH"])
    @requires_auth(permission="edit:stations")
    def update_station(payload, station_id):

        body = request.get_json()

        name = body.get("name", None)
        capacity = body.get("capacity", None)
        latitude = body.get("latitude", None)
        longitude = body.get("longitude", None)
        active = body.get("active", None)

        station = Station.query.get(station_id)

        # only update is attribute is present
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

        try:
            station.update()

            return jsonify({"success": True, "station_updated": station.format()})

        except Exception as error:
            abort(422)

    #### Riders ####
    # get riders
    @app.route("/riders")
    @requires_auth(permission="get:riders")
    def get_riders(payload):

        try:
            riders = Rider.query.order_by(Rider.id).all()
            current_page = paginate(request, riders)
        except Exception as e:
            abort(422)

        # return 404 if no riders on page
        if len(current_page) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "riders": current_page,
                "total_num_riders": len(riders),
                "page": request.args.get("page", 1, type=int),
            }
        )

        # get a specific station and bikes at that station

    @app.route("/riders/<rider_id>/trips")
    @requires_auth(permission="get:riders")
    def get_trips_of_rider(payload, rider_id):

        rider = Rider.query.get(rider_id)

        # return 404 if station not found
        if rider is None:
            abort(404)

        # gets bikes at station
        trips = [trip.format() for trip in rider.trips]

        return jsonify(
            {
                "success": True,
                "rider_info": rider.format(),
                "trips": trips,
                "num_trips": len(trips),
            }
        )

    # create new rider
    @app.route("/riders", methods=["POST"])
    @requires_auth(permission="edit:riders")
    def create_rider(payload):

        # get data from request
        body = request.get_json()

        name = body.get("name", None)
        email = body.get("email", None)
        address = body.get("address", None)
        membership = body.get("membership", None)

        try:
            # create new rider
            rider = Rider(
                name=name,
                email=email,
                address=address,
                membership=membership,
            )

            rider.insert()

            riders = Rider.query.order_by(Rider.id).all()
            current_page = paginate(request, riders)

            # return 404 if no riders on page
            if len(current_page) == 0:
                abort(404)

            return jsonify(
                {
                    "success": True,
                    "created_rider_id": rider.id,
                    "riders": current_page,
                    "total_num_riders": len(riders),
                    "page": request.args.get("page", 1, type=int),
                }
            )
        except:
            abort(422)

    # delete rider
    @app.route("/riders/<rider_id>", methods=["DELETE"])
    @requires_auth(permission="edit:riders")
    def delete_rider(payload, rider_id):
        rider = Rider.query.get(rider_id)
        print(rider)

        # if rider does not exist return 404
        if rider is None:
            abort(404)

        try:
            rider.delete()
            remaining_riders = Rider.query.all()
            current_page = paginate(request, remaining_riders)

            # return 404 if no riders on page
            if len(current_page) == 0:
                abort(404)

            return jsonify(
                {
                    "success": True,
                    "deleted_rider_id": int(rider_id),
                    "riders": current_page,
                    "page": request.args.get("page", 1, type=int),
                    "total_num_riders": len(remaining_riders),
                }
            )
        except Exception as e:
            abort(422)

    # patch rider
    @app.route("/riders/<rider_id>", methods=["PATCH"])
    @requires_auth(permission="edit:riders")
    def update_rider(payload, rider_id):

        # get data
        body = request.get_json()

        name = body.get("name", None)
        email = body.get("email", None)
        address = body.get("address", None)
        membership = body.get("membership", None)

        # get rider
        rider = Rider.query.get(rider_id)

        # return 404 if rider does not exist
        if rider is None:
            abort(404)

        # onlu update rider information as needed
        if name is not None:
            rider.name = name

        if email is not None:
            rider.email = email

        if address is not None:
            rider.address = address

        if membership is not None:
            rider.membership = membership

        try:
            rider.update()

            return jsonify({"success": True, "rider_updated": rider.format()})

        except Exception as error:
            abort(422)

    #### Trips ####
    # get list of trips
    @app.route("/trips")
    @requires_auth(permission="get:trips")
    def get_trips(payload):

        try:
            trips = Trip.query.order_by(Trip.id).all()
            current_page = paginate(request, trips)
        except Exception as e:
            abort(422)

        # return 404 if no trips on page
        if len(current_page) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "trips": current_page,
                "total_num_trips": len(trips),
                "page": request.args.get("page", 1, type=int),
            }
        )

    # Start a trip
    @app.route("/trips", methods=["POST"])
    @requires_auth("create:trips")
    def start_trip(payload):

        # get trip info from request
        body = request.get_json()

        bike_id = body.get("bike_id", None)
        rider_id = body.get("rider_id", None)
        start_time = dt.now()

        # abort if bike is already taken on unended trip
        if bike_id in [
            trip.bike_id for trip in Trip.query.filter(Trip.end_time == None).all()
        ]:
            abort(400)

        try:
            # Get original station wherever the bike currently is
            origination_station_id = Bike.query.get(bike_id).current_station_id

            # create strip and insert into db
            trip = Trip(rider_id, origination_station_id, bike_id, start_time)
            trip.insert()

            return jsonify(
                {
                    "success": True,
                    "started_trip": {
                        "bike_id": trip.bike_id,
                        "rider_id": trip.rider_id,
                        "origination_station_id": trip.origination_station_id,
                        "start_time": trip.start_time,
                        "trip_id": trip.id,
                    },
                }
            )
        except Exception as e:
            abort(422)

    # end a trip
    @app.route("/trips/<trip_id>", methods=["PATCH"])
    @requires_auth("create:trips")
    def end_trip(payload, trip_id):

        # get ending location
        body = request.get_json()
        destination_station_id = body.get("destination_station_id", None)

        trip = Trip.query.get(trip_id)

        # abort if trip not found
        if trip is None:
            abort(404)

        # get bike used in trip and end station
        bike = Bike.query.get(trip.bike_id)
        end_station = Station.query.get(destination_station_id)

        # about if end station not found
        if end_station is None:
            abort(404)
        # abort if trip has already ended
        elif trip.end_time is not None:
            abort(400)
        # abort if there are too many bikes at station
        elif end_station.capacity <= len(end_station.bikes):
            abort(400)
        # if ok end trip
        else:
            end_time = dt.now()

        try:
            trip.end_time = end_time
            trip.destination_station_id = destination_station_id

            bike.current_station_id = destination_station_id

            bike.update()
            trip.update()

            return jsonify(
                {
                    "success": True,
                    "ended_trip": trip.format(),
                }
            )
        except:
            abort(422)

    ##### ERROR HANDLERS ######

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": 400,
                    "message": "Bad request. Please try again",
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
    def unprocessable(error):
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
    def internal_error(error):
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

    @app.errorhandler(AuthError)
    def auth_error(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": error.status_code,
                    "message": error.error,
                }
            ),
            error.status_code,
        )

    return app


app = create_app()
