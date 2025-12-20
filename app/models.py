from database.db_connection import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<User {self.username}>'

class League(db.Model):
    __tablename__ = 'leagues'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(50))
    season = db.Column(db.String(20))
    url = db.Column(db.String(500))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    teams = db.relationship('Team', backref='league', lazy=True)

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'))
    url = db.Column(db.String(500))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    players = db.relationship('Player', backref='team', lazy=True)

class Player(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    position = db.Column(db.String(50))
    nationality = db.Column(db.String(50))
    age = db.Column(db.Integer)
    url = db.Column(db.String(500))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    stats = db.relationship('PlayerStats', backref='player', lazy=True)

class PlayerStats(db.Model):
    __tablename__ = 'player_stats'
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'))
    season = db.Column(db.String(20))
    matches_played = db.Column(db.Integer)
    goals = db.Column(db.Integer)
    assists = db.Column(db.Integer)
    minutes_played = db.Column(db.Integer)
    xg = db.Column(db.Float)
    xa = db.Column(db.Float)
    shots = db.Column(db.Integer)
    key_passes = db.Column(db.Integer)
    yellow_cards = db.Column(db.Integer)
    red_cards = db.Column(db.Integer)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    home_goals = db.Column(db.Integer)
    away_goals = db.Column(db.Integer)
    result = db.Column(db.String(10))
    possession_home = db.Column(db.Float)
    possession_away = db.Column(db.Float)
    shots_home = db.Column(db.Integer)
    shots_away = db.Column(db.Integer)
    xg_home = db.Column(db.Float)
    xg_away = db.Column(db.Float)
    passes_home = db.Column(db.Integer)
    passes_away = db.Column(db.Integer)
    pass_accuracy_home = db.Column(db.Float)
    pass_accuracy_away = db.Column(db.Float)
    fouls_home = db.Column(db.Integer)
    fouls_away = db.Column(db.Integer)
    corners_home = db.Column(db.Integer)
    corners_away = db.Column(db.Integer)
    saves_home = db.Column(db.Integer)
    saves_away = db.Column(db.Integer)
    goal_times = db.Column(db.Text)
    correct_score = db.Column(db.String(10))
    score_probabilities = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    home_team = db.relationship('Team', foreign_keys=[home_team_id])
    away_team = db.relationship('Team', foreign_keys=[away_team_id])
    
    def get_goal_times_list(self):
        """Retorna lista de minutos dos gols"""
        if self.goal_times:
            return [int(t) for t in self.goal_times.split(',')]
        return []
    
    def get_score_probabilities_dict(self):
        """Retorna dicionário de probabilidades"""
        if self.score_probabilities:
            import json
            return json.loads(self.score_probabilities)
        return {}

class AdvancedPlayerStats(db.Model):
    __tablename__ = 'advanced_player_stats'
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'))
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'))
    season = db.Column(db.String(20))
    xg = db.Column(db.Float, default=0.0)
    xa = db.Column(db.Float, default=0.0)
    xg_chain = db.Column(db.Float, default=0.0)
    xg_buildup = db.Column(db.Float, default=0.0)
    total_passes = db.Column(db.Integer, default=0)
    accurate_passes = db.Column(db.Integer, default=0)
    pass_accuracy = db.Column(db.Float, default=0.0)
    key_passes = db.Column(db.Integer, default=0)
    through_balls = db.Column(db.Integer, default=0)
    crosses = db.Column(db.Integer, default=0)
    long_balls = db.Column(db.Integer, default=0)
    saves = db.Column(db.Integer, default=0)
    saves_inside_box = db.Column(db.Integer, default=0)
    saves_penalties = db.Column(db.Integer, default=0)
    punches = db.Column(db.Integer, default=0)
    catches = db.Column(db.Integer, default=0)
    fouls_committed = db.Column(db.Integer, default=0)
    fouls_suffered = db.Column(db.Integer, default=0)
    yellow_cards = db.Column(db.Integer, default=0)
    red_cards = db.Column(db.Integer, default=0)
    touches = db.Column(db.Integer, default=0)
    touches_att_third = db.Column(db.Integer, default=0)
    carries = db.Column(db.Integer, default=0)
    progressive_carries = db.Column(db.Integer, default=0)
    goals_0_15 = db.Column(db.Integer, default=0)
    goals_16_30 = db.Column(db.Integer, default=0)
    goals_31_45 = db.Column(db.Integer, default=0)
    goals_46_60 = db.Column(db.Integer, default=0)
    goals_61_75 = db.Column(db.Integer, default=0)
    goals_76_90 = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    player = db.relationship('Player', backref=db.backref('advanced_stats', lazy=True))
    match = db.relationship('Match', backref=db.backref('player_advanced_stats', lazy=True))

class TeamStats(db.Model):
    __tablename__ = 'team_stats'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'))
    season = db.Column(db.String(20))
    possession = db.Column(db.Float, default=0.0)
    total_passes = db.Column(db.Integer, default=0)
    accurate_passes = db.Column(db.Integer, default=0)
    pass_accuracy = db.Column(db.Float, default=0.0)
    total_shots = db.Column(db.Integer, default=0)
    shots_on_target = db.Column(db.Integer, default=0)
    shots_off_target = db.Column(db.Integer, default=0)
    shots_blocked = db.Column(db.Integer, default=0)
    xg = db.Column(db.Float, default=0.0)
    xg_against = db.Column(db.Float, default=0.0)
    fouls_committed = db.Column(db.Integer, default=0)
    fouls_suffered = db.Column(db.Integer, default=0)
    saves = db.Column(db.Integer, default=0)
    interceptions = db.Column(db.Integer, default=0)
    tackles = db.Column(db.Integer, default=0)
    clearances = db.Column(db.Integer, default=0)
    blocks = db.Column(db.Integer, default=0)
    corners = db.Column(db.Integer, default=0)
    offsides = db.Column(db.Integer, default=0)
    crosses = db.Column(db.Integer, default=0)
    win_probability = db.Column(db.Float, default=0.0)
    draw_probability = db.Column(db.Float, default=0.0)
    loss_probability = db.Column(db.Float, default=0.0)
    goals_0_15 = db.Column(db.Integer, default=0)
    goals_16_30 = db.Column(db.Integer, default=0)
    goals_31_45 = db.Column(db.Integer, default=0)
    goals_46_60 = db.Column(db.Integer, default=0)
    goals_61_75 = db.Column(db.Integer, default=0)
    goals_76_90 = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    team = db.relationship('Team', backref=db.backref('team_stats', lazy=True))
    match = db.relationship('Match', backref=db.backref('team_stats_details', lazy=True))