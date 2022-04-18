from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
import secrets
from random import choice

app = Flask(__name__)
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        # for column in self.__table__.columns:
        #     dictionary[column.name] = getattr(self, column.name)
        # return dictionary
        # Or we can use Dictionary comprehension
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


# User TABLE Registration
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    api_token = db.Column(db.String(250), unique=True, nullable=False)


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - API-TOKEN
@app.route("/get-api-token", methods=["GET"])
def get_api_token():
    api_token = secrets.token_hex(16)
    if request.method == "GET":
        data = request.get_json()
        users_name = db.session.query(User).filter_by(username=data.get("username")).first()
        if users_name:
            return jsonify(created={"API TOKEN": users_name.api_token})
        else:
            new_user = User(username=data.get("username"),
                            password=data.get("password"),
                            api_token=api_token)
            db.session.add(new_user)
            db.session.commit()
            return jsonify(created={"API TOKEN": api_token})
    else:
        return jsonify(error={"Wrong request": "You need to use GET Request."})


# HTTP GET - RANDOM CAFE
@app.route("/random", methods=["GET"])
def random():
    if request.method == "GET":
        all_cafe = db.session.query(Cafe).all()
        random_cafe = choice(all_cafe)
        return jsonify(cafe={random_cafe.name: random_cafe.to_dict()})
    else:
        return jsonify(error={"Method Not Allowed": "The method is not allowed for the requested URL."}), 405


# HTTP GET - Read Record
@app.route("/all", methods=["GET", "POST"])
def all_cafes():
    if request.method == "GET":
        cafes = db.session.query(Cafe).all()
        return jsonify(all_cafes=[cafe.to_dict() for cafe in cafes])
    else:
        return jsonify(error={"Method Not Allowed": "The method is not allowed for the requested URL."}), 405


# HTTP GET - SEARCH RECORD
@app.route("/search", methods=["GET"])
def search():
    if request.method == "GET":
        loc = request.args.get("loc")
        results = db.session.query(Cafe).filter(Cafe.location == loc).all()
        limit = int(request.args.get("limit")) if request.args.get("limit") is not None else len(results)
        results = db.session.query(Cafe).filter(Cafe.location == loc).all()
        return jsonify(results=[result.to_dict() for result in results[:limit]]) if len(
            results) and limit != 0 else jsonify(
            error={"Not found": "We did not have a cafe in  this location or you can not use a zero limit."}), 404


# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add():
    if request.method == "POST":
        user_api_token = request.headers.get("x-api-key")
        user = db.session.query(User).filter(User.api_token == user_api_token).first()
        if user:
            body_data = request.get_json()

            def add_data(data:dict) -> dict:
                """
                This function will take a body data and check where we have a boolean data type and convert it to
                valid boolean type.
                :param data:
                :return:
                """
                for key, value in data.items():
                    if value == "true":
                        data[key] = True
                    elif value == "false":
                        data[key] = False
                return data

            data = add_data(body_data)
            cafe = Cafe(**data)
            db.session.add(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully new cafe added by {} .".format(user.username)})
        else:
            return jsonify(error={"Not Allowed": "You need an Api key for this service."}), 401


# HTTP PUT/PATCH - Update Record
@app.route("/update-price", methods=["PATCH"])
def update_price():
    body_data = request.get_json()
    cafe_id = body_data["cafe_id"]
    if request.method == "PATCH":
        user_api_token = request.headers.get("x-api-key")
        user = db.session.query(User).filter(User.api_token == user_api_token).first()
        if user:
            new_price = body_data["new-price"]
            cafe = db.session.query(Cafe).get(cafe_id)
            if request.method == "POST":
                if cafe and new_price:
                    return redirect(url_for("update_price", cafe_id=cafe_id))
            else:
                if cafe:
                    if new_price:
                        cafe.coffee_price = new_price
                        db.session.commit()
                        return jsonify(response={
                            "success": "Successfully Coffee price updated for {} by {}.".format(cafe.name,
                                                                                                user.username)})
                    else:
                        return jsonify(error={"No Price": "You seem forgot to add a coffee price."}), 404
                else:
                    return jsonify(error={"Not Found": "We can not found cafe with id {}.".format(cafe_id)}), 404
        else:
            return jsonify(error={"Not Allowed": "Your Api key is not allowed."}), 401


# HTTP DELETE - Delete Record
@app.route("/report-closed", methods=["DELETE"])
def delete_cafe():
    cafe_id = request.get_json()["cafe_id"]
    if request.method == "DELETE":
        cafe = db.session.query(Cafe).get(cafe_id)
        user_api_token = request.headers.get("x-api-key")
        user = db.session.query(User).filter(User.api_token == user_api_token).first()
        if user:
            if cafe:
                db.session.delete(cafe)
                db.session.commit()
                return jsonify(
                    response={
                        "success": "Successfully deleted {} from database by {} .".format(cafe.name, user.username)})
            else:
                return jsonify(error={"Not Found": "We can not found cafe with id {}.".format(cafe_id)}), 404
        else:
            return jsonify(error={"Not Allowed": "Your Api key is not allowed."}), 401


if __name__ == '__main__':
    app.run(debug=True)
