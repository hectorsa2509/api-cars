
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flasgger import Swagger
from flask_cors import CORS

import os


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
swagger = Swagger(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'cars.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    current_location = db.Column(db.String(3),nullable=False)
    fuel_consumption = db.Column(db.Integer, nullable=False)
    distance = db.Column(db.Float, nullable=False)
    fuel_consumed = db.Column(db.Integer, nullable=False)
    last_location = db.Column(db.Integer, nullable=True)

    def __init__(self, current_location, fuel_consumption, distance, fuel_consumed,last_location):
        self.current_location = current_location
        self.fuel_consumption = fuel_consumption
        self.distance = distance
        self.fuel_consumed = fuel_consumed
        self.last_location = last_location


class CarSchema(ma.Schema):
    class Meta:
        fields = ('id', 'current_location', 'fuel_consumption',
                  'distance', 'fuel_consumed','last_location')


car_schema = CarSchema()
cars_schema = CarSchema(many=True)

#Define locations
locations = ['A','B','C']

#Define locations rules
rules_location = {
    'AA': 0,
    'AB': 1,
    'BA': 1,
    'AC': 2,
    'CA': 2,
    'BB': 0,
    'BC': 4,
    'CB': 4,
    'CC': 0
}


@app.route("/api/car", methods=["POST"])
def add_car():
    """Example endpoint returning a car stored.
    ---
    parameters:
      - name: location
        in: body
        type: string

    definitions:
      Car:
        type: object
        properties:
          current_location:
            type: string
            description:  Store current location
          fuel_consumption:
            type: integer 
            description: Default value 10 is not necessary to send in this request due to you initiate a Car
          distance:
            type: integer 
            description: Default value 0 is not necessary to send in this request due to you initiate a Car
          fuel_consumed:
            type: integer 
            description: Default value 0 is not necessary to send in this request due to you initiate a Car,this value will change as you change location
          last_location:
            type: string 
            description: Default value null is not necessary to send in this request due to you initiate a Car,this value will change as you change location
            
    responses:
      200:
        description: store data
      409:
        description: Location not exist

    """
    current_location = request.json['location']
    fuel_consumption = 10
    distance = 0
    fuel_consumed = 0
    last_location=None

    if current_location.upper() not in locations:
        return "Location not exist", 409
    new_car = Car(current_location, fuel_consumption, distance, fuel_consumed,last_location)

    db.session.add(new_car)
    db.session.commit()

    guide = Car.query.get(new_car.id)

    return car_schema.jsonify(guide)


@app.route("/api/car", methods=["GET"])
def get_cars():
    """Example endpoint return a cars.
    ---
    responses:
      200:
        description: get one car

    """
    all_guides = Car.query.all()
    result = cars_schema.dump(all_guides)
    return jsonify(result)

# Endpoint for querying a single car


@app.route("/api/car/<id>", methods=["GET"])
def get_car(id):
    """Example endpoint return a one.
    ---
    parameters:
        - name: id
          in: query
          type: integer
    responses:
      200:
        description: get all data

    """
    guide = Car.query.get(id)
    return car_schema.jsonify(guide)


# Endpoint for updating a location for a car
@app.route("/api/car/location/<id>", methods=["PATCH"])
def car_update_location(id):
    """Example endpoint update location.
    ---
    responses:
      200:
        description: updated

    """
    car = Car.query.get(id)
    if request.json['location']:
        if car.current_location == request.json['location']:
            return "Same location", 409
    
        if car.fuel_consumption > 0:
            concat_location = car.current_location + request.json['location']

            if concat_location.upper() in rules_location.keys():
                car.distance +=  rules_location[concat_location.upper()]
                car.fuel_consumption = car.fuel_consumption - rules_location[concat_location.upper()]
                car.fuel_consumed = rules_location[concat_location.upper()]
                car.last_location=car.current_location
                car.current_location=request.json['location'].upper()
            else:
                return "Not route", 409
        else:
            return "It's out of gas, it needs to recharge", 409
    else:
         return "Failed to update location", 409
    db.session.commit()
    return car_schema.jsonify(car)

# Endpoint for udpating a record
@app.route("/api/car/<id>", methods=["PATCH"])
def car_update(id):
    """Example endpoint update car , only fuel_compsumption.
    ---
    responses:
      200:
        description: updated

    """
    car = Car.query.get(id)
    fuel_consumption=request.json['fuel_consumption']
    if fuel_consumption is not None:
        if isinstance(fuel_consumption, int):
            car.fuel_consumption=request.json['fuel_consumption']
        else:
            return "must be an integer", 409


    db.session.commit()
    return car_schema.jsonify(car)

# Endpoint for deleting a record
@app.route("/car/<id>", methods=["DELETE"])
def car_delete(id):
    """Example endpoint delete.
    ---
    parameters:
        - name: id
          in: query
          type: integer
    responses:
      200:
        description: deleted car

    """
    guide = Car.query.get(id)
    db.session.delete(guide)
    db.session.commit()

    return "Guide was successfully deleted"
if __name__ == '__main__':
    app.run(debug=True)
