from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY

db = SQLAlchemy()

class Game(db.Model):
    """ Game Model for database object """
    
    __tablename__ = 'games'

    gid = db.Column(db.Integer, primary_key=True)
    name_en = db.Column(db.String(100), nullable=False)
    authors = db.Column(ARRAY(db.String(40)))
    maxplayers = db.Column(db.Integer)
    minplayers = db.Column(db.Integer)
    max_playing_time = db.Column(db.Integer)
    min_playing_time = db.Column(db.Integer)
    best_playnum = db.Column(ARRAY(db.Integer))
    not_recom_playnum = db.Column(ARRAY(db.Integer))
    description = db.Column(db.Text)
    imageurl = db.Column(db.String(200))
    thumburl = db.Column(db.String(200))
    mechanics = db.Column(ARRAY(db.String(60)))
    average_weight = db.Column(db.Float)
    bgg_rank = db.Column(db.Integer)
    last_updated = db.Column(db.DateTime)

    def __repr__(self):
        return '<Game(id={}, name={}>'.format(self.gid, self.name_en)

    def __eq__(self, other):
        if self.gid != other.gid:
            print('Different gids -> different games!')
            return False
        if self.bgg_rank != other.bgg_rank:
            print('bgg_rank')
            return False
        if self.best_playnum != other.best_playnum:
            print('best_playnum')
            return False
        if self.not_recom_playnum != other.not_recom_playnum:
            print('not_recom_playnum')
            return False
        if self.average_weight != other.average_weight:
            print('average_weight')
            return False
        if self.imageurl != other.imageurl:
            print('imageurl')
            return False
        if self.thumburl != other.thumburl:
            print('thumburl')
            return False
        return True
