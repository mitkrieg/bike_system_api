# Bike Share System API

A demo API for a bike share system (example: [CitiBike](https://citibikenyc.com/)). Riders can query the API to get information about bikes and stations and create trips. Mangers of the system can add/edit/delete stations, riders, bikes, and trips.

## Running a Local Setup

#### Clone a local copy of this repository

Create a copy of this repository by cloning locally or forking to your own reposiotry and cloning locally

    ```
    $ git clone https://github.com/mitkrieg/bike_system_api
    ```

#### Install Dependencies

1. **Python 3.7**: Install python using the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)
2. **PostgreSQL**: Either download and install from https://www.postgresql.org/download/ or install via homebrew:
    ```
    brew install postgresql
    brew services start postgresql
    ```
3. **Virtual Environment**: Create and activate a new virtual environment

    ```
    $ python3 -m pip install --user virtualenv
    $ python3 -m venv env
    $ source env/bin/activate
    ```

4. **Install Dependencies via PIP**: Install dependenant packages found in [requirements.txt](https://github.com/mitkrieg/bike_system_api/blob/main/requirements.txt) using pip inside of the new virtual environment 
   
   ```
    $ pip install -r requirements.txt
   ```

#### Database Creation

Create a new local postgres database and populate it with test data using the following commands

    ```
    $ dropdb bike_system
    $ createdb bike_system
    $ psql bike_system < db_setup.psql
    ```

#### Run local server

Run the local server using the following code:

    ```
    $ export FLASK_APP=app.py
    $ export FLASK_ENV=development
    $ flask run --reload
    ```

#### Testing local server

To run unit tests first generate jwt tokens from this [login page](https://mk-bike-system.us.auth0.com/authorize?audience=bikes&response_type=token&client_id=NV1dRImnJo0AG8bGAdG8zXQoT4fQ7OMA&redirect_uri=https://127.0.0.1:8080/loginresults). To run all tests successfully, you need both a manager role token and a rider role token. Run the following commands

```
$ export RIDER_TOKEN=<insert your rider token>
$ export MANAGER_TOKEN=<insert your manager token>
$ python3 tests.py
```

## API Reference

### Getting Started

- **Base URL**: Two options:
  - Send requests locally: Set up and to run the server locally via the directions above. Then use the default host url `http://127.0.0.1:5000/`
  - Send requests to deployed version: A version of the API is deployed via heroku is hosted at `https://bike-system-api.herokuapp.com/` 
- Authentication: All requests must be authenticated via a bearer jwt token in the header of the request. Generate tokens via Auth0 at this [login page](https://mk-bike-system.us.auth0.com/authorize?audience=bikes&response_type=token&client_id=NV1dRImnJo0AG8bGAdG8zXQoT4fQ7OMA&redirect_uri=https://127.0.0.1:8080/loginresults). Add the following header to all requests
    ```
    -H 'Authorization: Bearer <INSERT JWT>'
    ```

### Error Handling

The following JSON is returned when errors occur:

```
{
    "success": boolean
    "error":int
    "message":string
}
```

Possible types of errors:

- 400: Bad Request
- 401: Missing or malformed Authorization header
- 403: Not permitted/credentials not valid
- 404: Resource not found
- 422: Not Processable
- 500: Internal Service Error

### Endpoints

#### GET /bikes

- Returns a paginated list of bike objects in the system and total number of bikes
- Max page legnth is 10 bikes, and a specfic page can be selected via an argument
- Requires permission `get:bikes` available in JWT to Rider and Manage roles
- Sample Request: `curl https://bike-system-api.herokuapp.com/bikes?page=2 -H 'Authorization: Bearer <JWT>' -H 'Content-Type: application/json'`
- Sample response:

```json
{
    "bikes": [
        {
            "current_station_id": 1,
            "electric": true,
            "id": 11,
            "model": "3a",
            "needs_maintenance": false,
            "num_trips": 1
        },
        {
            "current_station_id": 2,
            "electric": false,
            "id": 12,
            "model": "3a",
            "needs_maintenance": false,
            "num_trips": 0
        },
        {
            "current_station_id": 2,
            "electric": true,
            "id": 13,
            "model": "3a",
            "needs_maintenance": false,
            "num_trips": 0
        },
        {
            "current_station_id": 3,
            "electric": false,
            "id": 14,
            "model": "2g",
            "needs_maintenance": false,
            "num_trips": 0
        },
        {
            "current_station_id": 6,
            "electric": false,
            "id": 15,
            "model": "21c",
            "needs_maintenance": false,
            "num_trips": 1
        }
    ],
    "page": 2,
    "success": true,
    "total_num_bikes": 15
}
```

#### POST /bikes

- Creates a new bike in database, new bike id and returns a paginated list of bike objects in the system and total number of bikes
- Max page legnth is 10 bikes, and a specfic page can be selected via an argument
- Requires permission `edit:bikes` which isavailable in JWT to only Manager roles
- Requires at least the model, manufacturing date, electric, and current station id attributes of bike object passed in through json
- Sample Request: 
    ```
    curl https://bike-system-api.herokuapp.com/bikes?page=2 -X POST -H 'Authorization: Bearer <JWT>' -H 'Content-Type: application/json' -d '{ "model":"92b","manufactured_at":"2019-03-04","electric":true,"current_station_id":5}'
    ```
- Sample response:

    ```json
    {
        "bikes": [
            {
                "current_station_id": 1,
                "electric": true,
                "id": 1,
                "model": "3a",
                "needs_maintenance": false,
                "num_trips": 3
            },
            {
                "current_station_id": 2,
                "electric": false,
                "id": 2,
                "model": "3a",
                "needs_maintenance": false,
                "num_trips": 4
            },
            {
                "current_station_id": 2,
                "electric": true,
                "id": 3,
                "model": "3a",
                "needs_maintenance": false,
                "num_trips": 1
            },
            {
                "current_station_id": 3,
                "electric": false,
                "id": 4,
                "model": "2g",
                "needs_maintenance": false,
                "num_trips": 0
            },
            {
                "current_station_id": 6,
                "electric": false,
                "id": 5,
                "model": "21c",
                "needs_maintenance": false,
                "num_trips": 0
            },
            {
                "current_station_id": 1,
                "electric": true,
                "id": 6,
                "model": "3a",
                "needs_maintenance": false,
                "num_trips": 1
            },
            {
                "current_station_id": 2,
                "electric": false,
                "id": 7,
                "model": "3a",
                "needs_maintenance": false,
                "num_trips": 0
            },
            {
                "current_station_id": 2,
                "electric": true,
                "id": 8,
                "model": "3a",
                "needs_maintenance": false,
                "num_trips": 0
            },
            {
                "current_station_id": 3,
                "electric": false,
                "id": 9,
                "model": "2g",
                "needs_maintenance": false,
                "num_trips": 0
            },
            {
                "current_station_id": 6,
                "electric": false,
                "id": 10,
                "model": "21c",
                "needs_maintenance": false,
                "num_trips": 1
            }
        ],
        "created_bike_id": 16,
        "page": 1,
        "success": true,
        "total_num_bikes": 16
    }
    ```

#### PATCH /bikes/<bike_id>

- Edits an existing bike in database and returns information about the bike edited
- Will only update attributes passed in through the JSON
- Requires permission `edit:bikes` which is available in JWT to only Manager roles
- Sample Request: 
    ```
    curl https://bike-system-api.herokuapp.com/bikes/1 -X PATCH -H 'Authorization: Bearer <JWT>' -H 'Content-Type: application/json' -d '{ "model":"92b"}'
    ```
- Sample response:

    ```
    {
        "bike_updated": {
            "current_station_id": 1,
            "electric": true,
            "id": 1,
            "model": "92b",
            "needs_maintenance": false,
            "num_trips": 3
        },
        "success": true
    }
    ```

#### DELETE /bikes/<bike_id>

- Deletes an existing bike in database and returns the deleted bike id, a paginated list of remeaning bike objects in the system and total number of remaining bikes
- Max page legnth is 10 bikes, and a specfic page can be selected via an argument
- Requires permission `delete:bikes` which is available in JWT to only Manager roles
- Sample Request: 
  
    ```
    curl https://bike-system-api.herokuapp.com/bikes/1 -X DELETE -H 'Authorization: Bearer <JWT>' -H 'Content-Type: application/json'
    ```

- Sample Response:

    ```json
    {
        "bikes": [
            {
                "current_station_id": 2,
                "electric": false,
                "id": 2,
                "model": "3a",
                "needs_maintenance": false,
                "num_trips": 4
            },
            {
                "current_station_id": 2,
                "electric": true,
                "id": 3,
                "model": "3a",
                "needs_maintenance": false,
                "num_trips": 1
            },
            {
                "current_station_id": 6,
                "electric": false,
                "id": 10,
                "model": "21c",
                "needs_maintenance": false,
                "num_trips": 1
            },
            {
                "current_station_id": 6,
                "electric": false,
                "id": 15,
                "model": "21c",
                "needs_maintenance": false,
                "num_trips": 1
            },
            {
                "current_station_id": 1,
                "electric": true,
                "id": 11,
                "model": "3a",
                "needs_maintenance": false,
                "num_trips": 1
            },
            {
                "current_station_id": 1,
                "electric": true,
                "id": 6,
                "model": "3a",
                "needs_maintenance": false,
                "num_trips": 1
            },
            {
                "current_station_id": 2,
                "electric": false,
                "id": 12,
                "model": "3a",
                "needs_maintenance": false,
                "num_trips": 0
            },
            {
                "current_station_id": 2,
                "electric": true,
                "id": 13,
                "model": "3a",
                "needs_maintenance": false,
                "num_trips": 0
            },
            {
                "current_station_id": 6,
                "electric": false,
                "id": 5,
                "model": "21c",
                "needs_maintenance": false,
                "num_trips": 0
            },
            {
                "current_station_id": 2,
                "electric": true,
                "id": 8,
                "model": "3a",
                "needs_maintenance": false,
                "num_trips": 0
            }
        ],
        "deleted_bike_id": 1,
        "page": 1,
        "success": true,
        "total_num_bikes": 14
    }

    ```

#### GET /stations

- Returns a paginated list of station objects in the system and total number of stations
- Max page legnth is 10 stations, and a specfic page can be selected via an argument
- Requires permission `get:stations` available in JWT to Rider and Manager roles
- Sample Request: `curl https://bike-system-api.herokuapp.com/stations?page=2 -H 'Authorization: Bearer <JWT>' -H 'Content-Type: application/json'`
- Sample response:

    ```json
    {
        "page": 2,
        "stations": [
            {
                "capacity": 24,
                "id": 11,
                "latitude": 12.5324,
                "longitude": -83.4234,
                "name": "Grand Central Station",
                "num_bikes": 0
            },
            {
                "capacity": 13,
                "id": 12,
                "latitude": 32.525,
                "longitude": 44.5345,
                "name": "City Hall",
                "num_bikes": 0
            }
        ],
        "success": true,
        "total_num_stations": 12
    }
    ```

#### GET /stations/<station_id>/bikes

- Returns a list of bikes at a given station and information about the selected station
- requires permission `get:stations` available in JWT to Rider and Manager roles
- Sample Request: `curl https://bike-system-api.herokuapp.com/stations/1/bikes -H 'Authorization: Bearer <JWT>' -H 'Content-Type: application/json'`
- Sample response:
  
    ```json
        {
        "bikes": [
            {
                "current_station_id": 1,
                "electric": true,
                "id": 11,
                "model": "3a",
                "needs_maintenance": false,
                "num_trips": 1
            },
            {
                "current_station_id": 1,
                "electric": true,
                "id": 6,
                "model": "3a",
                "needs_maintenance": false,
                "num_trips": 1
            }
        ],
        "num_bikes": 2,
        "station_info": {
            "capacity": 50,
            "id": 1,
            "latitude": 42.4324,
            "longitude": -87.4234,
            "name": "Broadway",
            "num_bikes": 2
        },
        "success": true
    }
    ```

#### POST /stations

- Creates a new station in database, new station id and returns a paginated list of station objects in the system and total number of stations
- Max page legnth is 10 stations, and a specfic page can be selected via an argument
- Requires permission `edit:stations` which isavailable in JWT to only Manager roles
- Requires at least name, capacity, longitude and latitude attributes of stations passed in through json
- Sample Request: 
    ```
    curl https://bike-system-api.herokuapp.com/stations?page=1 -X POST -H 'Authorization: Bearer <JWT>' -H 'Content-Type: application/json' -d '{"name":"123 Sesame Street", "capacity":13, "longitude":-45.6777, "latitude": 42.3355 }'
    ```
- Sample response:
   ```json
    {
        "created_station_id": 15,
        "page": 1,
        "stations": [
            {
                "capacity": 50,
                "id": 1,
                "latitude": 42.4324,
                "longitude": -87.4234,
                "name": "Broadway",
                "num_bikes": 2
            },
            {
                "capacity": 15,
                "id": 2,
                "latitude": 43.525,
                "longitude": 44.5345,
                "name": "Amsterdam",
                "num_bikes": 6
            },
            {
                "capacity": 20,
                "id": 3,
                "latitude": 42.5324,
                "longitude": -83.4234,
                "name": "West End",
                "num_bikes": 3
            },
            {
                "capacity": 5,
                "id": 4,
                "latitude": 44.525,
                "longitude": 44.5345,
                "name": "Columbus",
                "num_bikes": 5
            },
            {
                "capacity": 24,
                "id": 5,
                "latitude": 12.5324,
                "longitude": -83.4234,
                "name": "14th Street",
                "num_bikes": 0
            },
            {
                "capacity": 13,
                "id": 6,
                "latitude": 32.525,
                "longitude": 44.5345,
                "name": "7th Ave",
                "num_bikes": 2
            },
            {
                "capacity": 20,
                "id": 7,
                "latitude": 42.4324,
                "longitude": -87.4234,
                "name": "Route 66",
                "num_bikes": 0
            },
            {
                "capacity": 15,
                "id": 8,
                "latitude": 43.525,
                "longitude": 44.5345,
                "name": "Wall St",
                "num_bikes": 0
            },
            {
                "capacity": 20,
                "id": 9,
                "latitude": 42.5324,
                "longitude": -83.4234,
                "name": "East End",
                "num_bikes": 0
            },
            {
                "capacity": 10,
                "id": 10,
                "latitude": 44.525,
                "longitude": 44.5345,
                "name": "Ferry Terminal",
                "num_bikes": 1
            }
        ],
        "success": true,
        "total_num_stations": 12
    }
    ```


#### PATCH /stations/<stations_id>

- Edits an existing station in database and returns information about the station edited
- Requires permission `edit:stations` which is available in JWT to only Manager roles
- Will only update attributes passed in through the JSON
- Sample Request: 
    ```
    curl https://bike-system-api.herokuapp.com/stations/1 -X PATCH -H 'Authorization: Bearer <JWT>' -H 'Content-Type: application/json' -d '{ "name":"808 Wysteria Lane"}'
    ```
- Sample response:

    ```json
        {
        "station_updated": {
            "capacity": 50,
            "id": 1,
            "latitude": 42.4324,
            "longitude": -87.4234,
            "name": "808 Wysteria Lane",
            "num_bikes": 2
        },
        "success": true
    }
    ```

#### DELETE /stations/<station_id>

- Deletes an existing station in database and returns the deleted station id, a paginated list of remeaning station objects in the system and total number of remaining stations
- Max page legnth is 10 stations, and a specfic page can be selected via an argument
- Requires permission `delete:stations` which is available in JWT to only Manager roles
- Sample Request: 
  
    ```
    curl https://bike-system-api.herokuapp.com/stations/1?page=1 -X DELETE -H 'Authorization: Bearer <JWT>' -H 'Content-Type: application/json'
    ```

- Sample Response:

    ```json
    {
        "deleted_station_id": 3,
        "page":1,
        "stations": [
            {
                "capacity": 10,
                "id": 10,
                "latitude": 44.525,
                "longitude": 44.5345,
                "name": "Ferry Terminal",
                "num_bikes": 1
            },
            {
                "capacity": 15,
                "id": 2,
                "latitude": 43.525,
                "longitude": 44.5345,
                "name": "Amsterdam",
                "num_bikes": 6
            },
            {
                "capacity": 13,
                "id": 6,
                "latitude": 32.525,
                "longitude": 44.5345,
                "name": "7th Ave",
                "num_bikes": 2
            },
            {
                "capacity": 50,
                "id": 1,
                "latitude": 42.4324,
                "longitude": -87.4234,
                "name": "808 Wysteria Lane",
                "num_bikes": 2
            },
            {
                "capacity": 24,
                "id": 11,
                "latitude": 12.5324,
                "longitude": -83.4234,
                "name": "Grand Central Station",
                "num_bikes": 1
            },
            {
                "capacity": 5,
                "id": 4,
                "latitude": 44.525,
                "longitude": 44.5345,
                "name": "Columbus",
                "num_bikes": 5
            },
            {
                "capacity": 13,
                "id": 15,
                "latitude": 42.3355,
                "longitude": -45.6777,
                "name": "123 Sesame Street",
                "num_bikes": 0
            },
            {
                "capacity": 24,
                "id": 5,
                "latitude": 12.5324,
                "longitude": -83.4234,
                "name": "14th Street",
                "num_bikes": 0
            },
            {
                "capacity": 15,
                "id": 8,
                "latitude": 43.525,
                "longitude": 44.5345,
                "name": "Wall St",
                "num_bikes": 0
            },
            {
                "capacity": 20,
                "id": 9,
                "latitude": 42.5324,
                "longitude": -83.4234,
                "name": "East End",
                "num_bikes": 0
            }
        ],
        "success": true,
        "total_num_stations": 11
    }
    ```

#### GET /riders

- Returns a paginated list of rider objects in the system and total number of riders
- Max page legnth is 10 riders, and a specfic page can be selected via an argument
- Requires permission `get:riders` available in JWT only to Manager roles
- Sample Request: `curl https://bike-system-api.herokuapp.com/riders?page=2 -H 'Authorization: Bearer <JWT>' -H 'Content-Type: application/json'`
- Sample response:

    ```json
        {
        "page": 2,
        "riders": [
            {
                "address": "Albany",
                "email": "Lisa@gmail.com",
                "id": 12,
                "membership": false,
                "name": "Lisa",
                "num_trips": 0
            },
            {
                "address": "123 Seasame Street",
                "email": "test@abc.com",
                "id": 13,
                "membership": true,
                "name": "Test",
                "num_trips": 0
            }
        ],
        "success": true,
        "total_num_riders": 12
    }
    ```

#### POST /riders

- Creates a new rider in database, new rider id and returns a paginated list of bike objects in the system and total number of riders
- Max page legnth is 10 riders, and a specfic page can be selected via an argument
- Requires permission `edit:riders` which isavailable in JWT to only Manager roles
- Requires at least name, email, address, and membership attributes of rider objects passed in through JSON
- Sample Request: 
    ```
    curl https://bike-system-api.herokuapp.com/riders?page=2 -X POST -H 'Authorization: Bearer <JWT>' -H 'Content-Type: application/json' -d '{ "name":"George Washington","email":"person@domain.com","address":"123 Cherry Lane", "membership":false}'
    ```
- Sample response:

    ```json
        {
        "created_rider_id": 15,
        "page": 2,
        "riders": [
            {
                "address": "Albany",
                "email": "Lisa@gmail.com",
                "id": 12,
                "membership": false,
                "name": "Lisa",
                "num_trips": 0
            },
            {
                "address": "123 Seasame Street",
                "email": "test@abc.com",
                "id": 13,
                "membership": true,
                "name": "Test",
                "num_trips": 0
            },
            {
                "address": "123 Cherry Lane",
                "email": "person@domain.com",
                "id": 15,
                "membership": false,
                "name": "George Washington",
                "num_trips": 0
            }
        ],
        "success": true,
        "total_num_riders": 13
    }
    ```

#### PATCH /riders/<rider_id>

- Edits an existing rider in database and returns information about the bike edited
- Will only update attributes passed in through the JSON
- Requires permission `edit:riders` which is available in JWT to only Manager roles
- Sample Request: 
    ```
    curl https://bike-system-api.herokuapp.com/riders/5 -X PATCH -H 'Authorization: Bearer <JWT>' -H 'Content-Type: application/json' -d '{ "name":"John Smith"}'
    ```
- Sample response:

    ```json
    {
        "rider_updated": {
            "address": "Hogwarts School of Witchcraft and Wizardry",
            "email": "hpotter@hogwarts.com",
            "id": 5,
            "membership": false,
            "name": "Harry Potter",
            "num_trips": 2
        },
        "success": true
    }
    ```

#### DELETE /riders/<bike_id>

- Deletes an existing riders in database and returns the deleted rider id, a paginated list of remeaning rider objects in the system and total number of remaining riders
- Max page legnth is 10 riders, and a specfic page can be selected via an argument
- Requires permission `delete:riders` which is available in JWT to only Manager roles
- Sample Request: 
  
    ```
    curl https://bike-system-api.herokuapp.com/riders/1?page=1 -X DELETE -H 'Authorization: Bearer <JWT>' -H 'Content-Type: application/json'
    ```

- Sample Response:

    ```json
    {
        "deleted_rider_id": 1,
        "riders": [
            {
                "address": "Uniondale",
                "email": "livi@test.com",
                "id": 2,
                "membership": false,
                "name": "Olivia",
                "num_trips": 4
            },
            {
                "address": "New York",
                "email": "jane@gmail.com",
                "id": 4,
                "membership": true,
                "name": "Jane",
                "num_trips": 1
            },
            {
                "address": "Chicago",
                "email": "Doug@gmail.com",
                "id": 10,
                "membership": true,
                "name": "Doug",
                "num_trips": 1
            },
            {
                "address": "Los Angeles",
                "email": "Sally@gmail.com",
                "id": 5,
                "membership": false,
                "name": "Sally",
                "num_trips": 2
            },
            {
                "address": "Florida",
                "email": "John@gmail.com",
                "id": 9,
                "membership": false,
                "name": "John",
                "num_trips": 1
            },
            {
                "address": "Long Island",
                "email": "Michael@gmail.com",
                "id": 8,
                "membership": false,
                "name": "Michael",
                "num_trips": 1
            },
            {
                "address": "Detroit",
                "email": "Ethan@gmail.com",
                "id": 11,
                "membership": false,
                "name": "Ethan",
                "num_trips": 0
            },
            {
                "address": "Albany",
                "email": "Lisa@gmail.com",
                "id": 12,
                "membership": false,
                "name": "Lisa",
                "num_trips": 0
            },
            {
                "address": "123 Seasame Street",
                "email": "test@abc.com",
                "id": 13,
                "membership": true,
                "name": "Test",
                "num_trips": 0
            },
            {
                "address": "Vermont",
                "email": "Sue@gmail.com",
                "id": 6,
                "membership": false,
                "name": "Sue",
                "num_trips": 0
            }
        ],
        "success": true,
        "total_num_riders": 12
    }
    ```


#### GET /riders/<rider_id>/trips

- Returns a list of trips for a given rider and information about the selected rider
- requires permission `get:riders` available only to Manager roles
- Sample Request: `curl https://bike-system-api.herokuapp.com/riders/5/trips -H 'Authorization: Bearer <JWT>' -H 'Content-Type: application/json'`
- Sample response:
  
    ```json
        {
        "num_trips": 2,
        "rider_info": {
            "address": "Hogwarts School of Witchcraft and Wizardry",
            "email": "hpotter@hogwarts.com",
            "id": 5,
            "membership": false,
            "name": "Harry Potter",
            "num_trips": 2
        },
        "success": true,
        "trips": [
            {
                "bike_id": 2,
                "destination_station": "Amsterdam",
                "destination_station_id": 2,
                "end_time": "Sun, 02 Jan 2022 18:00:23 GMT",
                "id": 8,
                "origination_station": "808 Wysteria Lane",
                "origination_station_id": 1,
                "rider": "Harry Potter",
                "rider_id": 5,
                "start_time": "Sun, 02 Jan 2022 17:23:43 GMT"
            },
            {
                "bike_id": 5,
                "destination_station": "Grand Central Station",
                "destination_station_id": 11,
                "end_time": "Sat, 29 Jan 2022 19:24:03 GMT",
                "id": 13,
                "origination_station": "7th Ave",
                "origination_station_id": 6,
                "rider": "Harry Potter",
                "rider_id": 5,
                "start_time": "Sat, 29 Jan 2022 19:24:02 GMT"
            }
        ]
    }
    ```

#### GET /trips

- Returns a paginated list of trip objects in the system and total number of trips
- Max page legnth is 10 trips, and a specfic page can be selected via an argument
- Requires permission `get:trips` available in JWT only to Manager roles
- Sample Request: `curl https://bike-system-api.herokuapp.com/trips?page=1 -H 'Authorization: Bearer <JWT>' -H 'Content-Type: application/json'`
- Sample response:

    ```json
        {
        "page": 1,
        "success": true,
        "total_num_trips": 10,
        "trips": [
            {
                "bike_id": 1,
                "destination_station": "808 Wysteria Lane",
                "destination_station_id": 1,
                "end_time": "Sat, 01 Jan 2022 18:00:01 GMT",
                "id": 1,
                "origination_station": "Amsterdam",
                "origination_station_id": 2,
                "rider": "Olivia",
                "rider_id": 2,
                "start_time": "Sat, 01 Jan 2022 17:32:23 GMT"
            },
            {
                "bike_id": 1,
                "destination_station": "808 Wysteria Lane",
                "destination_station_id": 1,
                "end_time": "Sat, 01 Jan 2022 18:00:01 GMT",
                "id": 3,
                "origination_station": "Amsterdam",
                "origination_station_id": 2,
                "rider": "Olivia",
                "rider_id": 2,
                "start_time": "Sat, 01 Jan 2022 17:32:23 GMT"
            },
            {
                "bike_id": 3,
                "destination_station": "Amsterdam",
                "destination_station_id": 2,
                "end_time": "Mon, 02 May 2022 18:00:23 GMT",
                "id": 4,
                "origination_station": "808 Wysteria Lane",
                "origination_station_id": 1,
                "rider": "Jane",
                "rider_id": 4,
                "start_time": "Mon, 02 May 2022 17:23:43 GMT"
            },
            {
                "bike_id": 10,
                "destination_station": "7th Ave",
                "destination_station_id": 6,
                "end_time": "Wed, 05 Jan 2022 18:00:01 GMT",
                "id": 5,
                "origination_station": "Amsterdam",
                "origination_station_id": 2,
                "rider": "Doug",
                "rider_id": 10,
                "start_time": "Wed, 05 Jan 2022 17:32:23 GMT"
            },
            {
                "bike_id": 11,
                "destination_station": "808 Wysteria Lane",
                "destination_station_id": 1,
                "end_time": "Sat, 01 Jan 2022 18:00:01 GMT",
                "id": 7,
                "origination_station": "Route 66",
                "origination_station_id": 7,
                "rider": "Olivia",
                "rider_id": 2,
                "start_time": "Sat, 01 Jan 2022 17:32:23 GMT"
            },
            {
                "bike_id": 2,
                "destination_station": "Amsterdam",
                "destination_station_id": 2,
                "end_time": "Sun, 02 Jan 2022 18:00:23 GMT",
                "id": 8,
                "origination_station": "808 Wysteria Lane",
                "origination_station_id": 1,
                "rider": "Harry Potter",
                "rider_id": 5,
                "start_time": "Sun, 02 Jan 2022 17:23:43 GMT"
            },
            {
                "bike_id": 6,
                "destination_station": "808 Wysteria Lane",
                "destination_station_id": 1,
                "end_time": "Sat, 01 Jan 2022 18:00:01 GMT",
                "id": 9,
                "origination_station": "Amsterdam",
                "origination_station_id": 2,
                "rider": "John",
                "rider_id": 9,
                "start_time": "Sat, 01 Jan 2022 17:32:23 GMT"
            },
            {
                "bike_id": 2,
                "destination_station": "Amsterdam",
                "destination_station_id": 2,
                "end_time": "Sun, 02 Jan 2022 18:00:23 GMT",
                "id": 10,
                "origination_station": "808 Wysteria Lane",
                "origination_station_id": 1,
                "rider": "Michael",
                "rider_id": 8,
                "start_time": "Sun, 02 Jan 2022 17:23:43 GMT"
            },
            {
                "bike_id": 1,
                "destination_station": "808 Wysteria Lane",
                "destination_station_id": 1,
                "end_time": "Sat, 01 Jan 2022 18:00:01 GMT",
                "id": 11,
                "origination_station": "Amsterdam",
                "origination_station_id": 2,
                "rider": "Olivia",
                "rider_id": 2,
                "start_time": "Sat, 01 Jan 2022 17:32:23 GMT"
            },
            {
                "bike_id": 5,
                "destination_station": "Grand Central Station",
                "destination_station_id": 11,
                "end_time": "Sat, 29 Jan 2022 19:24:03 GMT",
                "id": 13,
                "origination_station": "7th Ave",
                "origination_station_id": 6,
                "rider": "Harry Potter",
                "rider_id": 5,
                "start_time": "Sat, 29 Jan 2022 19:24:02 GMT"
            }
        ]
    }
    ```

#### POST /trips

- Begins a trip and saves to database. Returns information about the started trip
- Requires permission `start:trips` available in JWT to Rider and Manager roles
- Sample Request: 
    
    ```
    curl https://bike-system-api.herokuapp.com/trips -X POST -H 'Authorization: Bearer <JWT>' -H 'Content-Type: application/json' -d '{ "bike_id":8,"rider_id":11}'
    ```

- Sample response:

    ```json
    {
        "started_trip": {
            "bike_id": 11,
            "origination_station_id": 1,
            "rider_id": 8,
            "start_time": "Sat, 29 Jan 2022 21:58:39 GMT",
            "trip_id": 15
        },
        "success": true
    }
    ```

#### PATCH /trips/<trip_id>

- Begins a trip and saves to database. Returns information about the started trip
- Requires a destination station passed in through json
- Requires permission `start:trips` available in JWT to Rider and Manager roles
- Sample Request: 
    
    ```
    curl https://bike-system-api.herokuapp.com/trips/15 -X PATCH -H 'Authorization: Bearer <JWT>' -H 'Content-Type: application/json' -d '{"destination_station_id": 5}'
    ```

- Sample response:

    ```json
    {
        "ended_trip": {
            "bike_id": 11,
            "destination_station": "14th Street",
            "destination_station_id": 5,
            "end_time": "Sat, 29 Jan 2022 22:07:44 GMT",
            "id": 15,
            "origination_station": "Broadway",
            "origination_station_id": 1,
            "rider": "Michael",
            "rider_id": 8,
            "start_time": "Sat, 29 Jan 2022 21:58:39 GMT"
        },
        "success": true
    }
    ```

## Deployment

App deployed through heroku at http://bike-system-api.herokuapp.com. Base alone returns 404 error. Must use paths and methods above in the API reference.

## In this repository

```
├── migrations          <- directory containing alembic migrations of sqlalchemy database modes
│   ├── versions        <- directory containing alembic version files
│   ├── README          <- Database info
│   ├── alembic.ini     <- file to initialize alembic
│   ├── env.py          <- standard file to configure alembic
|   └── script.py.mako  <- mako to generate Doc script at the top of each version.py
├── .gitignore          <- git ignote
├── Procfile            <- Procfile for heroku deployment
├── README.md           <- API Reference and Installation instructions (The document you are reading)
├── app.py              <- Py script defining endpoints in api
├── auth.py             <- py script to generate @requires_auth decorator used to ensure authorization in requests in app.py
├── db_setup.psql       <- SQL code to quickly populate database with fake data
├── maange.py           <- Manges alemic migrations in heroku
├── models.py           <- Py file containing SQLAlchemy database models
├── requirement.txt     <- Dependencies required for local installation
├── runtime.txt         <- Python runtime for heroku deployment
├── setup.sh            <- set up commands
└── tests.py            <- py file containing unit tests for api
```

## Authors

Mitchell Krieger
