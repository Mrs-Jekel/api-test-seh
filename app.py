from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_login import UserMixin, login_user, logout_user, login_required, LoginManager
from flask_cors import CORS, cross_origin
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thiswillbesecretkey'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'user.db')
db = SQLAlchemy(app)
ma = Marshmallow(app)
# migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=False)
    password = db.Column(db.String(144), unique=False)

    # def __init__(self, username, password):
    #     self.username = username
    #     self.password = password

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
    
def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

@app.route('/signup', methods=['POST'])
@cross_origin()
def signup_post():
    
    username = request.json.get('username')
    password = request.json.get('password')

#  User.query.filter_by(username=username).first()

    if username is None or password is None:
        abort(400)

    if  User.query.filter_by(username=username).first() is not None:
        abort(400)

    
    new_user = User(username=username, password=generate_password_hash(password, method='sha256'))

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'username': new_user.username })    

@app.route('/login', methods=["GET", "POST"])
@cross_origin()
def login():
    
    username = request.json.get('username')
    password = request.json.get('password')
    remember = True if request.json.get('remember') else False

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password): 
        return ('incorrect Credentials') # if user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return('correct credentials')

    # username = request.json['username']
    # password = request.json['password']

    # new_user = User(username, password)

    # db.create_all()
    # db.session.add(new_user)
    # db.session.commit()

    # user = User.query.get(new_user.id)

    # return user_schema.jsonify(user)

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