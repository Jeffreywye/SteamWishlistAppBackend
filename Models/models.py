from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context

db = SQLAlchemy()

wishlist_table = db.Table('wishlists',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('app_id', db.Integer, db.ForeignKey('games.app_id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(80), unique= True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    games = db.relationship("Game", 
                            secondary=wishlist_table,
                            backref="users")

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

class Game(db.Model):
    __tablename__ = 'games'
    app_id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(240), nullable = False)
    init_price = db.Column(db.Integer)
    final_price = db.Column(db.Integer)
    discount_percent = db.Column(db.Integer)
    # last_updated = db.Column(db.DateTime, default= datetime.utcnow)
    last_updated = db.Column(db.DateTime)