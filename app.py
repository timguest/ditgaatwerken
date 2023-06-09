import os

from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from itertools import combinations

app = Flask(__name__)

# In memory storage for player data. Use a database in production.
players = []
schedule = []
standings = []

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form.get('name')
        handicap = request.form.get('handicap')

        players.append({'name': name, 'handicap': handicap, 'score': 0})

        return redirect(url_for('home'))

    return render_template('home.html', players=players)


@app.route('/generate-competition')
def generate_competition():
    global schedule
    global standings

    # schedule = generate_schedule(pd.DataFrame(players))
    schedule = [[('Tim', 'Jos', 1), ('Frank', 'Rob', 1)], [('Tim', 'Frank', 2), ('Jos', 'Rob', 2)],
                [('Tim', 'Rob', 3), ('Jos', 'Frank', 3)]]
    # standings = players
    standings = [{'name': 'Tim', 'handicap': '4', 'score': 0}, {'name': 'Jos', 'handicap': '2', 'score': 0}, {'name': 'Frank', 'handicap': '6', 'score': 0}, {'name': 'Rob', 'handicap': '7', 'score': 0}]

    # Adding extra parameter with outer loop indices
    schedule = [(i, week_schedule) for i, week_schedule in enumerate(schedule)]

    return render_template('competition.html', schedule=schedule, standings=standings)


def generate_schedule(players_df):
    players = players_df['name'].tolist()
    schedule = []

    # Generate combinations of players
    player_combinations = list(combinations(players, 2))

    # Generate schedule for each week
    for i in range(len(players) - 1):
        week_schedule = []
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
                # Include week number with match
                week_schedule.append((match[0], match[1], i + 1))
                player_combinations.remove(match)
        schedule.append(week_schedule)

    return schedule


@app.route('/update_score', methods=['POST'])
def update_score():
    week_number = int(request.form.get('week_number'))
    for i, week_schedule in enumerate(schedule):
        if i == week_number:
            for j, match in enumerate(week_schedule[1]):
                home_score = int(request.form.get('score_home_' + str(i) + '_' + str(j), 0))
                away_score = int(request.form.get('score_away_' + str(i) + '_' + str(j), 0))

                # Store scores in the match
                match.append((home_score, away_score))

                if home_score is not None and away_score is not None:
                    home_player = match[0]
                    away_player = match[1]

                    if home_score > away_score:
                        update_standings(home_player, 3)
                    elif home_score < away_score:
                        update_standings(away_player, 3)
                    else:
                        update_standings(home_player, 1)
                        update_standings(away_player, 1)
            # Stop the loop after the correct week has been found
            break

    # sort standings by score
    standings.sort(key=lambda x: x['score'], reverse=True)

    return render_template('competition.html', schedule=schedule, standings=standings)




def update_standings(player_name, points):
    for player in standings:
        if player['name'] == player_name:
            player['score'] += points
            break


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
