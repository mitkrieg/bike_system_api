import os
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Float, DateTime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

DATABASE_NAME = os.getenv("DB_NAME", "bike_system")
DATABASE_USER = os.getenv("DB_USER", "postgres")
DATABASE_PASSWORD = os.getenv("DB_PASS", "postgres")
DATABASE_HOST = os.getenv("DB_HOST", "localhost:5432")
DATABASE_PATH = (
    f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"
)

db = SQLAlchemy()

# Set up flask application and SQL Alchemy


def setup_db(app, databasepath=DATABASE_PATH):
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_PATH
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    # db.create_all()
    migrate = Migrate(app, db)


# Bikes


class Bike(db.Model):
    __tablename__ = "bikes"

    id = Column(Integer, primary_key=True)
    model = Column(String, nullable=False)
    manufactured_at = Column(DateTime, nullable=False)
    electric = Column(Boolean, nullable=False)
    needs_maintenance = Column(Boolean, default=False)
    current_station_id = Column(Integer, ForeignKey("stations.id"))
    trips = db.relationship("Trip", backref="bikes", lazy="joined")

    def __init__(self, model, electric, manufactured_at, current_station_id):
        self.model = model
        self.electric = electric
        self.manufactured_at = manufactured_at
        self.current_station_id = current_station_id

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            "id": self.id,
            "model": self.model,
            "electric": self.electric,
            "needs_maintenance": self.needs_maintenance,
            "current_station_id": self.current_station_id,
            "num_trips": len(self.trips),
        }


class Station(db.Model):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    active = Column(Boolean, default=True)
    bikes = db.relationship("Bike", backref="stations", lazy="joined")

    def __init__(self, name, capacity, latitude, longitude):
        self.name = name
        self.capacity = capacity
        self.latitude = latitude
        self.longitude = longitude

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            "id": self.id,
            "name": self.name,
            "capacity": self.capacity,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "num_bikes": len(self.bikes),
        }


class Rider(db.Model):
    __tablename__ = "riders"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    address = Column(String, nullable=False)
    membership = Column(Boolean, nullable=False)
    trips = db.relationship(
        "Trip", backref="riders", lazy="joined", cascade="all, delete"
    )

    def __init__(self, name, email, address, membership):
        self.name = name
        self.email = email
        self.address = address
        self.membership = membership

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "address": self.address,
            "membership": self.membership,
            "num_trips": len(self.trips),
        }


class Trip(db.Model):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True)
    origination_station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)
    destination_station_id = Column(Integer, ForeignKey("stations.id"))
    bike_id = Column(Integer, ForeignKey("bikes.id"))
    rider_id = Column(Integer, ForeignKey("riders.id"))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)

    def __init__(
        self,
        rider_id,
        origination_station_id,
        bike_id,
        start_time,
    ):
        self.rider_id = rider_id
        self.origination_station_id = origination_station_id
        self.bike_id = bike_id
        self.start_time = start_time
        self.destination_station_id = None
        self.end_time = None

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        rider = Rider.query.get(self.rider_id)
        orgi_station = Station.query.get(self.origination_station_id)

        # return if trip has not ended
        if self.destination_station_id is not None:
            dest_station = Station.query.get(self.destination_station_id)
            return {
                "id": self.id,
                "rider_id": self.rider_id,
                "rider": rider.name,
                "origination_station_id": self.origination_station_id,
                "origination_station": orgi_station.name,
                "destination_station_id": self.destination_station_id,
                "destination_station": dest_station.name,
                "bike_id": self.bike_id,
                "start_time": self.start_time,
                "end_time": self.end_time,
            }
        # return if ended
        else:
            return {
                "id": self.id,
                "rider_id": self.rider_id,
                "rider": rider.name,
                "origination_station_id": self.origination_station_id,
                "origination_station": orgi_station.name,
                "destination_station_id": self.destination_station_id,
                "destination_station": None,
                "bike_id": self.bike_id,
                "start_time": self.start_time,
                "end_time": self.end_time,
            }
