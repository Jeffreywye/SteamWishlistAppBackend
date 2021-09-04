import os
from datetime import datetime
from flask import Flask, json, jsonify, request, url_for, abort
from flask_cors import CORS
# from apscheduler.schedulers.background import BackgroundScheduler
from flask_mail import Mail, Message

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
mail = Mail()
mail.init_app(app)
db.init_app(app)
CORS(app)

# @app.route('/', methods=['GET'])
# def entry():
#     users = User.query.all()
#     ret = []
#     if not users:
#         return jsonify(["empty"])
#     for user in users:
#         ret.append( {'id': user.id, 'email': user.email, 'hashed_pass': user.password_hash } )
#     return jsonify(ret)

# @app.route('/games', methods=['GET'])
# def games():
#     games = Game.query.all()
#     ret = []
#     for game in games:
#         ret.append( {'id': game.app_id, 'name': game.name, 'init': game.init_price, 'final': game.final_price, 'discount': game.discount_percent, 'last_up': game.last_updated, "now": datetime.utcnow() } )
#     return jsonify(ret)

def reformatGamesToEmail(gamesList):
    ret = "Games On Sale Today\n"
    for game in gamesList:
        ret = ret + "\nTitle: "+ str(game['name']) + "\nApp ID: "+ str(game['appID'])+ "\nCurrent Price: "+ str(game['final price'])+"\nOriginal Price: "+ str(game['init price'])+"\nDiscount Percent: "+ str(game['discount percent'])+'\n'
    return ret


def sendEmails():
    with app.app_context():
        queries = Queries.Queries(db)
        
        if not queries.updateGames():
            print("Failed to update games")

        userGames = queries.getUsersGames()
        for userId in userGames:
            try:
                emailBody = reformatGamesToEmail(userGames[userId]['games'])
                msg = Message(subject="Steam Games Update", sender="jye7apps@gmail.com", recipients=[userGames[userId]['email']])
                msg.body = emailBody
                mail.send(msg)
            except Exception as e:
                print("\nFailed to send mail to "+userGames[userId]['email']+"\n")
                print(e)

# test route
# @app.route('/mail', methods=['Get'])
# def testMail():
#     sendEmails()
#     return jsonify([]), 200
    
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
    identity = get_jwt_identity()
    queries = Queries.Queries(db)
    try:
        games = queries.getWishlist(identity)
    except:
        return jsonify("Failed to retrive list"), 500
    return jsonify(games), 200

@app.route('/api/addToWishlist', methods=['POST'])
@jwt_required
def addToPlayerWishlist():
    json_data = request.get_json()
    identity = get_jwt_identity()
    if not json_data:
        return jsonify({'msg': 'Missing JSON', 'type':'error'}), 400
    
    try:
        appID = int(json_data.get('appID'))
    except:
        return jsonify({'msg': 'Missing appID', 'type':'error'}), 400
        
    queries = Queries.Queries(db)
    res = queries.addToWishlist(identity,appID)
    if not res:
        return jsonify({"msg": "Failed to add app" }), 400
    return jsonify(res), 200

@app.route('/api/deleteFromWishlist', methods=['DELETE'])
@jwt_required
def remFromPlayerWishlist():
    identity = get_jwt_identity()
    json_data = request.get_json()
    if not json_data:
        return jsonify({'msg': 'Missing JSON', 'type':'error'}), 400
    
    try:
        appID = int(json_data.get('appID'))
    except:
        return jsonify({'msg': 'Missing appID', 'type':'error'}), 400

    queries = Queries.Queries(db)
    res = queries.removeFromWishlist(identity,appID)
    if not res:
        return jsonify({"msg": "Failed to remove from list" }), 500
    return jsonify({'msg':'App removed'}), 200

if __name__ == '__main__':
    if database_exists(conn):
        print("DB Exists")
    else:
        print("DB must be init")
        engine = create_engine(conn)
        create_database(engine.url)
        with app.app_context():
            db.create_all()
    
    # not needed for production
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(sendEmails,"cron",minute="*/10", hour="*")
    # scheduler.start()

    app.run()
    