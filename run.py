from flask import Flask
from flask import render_template, url_for, json, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import requests
import os

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'

db = SQLAlchemy(app)


class Cities(db.Model):
    """Model for City"""
    __tablename__ = 'Cities'

    id = db.Column(db.Integer,
                   primary_key=True)
    city = db.Column(db.String,
                     nullable=False,
                     unique=False)

    def __repr__(self):
        return '<User {}>'.format(self.city)


def add_city(city_name):
    api_get = requests.get(
        f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid=3d446dd2eafa5e31768573394249249e")

    if api_get.text[24:38] == "city not found":
        flash('No City Found!', 'danger')
    else:
        if Cities.query.filter_by(city=city_name).first() == None:
            new_city = Cities(city=city_name)
            db.session.add(new_city)
            db.session.commit()


def get_cities_list(cities_list):

    weather_details_all = []
    for city in cities_list:
        name = city.city
        api_get = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={name}&appid=3d446dd2eafa5e31768573394249249e")
        api_data = api_get.json()
        id = str(api_data["id"])

        description = api_data["weather"][0]["description"]
        temp_kelvin = api_data["main"]["temp"]
        temp_celsius = round((float(temp_kelvin)-273.15), 2)
        icon = api_data["weather"][0]["icon"]
        city_name = api_data["name"]

        weather_detail = {
            'id': id,
            'city': city.city,
            'description': description,
            'tempkelvin': temp_kelvin,
            'tempcelsius': temp_celsius,
            'icon': icon,
            'city_name': city_name,

        }
        weather_details_all.append(weather_detail)
    return weather_details_all


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        new_city = (request.form.get('city')).capitalize()
        if new_city:
            add_city(new_city)

    cities_list = Cities.query.all()
    weather_details_all = get_cities_list(cities_list)
    weather_details_all.reverse()
    return render_template('index.html', weather_details_all=weather_details_all)


@app.route("/city/<int:city_id>", methods=['GET', 'POST'])
def city_weather(city_id):
    cities_data = requests.get(
        f"http://api.openweathermap.org/data/2.5/weather?id={city_id}&appid=3d446dd2eafa5e31768573394249249e")
    cities_data_json = cities_data.json()

    min_temp = cities_data_json["main"]["temp_min"]
    min_temp_celsius = round((float(min_temp)-273.15), 2)
    max_temp = cities_data_json["main"]["temp_max"]
    max_temp_celsius = round((float(max_temp)-273.15), 2)
    wind_speed = cities_data_json["wind"]["speed"]
    pressure = cities_data_json["main"]["pressure"]
    country = cities_data_json["sys"]["country"]
    extra_details = {
        'min_temp': min_temp,
        'min_temp_celsius': min_temp_celsius,
        'max_temp': max_temp,
        'max_temp_celsius': max_temp_celsius,
        'wind_speed': wind_speed,
        'pressure': pressure,
        "country": country,
    }

    return render_template("city_weather.html", cityid=city_id, extra_details=extra_details)


@app.route("/map/<string:map_type>", methods=['GET', 'POST'])
def view_map(map_type):
    return render_template("map.html", map_type=map_type)


@app.route('/city/<string:city_name>/delete', methods=['GET', 'POST'])
def delete_city(city_name):
    city_cap = city_name.capitalize()
    citi = Cities.query.all()
    print(citi)
    city = Cities.query.filter_by(city=city_cap).first()

    db.session.delete(city)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.run(debug=True)
