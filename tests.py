import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from api import create_app
from models import setup_db, Station, Bike, Trip, Rider, DATABASE_PATH


class BikeSystemTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client

        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.create_all()

    def tear_down(self):
        pass

    def test_get_bikes(self):
        """Test for successful GET bikes endpoint"""
        res = self.client().get("/bikes")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)  # Good request code
        self.assertEqual(data["success"], True)  # json says success
        self.assertEqual(len(data["bikes"]), 10)  # returns paginated bike info
        self.assertTrue(data["total_num_bikes"])  # returns number of bikes

    def test_get_stations(self):
        """Test for successful GET bikes stations"""
        res = self.client().get("/stations")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)  # Good request code
        self.assertEqual(data["success"], True)  # json says success
        self.assertEqual(len(data["stations"]), 10)  # returns paginated station info
        self.assertTrue(data["total_num_stations"])  # returns number of stations

    def test_get_riders(self):
        """Test for successful GET bikes riders"""
        res = self.client().get("/riders")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)  # Good request code
        self.assertEqual(data["success"], True)  # json says success
        self.assertEqual(len(data["riders"]), 10)  # returns paginated rider info
        self.assertTrue(data["total_num_riders"])  # returns number of riders

    def test_get_trips(self):
        """Test for successful GET bikes trips"""
        res = self.client().get("/trips")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)  # Good request code
        self.assertEqual(data["success"], True)  # json says success
        self.assertEqual(len(data["trips"]), 10)  # returns paginated trips info
        self.assertTrue(data["total_num_trips"])  # returns number of trips


if __name__ == "__main__":
    unittest.main()
