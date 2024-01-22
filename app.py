# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from dateutil.relativedelta import relativedelta
from datetime import datetime
from flask import Flask, jsonify



#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# reflect the tables
Base = automap_base()
Base.prepare(autoload_with=engine)
# Save references to each table
Station=Base.classes.stations
Measurement=Base.classes.measurements

# Create our session (link) from Python to the DB

session= db.session

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return(
        f'Welcome to the Precipitation website API! <br/>'
        f'Available Routes:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/<start><br/>'
        f'/api/v1.0/<start>/<end>'
    )
#1. Query
@app.route('/api/v1.0/precipitation')
def precipitacion():
    session = Session(engine)

    #query for the get the 12 month of precipitation:
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = datetime.strptime(most_recent_date,'%Y-%m-%d')
    one_year_before= most_recent_date - relativedelta(years=1)
    one_year_before= one_year_before.strftime('%Y-%m-%d')   
    results= session.query(Measurement.station,Measurement.date,Measurement.prcp,Measurement.tobs).filter(Measurement.date >= one_year_before).all()
    session.close()
    one_year_before_data=list(np.ravel(results))

    return dict(one_year_before_data)
#2.Query
@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    results= session.query(Station.station).all()

    session.close()

    #convert the list of tuples into normal list
    all_stations=list(np.ravel(results))

    return jsonify(all_stations)

#3.Query
@app.route('/api/v1.0/tobs')
def most_active_station():
    session = Session(engine)
    #query to get the most active station and the temperatures.
    most_active_station= (session.query(Measurement.station,
            func.count().label('station_count'))
            .group_by(Measurement.station)
            .order_by(func.count().desc())
            .first())
    most_active_station_id= most_active_station.station
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = datetime.strptime(most_recent_date,'%Y-%m-%d')
    one_year_before= most_recent_date - relativedelta(years=1)
    one_year_before= one_year_before.strftime('%Y-%m-%d')   
    temperature_one_year= (session.query(Measurement.tobs)
                       .filter(Measurement.station == most_active_station_id,
                               Measurement.date >= one_year_before)).all()
    
    session.close()

    temperatures=list(np.ravel(temperature_one_year))

    return jsonify(temperatures)

#4.Query

@app.route('/api/v1.0/<start>')
def stats_with_start(start):
    session = Session(engine)
    query=(session.query(
        func.min(Measurement.tobs).label('min_temperature'),
        func.max(Measurement.tobs).label('max_temperature'),
        func.avg(Measurement.tobs).label('avg_temperature')
    )
    .filter(Measurement.date>= start)
        .group_by(Measurement.date))

    temp_stats= query.all()
    session.close()

    return jsonify(temp_stats)

@app.route('/api/v1.0/<start>/<end>')
def stats_with_start(start,end):
    session = Session(engine)
    query=(session.query(
        func.min(Measurement.tobs).label('min_temperature'),
        func.max(Measurement.tobs).label('max_temperature'),
        func.avg(Measurement.tobs).label('avg_temperature')
    )
    .filter(Measurement.date>= start,Measurement.date<=end)
        .group_by(Measurement.date))

    temp_stats= query.all()
    session.close()

    return jsonify(temp_stats)   

if __name__ =='__main__':
    app.run(debug=True)
    