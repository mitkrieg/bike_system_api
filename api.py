from datetime import datetime as dt
from logging import exception

from sqlalchemy import func
from models import Rider, Station, Bike, Trip, setup_db
from flask_moment import Moment
from flask_cors import CORS
from flask import Flask, Response, request, abort, jsonify

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
                "success": True,
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

        if station.capacity <= len(station.bikes):
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
                    "success": True,
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
                "success": True,
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
                    "success": True,
                    "created_station_id": station.id,
                    "station": current_page,
                    "total_num_stations": len(stations),
                    "page": request.args.get("page", 1, type=int),
                }
            )
        except:
            abort(422)

    @app.route("/stations/<station_id>", methods=["DELETE"])
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

    @app.route("/stations/<station_id>", methods=["PATCH"])
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

    #### Riders ####

    @app.route("/riders")
    def get_riders():

        try:
            riders = Rider.query.order_by(Rider.id).all()
            current_page = paginate(request, riders)
        except Exception as e:
            print(e)
            abort(422)

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

    @app.route("/riders", methods=["POST"])
    def create_rider():

        body = request.get_json()

        name = body.get("name", None)
        email = body.get("email", None)
        address = body.get("address", None)
        membership = body.get("membership", None)

        try:

            rider = Rider(
                name=name,
                email=email,
                address=address,
                membership=membership,
            )

            rider.insert()

            riders = Rider.query.order_by(Rider.id).all()
            current_page = paginate(request, riders)

            if len(current_page) == 0:
                abort(404)

            return jsonify(
                {
                    "success": True,
                    "created_station_id": rider.id,
                    "riders": current_page,
                    "total_num_riders": len(riders),
                    "page": request.args.get("page", 1, type=int),
                }
            )
        except:
            abort(422)

    @app.route("/riders/<rider_id>", methods=["DELETE"])
    def delete_rider(rider_id):
        rider = Station.query.get(rider_id)

        if rider is None:
            abort(404)

        try:
            rider.delete()
            remaining_riders = Station.query.all()
            current_page = paginate(request, remaining_riders)

            return jsonify(
                {
                    "success": True,
                    "deleted": rider_id,
                    "stations": current_page,
                    "total_num_riders": len(remaining_riders),
                }
            )
        except:
            abort(500)

    @app.route("/riders/<rider_id>", methods=["PATCH"])
    def update_rider(rider_id):

        body = request.get_json()

        name = body.get("name", None)
        email = body.get("email", None)
        address = body.get("address", None)
        membership = body.get("membership", None)

        try:
            rider = Station.query.get(rider_id)
            if rider is None:
                abort(404)

            if name is not None:
                rider.name = name

            if email is not None:
                rider.email = email

            if address is not None:
                rider.address = address

            if membership is not None:
                rider.membership = membership

            rider.update()

            return jsonify({"success": True, "station_updated": rider.format()})

        except Exception as error:
            print(error)
            abort(422)

    #### Trips ####

    @app.route("/trips")
    def get_trips():

        try:
            trips = Trip.query.order_by(Trip.id).all()
            current_page = paginate(request, trips)
        except Exception as e:
            print(e)
            abort(422)

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

    @app.route("/trips", methods=["POST"])
    def start_trip():

        body = request.get_json()
        print(body)

        bike_id = body.get("bike_id", None)
        rider_id = body.get("rider_id", None)
        start_time = dt.now()

        print(bike_id)
        print(rider_id)

        # abort if bike is already taken on unended trip
        if bike_id in [
            trip.bike_id for trip in Trip.query.filter(Trip.end_time == None).all()
        ]:
            abort(400)

        try:
            origination_station_id = Bike.query.get(bike_id).current_station_id
            print(origination_station_id)

            trip = Trip(rider_id, origination_station_id, bike_id, start_time)
            trip.insert()
            print(trip.end_time)

            return jsonify(
                {
                    "sucess": True,
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
            print(e)
            abort(422)

    @app.route("/trips/<trip_id>", methods=["PATCH"])
    def end_trip(trip_id):

        body = request.get_json()
        destination_station_id = body.get("destination_station_id", None)
        end_time = dt.now()

        print(body)

        trip = Trip.query.get(trip_id)
        bike = Bike.query.get(trip.bike_id)
        end_station = Station.query.get(destination_station_id)
        print(end_station.name)

        # abort if trip or end_station not found
        if trip is None or end_station is None:
            abort(404)
        # abort if trip has already ended
        elif trip.end_time is not None:
            abort(400)
        # abort if there are too many bikes at station
        elif end_station.capacity <= len(end_station.bikes):
            abort(400)

        try:
            trip.end_time = end_time
            trip.destination_station_id = destination_station_id
            print("xxxxx")

            bike.current_station_id = destination_station_id

            bike.update()
            trip.update()

            return jsonify(
                {
                    "sucess": True,
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
    def internal_error(error):
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
    # def auth_error(error):
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

    return app


APP = create_app()

if __name__ == "__main__":
    APP.run(host="localhost", port=5000, debug=True)
