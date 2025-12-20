from flask import Blueprint, jsonify, request
from flask_login import login_required
from app.models import AdvancedPlayerStats, TeamStats, Match, db
import json

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/player/advanced/<int:player_id>')
@login_required
def get_player_advanced_stats(player_id):
    """Retorna estatísticas avançadas de um jogador"""
    stats = AdvancedPlayerStats.query.filter_by(player_id=player_id).all()
    
    result = []
    for stat in stats:
        result.append({
            'season': stat.season,
            'match_id': stat.match_id,
            'xg': stat.xg,
            'xa': stat.xa,
            'xg_chain': stat.xg_chain,
            'pass_accuracy': stat.pass_accuracy,
            'key_passes': stat.key_passes,
            'total_passes': stat.total_passes,
            'fouls_committed': stat.fouls_committed,
            'fouls_suffered': stat.fouls_suffered,
            'touches': stat.touches,
            'saves': stat.saves if stat.saves else 0,
            'goal_times': {
                '0_15': stat.goals_0_15,
                '16_30': stat.goals_16_30,
                '31_45': stat.goals_31_45,
                '46_60': stat.goals_46_60,
                '61_75': stat.goals_61_75,
                '76_90': stat.goals_76_90
            }
        })
    
    return jsonify(result)

@api_bp.route('/api/team/stats/<int:team_id>')
@login_required
def get_team_stats(team_id):
    """Retorna estatísticas do time"""
    stats = TeamStats.query.filter_by(team_id=team_id).order_by(TeamStats.season.desc()).all()
    
    aggregated = {
        'possession_avg': 0,
        'pass_accuracy_avg': 0,
        'xg_per_match': 0,
        'fouls_per_match': 0,
        'saves_per_match': 0,
        'goal_times_distribution': {},
        'by_season': []
    }
    
    total_matches = len(stats)
    if total_matches > 0:
        # Calcular médias
        aggregated['possession_avg'] = sum(s.possession for s in stats) / total_matches
        aggregated['pass_accuracy_avg'] = sum(s.pass_accuracy for s in stats) / total_matches
        aggregated['xg_per_match'] = sum(s.xg for s in stats) / total_matches
        aggregated['fouls_per_match'] = sum(s.fouls_committed for s in stats) / total_matches
        aggregated['saves_per_match'] = sum(s.saves for s in stats) / total_matches
        
        # Distribuição dos tempos dos gols
        time_slots = ['0_15', '16_30', '31_45', '46_60', '61_75', '76_90']
        for slot in time_slots:
            total = sum(getattr(s, f'goals_{slot}') for s in stats)
            aggregated['goal_times_distribution'][slot] = total
    
    # Estatísticas por temporada
    seasons = {}
    for stat in stats:
        if stat.season not in seasons:
            seasons[stat.season] = {
                'matches': 0,
                'possession': 0,
                'xg': 0,
                'fouls': 0,
                'saves': 0
            }
        seasons[stat.season]['matches'] += 1
        seasons[stat.season]['possession'] += stat.possession
        seasons[stat.season]['xg'] += stat.xg
        seasons[stat.season]['fouls'] += stat.fouls_committed
        seasons[stat.season]['saves'] += stat.saves
    
    for season, data in seasons.items():
        matches = data['matches']
        aggregated['by_season'].append({
            'season': season,
            'possession_avg': data['possession'] / matches if matches > 0 else 0,
            'xg_avg': data['xg'] / matches if matches > 0 else 0,
            'fouls_avg': data['fouls'] / matches if matches > 0 else 0,
            'saves_avg': data['saves'] / matches if matches > 0 else 0
        })
    
    return jsonify(aggregated)

@api_bp.route('/api/match/goal-analysis/<int:match_id>')
@login_required
def get_match_goal_analysis(match_id):
    """Análise de tempos dos gols de uma partida"""
    match = Match.query.get_or_404(match_id)
    
    # Extrair tempos dos gols
    goal_times = match.get_goal_times_list()
    
    # Classificar por intervalo de tempo
    time_slots = {
        '0-15': 0, '16-30': 0, '31-45': 0,
        '46-60': 0, '61-75': 0, '76-90': 0,
        'extra': 0
    }
    
    for minute in goal_times:
        if minute <= 15:
            time_slots['0-15'] += 1
        elif minute <= 30:
            time_slots['16-30'] += 1
        elif minute <= 45:
            time_slots['31-45'] += 1
        elif minute <= 60:
            time_slots['46-60'] += 1
        elif minute <= 75:
            time_slots['61-75'] += 1
        elif minute <= 90:
            time_slots['76-90'] += 1
        else:
            time_slots['extra'] += 1
    
    return jsonify({
        'total_goals': len(goal_times),
        'goal_times': goal_times,
        'time_distribution': time_slots,
        'first_half_goals': sum(1 for m in goal_times if m <= 45),
        'second_half_goals': sum(1 for m in goal_times if m > 45)
    })

@api_bp.route('/api/correct-score/predictions')
@login_required
def get_correct_score_predictions():
    """Retorna previsões de placar exato"""
    # Obter parâmetros
    home_team_id = request.args.get('home_team')
    away_team_id = request.args.get('away_team')
    
    # Lógica de previsão (simplificada)
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

@api_bp.route('/api/player/passing-stats/<int:player_id>')
@login_required
def get_player_passing_stats(player_id):
    """Estatísticas de passes do jogador"""
    stats = AdvancedPlayerStats.query.filter_by(player_id=player_id).all()
    
    if not stats:
        return jsonify({'error': 'No stats found'}), 404
    
    total_matches = len(stats)
    
    aggregated = {
        'total_passes': sum(s.total_passes for s in stats),
        'accurate_passes': sum(s.accurate_passes for s in stats),
        'avg_pass_accuracy': sum(s.pass_accuracy for s in stats) / total_matches,
        'key_passes_per_match': sum(s.key_passes for s in stats) / total_matches,
        'through_balls': sum(s.through_balls for s in stats),
        'crosses': sum(s.crosses for s in stats),
        'long_balls': sum(s.long_balls for s in stats),
        'by_match': [
            {
                'match_id': s.match_id,
                'pass_accuracy': s.pass_accuracy,
                'key_passes': s.key_passes,
                'total_passes': s.total_passes
            } for s in stats[-10:]  # Últimas 10 partidas
        ]
    }
    
    return jsonify(aggregated)

@api_bp.route('/api/defensive/stats')
@login_required
def get_defensive_stats():
    """Estatísticas defensivas agregadas"""
    team_id = request.args.get('team_id')
    player_id = request.args.get('player_id')
    
    if team_id:
        # Estatísticas do time
        stats = TeamStats.query.filter_by(team_id=team_id).all()
        
        aggregated = {
            'saves_per_match': 0,
            'interceptions_per_match': 0,
            'tackles_per_match': 0,
            'clearances_per_match': 0,
            'blocks_per_match': 0,
            'clean_sheets': 0
        }
        
        if stats:
            total_matches = len(stats)
            aggregated['saves_per_match'] = sum(s.saves for s in stats) / total_matches
            aggregated['interceptions_per_match'] = sum(s.interceptions for s in stats) / total_matches
            aggregated['tackles_per_match'] = sum(s.tackles for s in stats) / total_matches
            aggregated['clearances_per_match'] = sum(s.clearances for s in stats) / total_matches
            aggregated['blocks_per_match'] = sum(s.blocks for s in stats) / total_matches
            
        return jsonify(aggregated)
    
    elif player_id:
        # Estatísticas do jogador (se for goleiro ou defensor)
        stats = AdvancedPlayerStats.query.filter_by(player_id=player_id).all()
        
        aggregated = {
            'is_goalkeeper': False,
            'saves': 0,
            'tackles_per_match': 0,
            'interceptions_per_match': 0,
            'fouls_committed_per_match': 0,
            'clearances_per_match': 0
        }
        
        if stats:
            total_matches = len(stats)
            # Verificar se é goleiro (tem saves)
            total_saves = sum(s.saves for s in stats)
            if total_saves > 0:
                aggregated['is_goalkeeper'] = True
                aggregated['saves'] = total_saves
            
            aggregated['tackles_per_match'] = sum(s.fouls_committed for s in stats) / total_matches
            aggregated['fouls_committed_per_match'] = aggregated['tackles_per_match']
            
        return jsonify(aggregated)
    
    return jsonify({'error': 'Specify team_id or player_id'}), 400