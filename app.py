import os
from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
from itertools import combinations

from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange


app = Flask(__name__)
app.config['SECRET_KEY'] = 'tommy_de_hond'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)
    # schedule = [
    #     {'week': 1, 'edit': False, 'allow_update': True,
    #      'matches': [{'player1': 'Tim', 'player2': 'Jos', 'score_home': None, 'score_away': None, 'updated': False},
    #                  {'player1': 'Frank', 'player2': 'Rob', 'score_home': None, 'score_away': None, 'updated': False}]},
    #     {'week': 2, 'edit': False, 'allow_update': True,
    #      'matches': [{'player1': 'Tim', 'player2': 'Frank', 'score_home': None, 'score_away': None, 'updated': False},
    #                  {'player1': 'Jos', 'player2': 'Rob', 'score_home': None, 'score_away': None, 'updated': False}]},
    #     {'week': 3, 'edit': False, 'allow_update': True,
    #      'matches': [{'player1': 'Tim', 'player2': 'Rob', 'score_home': None, 'score_away': None, 'updated': False},
    #                  {'player1': 'Jos', 'player2': 'Frank', 'score_home': None, 'score_away': None, 'updated': False}]}
    # ]

# players = [{'name': 'Tim', 'handicap': '4', 'score': 0},
#            {'name': 'Jos', 'handicap': '2', 'score': 0},
#            {'name': 'Frank', 'handicap': '6', 'score': 0},
#            {'name': 'Rob', 'handicap': '7', 'score': 0}]
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    handicap = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, default=0)

class Week(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True)
    edit = db.Column(db.Boolean, default=False)
    allow_update = db.Column(db.Boolean, default=True)
    matches = db.relationship('Match', backref='week', lazy=True)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player1_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    score_home = db.Column(db.Integer)
    score_away = db.Column(db.Integer)
    updated = db.Column(db.Boolean, default=False)
    week_id = db.Column(db.Integer, db.ForeignKey('week.id'), nullable=False)


with app.app_context():
    # Create all tables
    db.create_all()

class Competition:
    def __init__(self):
        self.players = []
        self.schedule = []
        self.standings = []

    def add_player(self, name, handicap):
        self.players.append({'name': name, 'handicap': handicap, 'score': 0})

    def generate_schedule(self):
        # Get all players
        players = Player.query.all()
        players_df = pd.DataFrame([(p.id, p.name) for p in players], columns=["id", "name"])
        player_combinations = list(combinations(players_df["id"].to_list(), 2))

        for i in range(len(players) - 1):
            week = Week(number=i + 1, edit=False, allow_update=True)
            db.session.add(week)
            try:
                # Commit here to ensure that the week is saved and its ID is generated
                db.session.commit()
            except Exception as e:
                print(e)
                db.session.rollback()
                return {"error": "An error occurred during week creation"}

            used_players = set()
            for j in range(len(players) // 2):
                match = None
                for combo in player_combinations:
                    if combo[0] not in used_players and combo[1] not in used_players:
                        match = combo
                        break

                if match:
                    used_players.add(match[0])
                    used_players.add(match[1])
                    new_match = Match(player1_id=match[0], player2_id=match[1], week_id=week.id)
                    db.session.add(new_match)
                    player_combinations.remove(match)

                try:
                    # Commit the matches
                    db.session.commit()
                except Exception as e:
                    print(e)
                    db.session.rollback()
                    return {"error": "An error occurred during match creation"}

        return {"message": "Schedule successfully generated"}

    def get_schedule(self):
        # Query all the weeks from the database
        weeks = Week.query.all()

        # Initialize the schedule list
        schedule = []

        # Loop through each week
        for week in weeks:
            # Query all the matches for the current week
            matches = Match.query.filter_by(week_id=week.id).all()

            # Initialize the matches list
            matches_list = []

            # Loop through each match
            for match in matches:
                # Get player names
                player1 = Player.query.get(match.player1_id).name
                player2 = Player.query.get(match.player2_id).name

                # Append match to matches list
                matches_list.append({
                    'player1': player1,
                    'player2': player2,
                    'score_home': match.score_home,
                    'score_away': match.score_away,
                    'updated': match.updated
                })

            # Append week to schedule list
            schedule.append({
                'week': week.number,
                'edit': week.edit,
                'allow_update': week.allow_update,
                'matches': matches_list
            })

        self.schedule = schedule

    def update_standings_from_schedule(self):
        # Reset all player scores
        players = Player.query.all()
        for player in players:
            player.score = 0

        # Get all the matches
        matches = Match.query.all()

        for match in matches:
            if match.updated:
                home_score = match.score_home
                away_score = match.score_away
                player1 = Player.query.get(match.player1_id)
                player2 = Player.query.get(match.player2_id)

                if home_score > away_score:
                    player1.score += 3
                elif home_score == away_score:
                    player1.score += 1
                    player2.score += 1
                elif away_score > home_score:
                    player2.score += 3

        # Commit the changes to the database
        db.session.commit()

        # Update the standings
        self.standings = sorted([{'name': p.name, 'handicap': p.handicap, 'score': p.score} for p in players],
                                key=lambda x: x['score'], reverse=True)


competition = Competition()

class PlayerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    handicap = IntegerField('Handicap', validators=[DataRequired(), NumberRange(min=0, max=100)])
    submit = SubmitField('Add Player')

@app.route('/', methods=['GET', 'POST'])
def home():
    form = PlayerForm()
    if form.validate_on_submit():
        name = form.name.data
        handicap = form.handicap.data

        # Create a new player and add them to the session
        new_player = Player(name=name, handicap=handicap, score=0)
        db.session.add(new_player)

        # Commit the session to save the changes in the database
        try:
            db.session.commit()
        except Exception as e:
            # Handle the exception
            print(e)
            db.session.rollback()
            flash('Error occurred while adding the player.', 'error')
            return redirect(url_for('home'))

        # No need for this line anymore
        # competition.add_player(name, handicap)

        return redirect(url_for('home'))
    players = Player.query.all()

    # Convert the Player objects into dictionaries
    competition.players = [{'name': player.name, 'handicap': player.handicap, 'score': player.score} for player in players]

    # Query all the players from the database
    return render_template('home.html', players=competition.players, form=form)


@app.route('/generate-competition')
def generate_competition():
    competition.generate_schedule()
    competition.get_schedule()
    return render_template('competition.html', schedule=competition.schedule, standings=competition.players)


@app.route('/edit_score/<int:week_number>', methods=['GET'])
def edit_score(week_number):
    # Get the Week object from the database
    week = Week.query.filter_by(number=week_number).first()

    if week:
        week.edit = False
        week.allow_update = True

        # Commit the changes to the database
        db.session.commit()

    return render_template('competition.html', schedule=competition.schedule, standings=competition.standings)

@app.route('/update-score', methods=['POST'])
def update_score():
    week_number = int(request.form.get('week_number'))

    # Get the Week object from the database
    week = Week.query.filter_by(number=week_number).first()

    # Get all the matches for the week
    matches = Match.query.filter_by(week_id=week.id).all()

    for i, match in enumerate(matches):
        home_score_key = f'score_home_{week_number}_{i}'
        away_score_key = f'score_away_{week_number}_{i}'
        if home_score_key in request.form and away_score_key in request.form:
            home_score = int(request.form.get(home_score_key))
            away_score = int(request.form.get(away_score_key))

            # Update the match scores in the database
            match.score_home = home_score
            match.score_away = away_score
            match.updated = True

    # Update the week's status
    week.edit = True
    week.allow_update = False

    # Commit the changes to the database
    db.session.commit()

    competition.update_standings_from_schedule()

    return render_template('competition.html', schedule=competition.schedule, standings=competition.standings)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))




## Get all weeks
# weeks = Week.query.all()
#
# # Loop through each week and print its details
# for week in weeks:
#     print(f"Week Number: {week.number}, Edit: {week.edit}, Allow Update: {week.allow_update}")


# Week.query.delete()
# db.session.commit()
