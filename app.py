import os
from datetime import datetime
from flask import Flask, jsonify, request, url_for, abort
from flask_cors import CORS

from Models.models import db, User, Game
import Queries

from config import conn
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from flask_jwt_extended import (JWTManager, create_access_token,
                                get_jwt_identity, jwt_required,
                                jwt_refresh_token_required, create_refresh_token)


app = Flask(__name__)
app.config.from_pyfile('config.py')
jwt = JWTManager(app)
db.init_app(app)
CORS(app)

@app.route('/', methods=['GET'])
def entry():
    users = User.query.all()
    ret = []
    for user in users:
        ret.append( {'id': user.id, 'email': user.email, 'hashed_pass': user.password_hash } )
    return jsonify(ret)

@app.route('/games', methods=['GET'])
def games():
    games = Game.query.all()
    ret = []
    for game in games:
        ret.append( {'id': game.app_id, 'name': game.name, 'init': game.init_price, 'final': game.final_price, 'discount': game.discount_percent, 'last_up': game.last_updated, "now": datetime.utcnow() } )
    return jsonify(ret)

@app.route('/api/login', methods=['POST'])
def login():
    login_json = request.get_json()

    if not login_json:
        return jsonify({'msg': 'Missing JSON' , 'type':'error'}), 400

    email = login_json.get('email')
    password = login_json.get('password')

    if not email:
        return jsonify({'msg': 'Email is missing', 'type':'error'}), 400

    if not password:
        return jsonify({'msg': 'Password is missing', 'type':'error'}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"msg": 'Email Not Found', 'type':'error'}), 401
    
    if not user.verify_password(password):
        return jsonify({"msg": 'Wrong Password', 'type':'error'}), 401

    ret = {
        "access_token": create_access_token(identity=user.id),
        "refresh_token": create_refresh_token(identity=user.id),
        "type":"success"
    }
    return jsonify(ret), 200


@app.route('/api/signup', methods=['POST'])
def sign_up():
    login_json = request.get_json()
    print("")
    print(login_json)
    if not login_json:
        return jsonify({'msg': 'Missing JSON', 'type':'error'}), 400

    email = login_json.get('email')
    password = login_json.get('password')

    if not email:
        return jsonify({'msg': 'Email is missing', 'type':'error'}), 400

    if not password:
        return jsonify({'msg': 'Password is missing', 'type':'error'}), 400

    if User.query.filter_by(email = email).first() is not None:
        return jsonify({'msg': "Email Already Exists", 'type':'error'}), 400
    
    user=User(email=email)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'msg': 'User '+email+" Created", 'type':'success'}), 201

@app.route('/api/users/<int:id>')
@jwt_required
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.email}), 200

@app.route('/api/protected', methods=['GET'])
@jwt_required
def protected():
    identity = get_jwt_identity()
    return jsonify({'msg': 'You can open this YAY',
    "id": identity}), 200

@app.route('/api/verify', methods=['GET'])
@jwt_required
def verify_user():
    return jsonify({'msg': 'confirmed'}) , 200

@app.route('/token/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    identity = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=identity)
    }
    return jsonify(ret),200

@app.route('/api/getWishlist', methods=['GET'])
@jwt_required
def get_wishlist():
    return []

@app.route('/api/addToWishlist', methods=['POST'])
@jwt_required
def addToPlayerWishlist():
    return []

@app.route('/api/deleteFromWishlist', methods=['DELETE'])
@jwt_required
def remFromPlayerWishlist():
    return []

@app.route('/api/test', methods=['POST'])
def test():
    json_data = request.get_json()
    if not json_data:
        return jsonify({'msg': 'Missing JSON', 'type':'error'}), 400
    
    appID = json_data.get('appID')
    if not appID:
        return jsonify({'msg': 'Missing appID', 'type':'error'}), 400
    queries = Queries.Queries(db)
    res = queries.addToWishlist(1,appID)
    return jsonify([res]), 200

if __name__ == '__main__':
    if database_exists(conn):
        print("DB Exists")
    else:
        print("DB must be init")
        engine = create_engine(conn)
        create_database(engine.url)
        with app.app_context():
            db.create_all()

    app.run(debug=True)