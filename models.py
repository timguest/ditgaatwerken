from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    handicap = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'name': self.name,
            'handicap': self.handicap,
            'score': self.score
        }
