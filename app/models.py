from app import db
import datetime

#This is where we create our fields for the db. You can add / mod these to your liking.
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(10), index=True, unique=False)
    hostname = db.Column(db.String(120), index=True, unique=False)
    score = db.Column(db.Integer, index=True, unique=False)
    date = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow())

    def __repr__(self):
        return '<User {}>'.format(self.username)
