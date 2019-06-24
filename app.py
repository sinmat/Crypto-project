from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

from helpers.helpers import myconverter

from datetime import datetime

import pandas as pd

import json

import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("CLEARDB_DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/comparison")
def comparison():
    return render_template("comparison.html")


@app.route("/data")
def data():
    return render_template("data.html")


@app.route("/influencers")
def influencers():
    return render_template("influencers.html")


@app.route("/members")
def members():
    return render_template("members.html")


@app.route("/trend")
def trend():
    headers = ['close', 'date', 'name']

    query = db.engine.execute("SELECT close, date, name "
                              "FROM top_10_coins "
                              "WHERE DATE(date) > '2017-01-01'")
    line_data = [dict(zip(headers, row)) for row in query.fetchall()]
    for row in line_data:
        row['date'] = row['date'].__str__()

    headers = ['name', 'close', 'date', 'full_date', 'volume']

    query = db.engine.execute(
        "SELECT name, close, Month(date), date, AVG(volume) "
        "FROM top_10_coins "
        "GROUP BY name, Year(date), Month(date) "
        "HAVING DATE(`date`) > '2017-01-01'")

    bubble_data = [dict(zip(headers, row)) for row in query.fetchall()]
    for row in bubble_data:
        row['date'] = row['date'].__str__()

    return render_template("trend.html", line_data=line_data, bubble_data=bubble_data)


@app.route("/twitter_viz")
def twitter_viz():
    return render_template("twitter_viz.html")


@app.route("/crypto_top_10_line")
def crypto_top_10_line():
    headers = ['close', 'date', 'name']

    query = db.engine.execute("SELECT close, date, name "
                              "FROM top_10_coins "
                              "WHERE DATE(date) > '2017-01-01'")
    j = [dict(zip(headers, row)) for row in query.fetchall()]

    with open("data.json", "w") as f:
        json.dump(j, f, default=myconverter)

    return json.dumps(j, default=myconverter)


@app.route("/crypto_top_10_bubble")
def crypto_top_10_bubble():
    result = db.engine.execute("SHOW columns FROM top_10_coins")
    headers = ['name', 'close', 'date', 'full_date', 'volume']

    query = db.engine.execute(
        "SELECT name, close, Month(date), date, AVG(volume) "
        "FROM top_10_coins "
        "GROUP BY name, Year(date), Month(date) "
        "HAVING DATE(`date`) > '2017-01-01'")

    j = [dict(zip(headers, row)) for row in query.fetchall()]

    with open("data.json2", "w") as f:
        json.dump(j, f, default=myconverter)

    return json.dumps(j, default=myconverter)


@app.route("/data_string")
def data_string():
    delimter = ","
    end_of_line = "\n"

    result = db.engine.execute("SHOW columns FROM top_10_coins")
    headers = [column[0] for column in result.fetchall()]
    result_string = delimter.join(headers)
    result_string += end_of_line

    query = db.engine.execute("SELECT * "
                              "FROM top_10_coins "
                              "WHERE DATE(date) > '2017-01-01'")

    data = ""
    for row in query.fetchall():
        row = list(row)

        row[2] = datetime.strftime(row[2], "%Y-%m-%d")
        row = [str(i) for i in row]
        data += delimter.join(row)
        data += "\n"

    result_string += data

    return result_string


@app.route("/twitter_data/<agg_type>")
def twitter_data(agg_type):
    with app.open_resource('static/Resources/twitter_data.json') as f:
        df = pd.read_json(f)

    return "Hello"


if __name__ == '__main__':
    app.run()
