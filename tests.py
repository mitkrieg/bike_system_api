import unittest
import json
from wsgiref import headers
from flask_sqlalchemy import SQLAlchemy
import os
from app import create_app
from models import setup_db, Station, Bike, Trip, Rider, DATABASE_PATH


RIDER_BEARER_TOKEN = os.getenv("RIDER_TOKEN")
MANAGER_BEARER_TOKEN = os.getenv("MANAGER_TOKEN")


class BikeSystemTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.test_bike = {
            "model": "test",
            "manufactured_at": "2021-01-03",
            "electric": False,
            "current_station_id": 4,
        }
        self.test_station = {
            "name": "Testing Street",
            "capacity": 10,
            "latitude": 40.33,
            "longitude": -45.66,
        }
        self.test_rider = {
            "name": "Test",
            "email": "test@abc.com",
            "address": "123 Seasame Street",
            "membership": True,
        }

        self.rider_auth_header = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + str(RIDER_BEARER_TOKEN),
        }
        self.manager_auth_header = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + str(MANAGER_BEARER_TOKEN),
        }

        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.create_all()

    def tear_down(self):
        pass

    def test_get_bikes(self):
        """Test for successful GET bikes endpoint"""
        res = self.client().get("/bikes", headers=self.rider_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)  # Good request code
        self.assertEqual(data["success"], True)  # json says success
        self.assertEqual(len(data["bikes"]), 10)  # returns paginated bike info
        self.assertTrue(data["total_num_bikes"])  # returns number of bikes

    def test_get_stations(self):
        """Test for successful GET stations"""
        res = self.client().get("/stations", headers=self.manager_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)  # Good request code
        self.assertEqual(data["success"], True)  # json says success
        self.assertEqual(len(data["stations"]), 10)  # returns paginated station info
        self.assertTrue(data["total_num_stations"])  # returns number of stations

    def test_get_riders(self):
        """Test for successful GET riders"""
        res = self.client().get("/riders", headers=self.manager_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)  # Good request code
        self.assertEqual(data["success"], True)  # json says success
        self.assertEqual(len(data["riders"]), 10)  # returns paginated rider info
        self.assertTrue(data["total_num_riders"])  # returns number of riders

    def test_get_trips(self):
        """Test for successful GET trips"""
        res = self.client().get("/trips", headers=self.manager_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)  # Good request code
        self.assertEqual(data["success"], True)  # json says success
        self.assertEqual(len(data["trips"]), 10)  # returns paginated trips info
        self.assertTrue(data["total_num_trips"])  # returns number of trips

    def test_404_invalid_page_get_bikes(self):
        """Tests for 404 error in GET bikes"""
        res = self.client().get("/bikes?page=10000", headers=self.manager_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_404_invalid_page_get_stations(self):
        """Tests for 404 error in GET stations"""
        res = self.client().get(
            "/stations?page=10000", headers=self.manager_auth_header
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_404_invalid_page_get_riders(self):
        """Tests for 404 error in GET riders"""
        res = self.client().get("/riders?page=10000", headers=self.manager_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_404_invalid_page_get_trips(self):
        """Tests for 404 error in trips"""
        res = self.client().get("/trips?page=10000", headers=self.manager_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_1_create_bike(self):
        """Tests for successful POST of new bike"""
        res = self.client().post(
            "/bikes", json=self.test_bike, headers=self.manager_auth_header
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["bikes"]), 10)
        self.assertTrue(Bike.query.order_by(Bike.model == "test").all())

    def test_2_edit_bike(self):
        """Tests for seuccessful PATCH of Bike"""
        res = self.client().patch(
            "/bikes/1",
            json={"current_station_id": 10},
            headers=self.manager_auth_header,
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["bike_updated"]["current_station_id"], 10)
        self.assertEqual(data["bike_updated"]["id"], 1)

    def test_3_delete_bike(self):
        """Tests for seuccessful DELETE of Bike"""
        res = self.client().delete("/bikes/16", headers=self.manager_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["total_num_bikes"], 15)
        self.assertEqual(len(data["bikes"]), 10)
        self.assertEqual(data["deleted_bike_id"], 16)

    def test_400_too_many_bikes_at_station(self):
        """Tests for if there are too many bikes at a station"""

        # fill station
        for i in range(Station.query.get(4).capacity):
            self.client().post(
                "/bikes", json=self.test_bike, headers=self.manager_auth_header
            )

        # one additional bike
        res = self.client().post(
            "/bikes", json=self.test_bike, headers=self.manager_auth_header
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad request. Please try again")

    def test_404_station_not_found(self):
        """Tests if station not found in bike creation"""
        res = self.client().post(
            "/bikes",
            json={
                "model": "test",
                "manufactured_at": "2021-01-03",
                "electric": False,
                "current_station_id": 100,
            },
            headers=self.manager_auth_header,
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_422_bad_bike_creation(self):
        """Tests for bad POST request to bikes"""
        res = self.client().post(
            "/bikes", json={"current_station_id": 1}, headers=self.manager_auth_header
        )

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable")

    def test_404_update_bike_fail(self):
        """Tests for bad PATCH requests to bikes"""
        res = self.client().patch(
            "/bikes/100", json={"electric": True}, headers=self.manager_auth_header
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_404_delete_bike_fail(self):
        """Tests for bad DELETE requests to bikes"""
        res = self.client().delete("/bikes/100", headers=self.manager_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_1_create_station(self):
        """Tests for successful POST of new station"""
        res = self.client().post(
            "/stations", json=self.test_station, headers=self.manager_auth_header
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["stations"]), 10)
        self.assertTrue(Station.query.order_by(Station.name == "Test Street").all())

    def test_2_edit_station(self):
        """Tests for seuccessful PATCH of Station"""
        res = self.client().patch(
            "/stations/1", json={"capacity": 50}, headers=self.manager_auth_header
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["station_updated"]["capacity"], 50)
        self.assertEqual(data["station_updated"]["id"], 1)

    def test_3_delete_station(self):
        """Tests for seuccessful DELETE of station"""
        res = self.client().delete("/stations/12", headers=self.manager_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["total_num_stations"], 11)
        self.assertEqual(len(data["stations"]), 10)
        self.assertEqual(data["deleted_station_id"], 12)

    def test_422_bad_station_creation(self):
        """Tests for bad POST request to stations"""
        res = self.client().post(
            "/stations", json={"capacity": 1}, headers=self.manager_auth_header
        )

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable")

    def test_404_update_station_fail(self):
        """Tests for bad PATCH requests to stations"""
        res = self.client().patch(
            "/stations/100", json={"active": "string"}, headers=self.manager_auth_header
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_404_delete_station_fail(self):
        """Tests for bad DELETE requests to stations"""
        res = self.client().delete("/stations/100", headers=self.manager_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_1_create_rider(self):
        """Tests for successful POST of new rider"""
        res = self.client().post(
            "/riders", json=self.test_rider, headers=self.manager_auth_header
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["riders"]), 10)
        self.assertTrue(Rider.query.order_by(Rider.name == "Test").all())

    def test_2_edit_rider(self):
        """Tests for seuccessful PATCH of rider"""
        res = self.client().patch(
            "/riders/1",
            json={"address": "Address Test"},
            headers=self.manager_auth_header,
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["rider_updated"]["address"], "Address Test")
        self.assertEqual(data["rider_updated"]["id"], 1)

    def test_3_delete_rider(self):
        """Tests for seuccessful DELETE of rider"""
        res = self.client().delete("/riders/13", headers=self.manager_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["total_num_riders"], 12)
        self.assertEqual(len(data["riders"]), 10)
        self.assertEqual(data["deleted_rider_id"], 13)

    def test_422_bad_rider_creation(self):
        """Tests for bad POST request to rider"""
        res = self.client().post(
            "/riders", json={"email": 1}, headers=self.manager_auth_header
        )

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable")

    def test_404_update_rider_fail(self):
        """Tests for bad PATCH requests to riders"""
        res = self.client().patch(
            "/riders/100", json={"email": "string"}, headers=self.manager_auth_header
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_404_delete_rider_fail(self):
        """Tests for bad DELETE requests to riders"""
        res = self.client().delete("/riders/100", headers=self.manager_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_1_start_trip(self):
        """Tests for successful start trip POST request to trips"""
        res = self.client().post(
            "/trips",
            json={"rider_id": 5, "bike_id": 5},
            headers=self.manager_auth_header,
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["started_trip"]["bike_id"], 5)

    def test_2_400_bike_already_on_trip(self):
        """Tests for prevention of double taking out a bike"""
        res = self.client().post(
            "/trips",
            json={"rider_id": 5, "bike_id": 5},
            headers=self.manager_auth_header,
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad request. Please try again")

    def test_3_end_trip(self):
        """Tests for successful end of trip"""
        res = self.client().patch(
            "/trips/13",
            json={"destination_station_id": 11},
            headers=self.manager_auth_header,
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["ended_trip"]["id"], 13)

    def test_422_trip_start_fail(self):
        """Tests for bad POST request to start a trip"""
        res = self.client().post(
            "/trips", json={"email": 1}, headers=self.manager_auth_header
        )

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable")

    def test_404_trip_end_fail(self):
        """Tests for bad PATCH request to end a trip"""
        res = self.client().patch(
            "/trips/10000",
            json={"destination_station_id": 9},
            headers=self.manager_auth_header,
        )

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_400_too_many_bikes_at_station_on_trip_end(self):

        # start one additional trip
        self.client().post(
            "/trips",
            json={"bike_id": 1, "rider_id": 1},
            headers=self.manager_auth_header,
        )
        # end trip at filled station
        res = self.client().patch(
            "/trips/14",
            json={"destination_station_id": 4},
            headers=self.manager_auth_header,
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad request. Please try again")

    def test_401_no_authorization_header(self):
        res = self.client().get("/trips")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"]["code"], "authorization_header_missing")

    def test_403_not_permitted_request(self):
        """Rider Role Not allowed to post to stations"""
        res = self.client().post(
            "/stations", json=self.test_station, headers=self.rider_auth_header
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"]["code"], "invalid_claims")

    def test_403_not_permitted_request(self):
        """Rider Role Not allowed to get other rider information"""
        res = self.client().get("/riders", headers=self.rider_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"]["code"], "invalid_claims")


if __name__ == "__main__":
    unittest.main()
