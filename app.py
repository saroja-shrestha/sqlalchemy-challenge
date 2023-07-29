#Import the dependencies.
from flask import Flask, jsonify
from datetime import datetime as dt, timedelta as td
import numpy as np
import sqlalchemy
from sqlalchemy import create_engine, func, desc
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

#################################################

#Database Setup
#################################################

#Create engine to connect to the SQLite database.
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#Reflect the database into a new model.
Base = automap_base()

#Reflect the tables.
Base.prepare(engine, reflect=True)

#Save references to each table.
Measurement = Base.classes.measurement
Station = Base.classes.station

#Create our session (link) from Python to the DB. 
session = Session(engine)

#################################################

#Flask Setup
#################################################

#Create a Flask app.
app = Flask(__name__)

#################################################

#Flask Routes
#################################################

#Define the root route.
@app.route("/")
def home():
    #"""List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

#Define the precipitation route.
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create a new session.
    session = Session(engine)

    #"""Return a list of the last 12 months of precipitation data."""

    # Calculate the date 1 year ago from the last data point in the database.
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = dt.strptime(recent_date, "%Y-%m-%d") - td(days=365)

    # Query the last 12 months of precipitation data.
    prcp_data = session.query(Measurement.date, Measurement.prcp) \
        .filter(Measurement.date >= one_year_ago) \
        .order_by(Measurement.date) \
        .all()

    # Convert the query results to a dictionary.
    prcp_dict = {}
    for result in prcp_data:
        prcp_dict[result[0]] = result[1]
    # Close the session.
    session.close()
    # Return the JSON representation of the dictionary.
    return jsonify(prcp_dict)

#Define the stations route.
@app.route("/api/v1.0/stations")
def stations():
    # Create a new session.
    session = Session(engine)
    """Return a list of all stations."""
    # Query all stations.
    station_data = session.query(Station.station, Station.name).all()

    # Convert the query results to a list of dictionaries.
    station_list = []
    for result in station_data:
        station_dict = {}
        station_dict["station"] = result.station
        station_dict["name"] = result.name
        station_list.append(station_dict)
    # Close the session.
    session.close()
    # Return the JSON representation of the list.
    return jsonify(station_list)

# Define the tobs route.
@app.route("/api/v1.0/tobs")
def tobs():
    # Create a new session.
    session = Session(engine)
    """Return a list of the last 12 months of temperature observations for the most active station."""
    # Query the most active station.
    recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = (dt.strptime(recent_date, '%Y-%m-%d').date() - td(days=365)).strftime('%Y-%m-%d')

    most_active_station = session.query(Measurement.station, func.count(Measurement.station))\
    .group_by(Measurement.station)\
    .order_by(func.count(Measurement.station).desc())\
    .first()[0]
    # Calculate the date 1 year ago from the last data point in the database.
    tobs_data = session.query(Measurement.date, Measurement.tobs) \
              .filter(Measurement.date >= one_year_ago) \
              .filter(Measurement.station == most_active_station) \
              .all()
   # Create a dictionary with date as key and temperature as value
    tobs_dict = {}
    for row in tobs_data:
        tobs_dict[row[0]] = row[1]

    # Close the session.
    session.close()


   # Return the JSON representation of the dictionary
    return jsonify(tobs_dict)

if __name__ == '__main__':
    app.run()
