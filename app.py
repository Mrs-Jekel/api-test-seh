from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_cors import CORS, cross_origin
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=False)
    password = db.Column(db.String(144), unique=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password


class UserSchema(ma.Schema):
    class Meta:
        fields = ('username', 'password')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

@app.route('/')
@cross_origin()
def hello():
    return "Hey Flask"
    return "Whats up"

@app.route('/user', methods=["POST"])
@cross_origin()
def add_user():
    username = request.json['username']
    password = request.json['password']

    new_user = User(username, password)

    db.create_all()
    db.session.add(new_user)
    db.session.commit()

    user = User.query.get(new_user.id)

    return user_schema.jsonify(user)

@app.route("/users", methods=["GET"])
@cross_origin()
def get_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result)

@app.route("/user/<id>", methods=["GET"])
@cross_origin()
def get_user(id):
    user = User.query.get(id)
    return user_schema.jsonify(user)

@app.route("/user/<id>", methods=["DELETE"])
@cross_origin()
def user_delete(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()

    return "User was successfully deleted"


if __name__ == '__main__':
    app.run(debug=True)