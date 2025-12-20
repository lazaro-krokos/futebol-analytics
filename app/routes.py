from flask import Blueprint, render_template, request, jsonify, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
import pandas as pd
import json
from datetime import datetime
from database.db_connection import get_db_connection
from app.models import Player, Team, League, PlayerStats, Match

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    total_players = Player.query.count()
    total_teams = Team.query.count()
    total_leagues = League.query.count()
    total_matches = Match.query.count()
    
    return render_template('dashboard.html', 
                         total_players=total_players,
                         total_teams=total_teams,
                         total_leagues=total_leagues,
                         total_matches=total_matches)

@main_bp.route('/players')
@login_required
def players():
    league_id = request.args.get('league', '')
    team_id = request.args.get('team', '')
    position = request.args.get('position', '')
    
    query = Player.query.join(Team).join(League)
    
    if league_id:
        query = query.filter(Team.league_id == league_id)
    if team_id:
        query = query.filter(Player.team_id == team_id)
    if position:
        query = query.filter(Player.position == position)
    
    players = query.limit(100).all()
    leagues = League.query.all()
    teams = Team.query.all()
    
    return render_template('players.html', 
                         players=players, 
                         leagues=leagues, 
                         teams=teams,
                         selected_league=league_id,
                         selected_team=team_id,
                         selected_position=position)

@main_bp.route('/teams')
@login_required
def teams():
    league_id = request.args.get('league', '')
    
    query = Team.query
    if league_id:
        query = query.filter(Team.league_id == league_id)
    
    teams = query.all()
    leagues = League.query.all()
    
    return render_template('teams.html', 
                         teams=teams, 
                         leagues=leagues,
                         selected_league=league_id)

@main_bp.route('/compare')
@login_required
def compare():
    players = Player.query.limit(50).all()
    teams = Team.query.all()
    
    return render_template('compare.html', players=players, teams=teams)

@main_bp.route('/advanced-stats')
@login_required
def advanced_stats():
    return render_template('advanced_stats.html')

@main_bp.route('/api/player_stats/<int:player_id>')
@login_required
def api_player_stats(player_id):
    stats = PlayerStats.query.filter_by(player_id=player_id).all()
    
    result = {
        'seasons': [stat.season for stat in stats],
        'goals': [stat.goals for stat in stats],
        'assists': [stat.assists for stat in stats],
        'xg': [float(stat.xg) if stat.xg else 0 for stat in stats],
        'xa': [float(stat.xa) if stat.xa else 0 for stat in stats]
    }
    
    return jsonify(result)

@main_bp.route('/api/team_stats/<int:team_id>')
@login_required
def api_team_stats(team_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT season, SUM(goals), SUM(assists), AVG(xg)
        FROM player_stats ps
        JOIN players p ON ps.player_id = p.id
        WHERE p.team_id = %s
        GROUP BY season
    """, (team_id,))
    
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    seasons, goals, assists, xg = zip(*results) if results else ([], [], [], [])
    
    return jsonify({
        'seasons': seasons,
        'goals': goals,
        'assists': assists,
        'xg': [float(x) if x else 0 for x in xg]
    })

@main_bp.route('/api/top_scorers')
@login_required
def api_top_scorers():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT p.name, t.name as team, ps.goals
        FROM player_stats ps
        JOIN players p ON ps.player_id = p.id
        JOIN teams t ON p.team_id = t.id
        WHERE ps.season = '2023-2024'
        ORDER BY ps.goals DESC
        LIMIT 10
    """)
    
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    players = [{'name': r[0], 'team': r[1], 'goals': r[2]} for r in results]
    
    return jsonify(players)

@main_bp.route('/export/players')
@login_required
def export_players():
    league_id = request.args.get('league', '')
    team_id = request.args.get('team', '')
    
    query = Player.query.join(Team).join(League)
    
    if league_id:
        query = query.filter(Team.league_id == league_id)
    if team_id:
        query = query.filter(Player.team_id == team_id)
    
    players = query.limit(100).all()
    
    data = []
    for player in players:
        latest_stats = player.stats[-1] if player.stats else None
        data.append({
            'Nome': player.name,
            'Time': player.team.name if player.team else '',
            'Liga': player.team.league.name if player.team and player.team.league else '',
            'Posição': player.position,
            'Jogos': latest_stats.matches_played if latest_stats else 0,
            'Gols': latest_stats.goals if latest_stats else 0,
            'Assistências': latest_stats.assists if latest_stats else 0,
            'xG': latest_stats.xg if latest_stats else 0,
            'xA': latest_stats.xa if latest_stats else 0
        })
    
    df = pd.DataFrame(data)
    
    filename = f"jogadores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    df.to_excel(filename, index=False)
    
    return send_file(filename, as_attachment=True)

@main_bp.route('/api/teams/list')
@login_required
def api_teams_list():
    teams = Team.query.all()
    result = [{'id': team.id, 'name': team.name} for team in teams]
    return jsonify(result)

@main_bp.route('/api/xg/analysis')
@login_required
def api_xg_analysis():
    data = {
        'dates': ['2024-01-01', '2024-01-08', '2024-01-15', '2024-01-22'],
        'xg_trend': [1.2, 1.8, 1.5, 2.1],
        'goals_trend': [1, 2, 1, 3],
        'players': [
            {'name': 'Jogador A', 'xg': 8.7, 'goals': 9, 'xg_per_90': 0.65},
            {'name': 'Jogador B', 'xg': 5.2, 'goals': 6, 'xg_per_90': 0.48},
            {'name': 'Jogador C', 'xg': 3.1, 'goals': 2, 'xg_per_90': 0.32},
            {'name': 'Jogador D', 'xg': 6.5, 'goals': 7, 'xg_per_90': 0.55},
            {'name': 'Jogador E', 'xg': 4.8, 'goals': 5, 'xg_per_90': 0.41}
        ]
    }
    return jsonify(data)

@main_bp.route('/api/passing/stats')
@login_required
def api_passing_stats():
    data = {
        'avg_pass_accuracy': 82.5,
        'total_passes': 15420,
        'key_passes_per_match': 2.3,
        'short_passes_per_match': 45.2,
        'long_passes_per_match': 12.1,
        'crosses_per_match': 7.8,
        'through_balls_per_match': 1.2
    }
    return jsonify(data)

@main_bp.route('/api/possession/stats')
@login_required
def api_possession_stats():
    data = {
        'avg_possession': 58.7,
        'home_possession': 62.3,
        'away_possession': 55.1,
        'possession_trend': [55, 58, 62, 60, 59],
        'matches_dominated': 18,
        'matches_balanced': 12,
        'matches_dominated_against': 4
    }
    return jsonify(data)

@main_bp.route('/api/goal-timing/aggregated')
@login_required
def api_goal_timing_aggregated():
    data = {
        'total_goals': 42,
        'first_half_goals': 18,
        'second_half_goals': 24,
        'time_distribution': {
            '0_15': 4,
            '16_30': 7,
            '31_45': 7,
            '46_60': 9,
            '61_75': 8,
            '76_90': 6,
            'extra': 1
        },
        'avg_goal_minute': 52.3,
        'early_goals_0_15': 4,
        'late_goals_75_90': 7
    }
    return jsonify(data)

@main_bp.route('/api/correct-score/predictions')
@login_required
def api_correct_score_predictions():
    predictions = {
        'most_likely': '1-1',
        'probabilities': {
            '0-0': 15.2,
            '1-0': 12.5,
            '0-1': 11.8,
            '1-1': 18.3,
            '2-0': 8.7,
            '0-2': 7.9,
            '2-1': 9.4,
            '1-2': 8.1,
            '2-2': 5.3,
            '3+': 2.8
        },
        'both_teams_score': 68.4,
        'over_2_5': 42.7,
        'under_2_5': 57.3
    }
    return jsonify(predictions)

@main_bp.route('/api/defensive/stats')
@login_required
def api_defensive_stats():
    data = {
        'saves_per_match': 3.2,
        'interceptions_per_match': 12.5,
        'tackles_per_match': 18.7,
        'clearances_per_match': 22.1,
        'blocks_per_match': 4.8,
        'clean_sheets': 8
    }
    return jsonify(data)