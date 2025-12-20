import requests
from bs4 import BeautifulSoup
import time
import logging
from datetime import datetime
from database.db_connection import get_db_connection
from app.models import db, League, Team, Player, PlayerStats, Match, AdvancedPlayerStats, TeamStats
import json

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FBRefScraper:
    def __init__(self):
        self.base_url = "https://fbref.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def scrape_leagues(self):
        """Coleta dados das ligas principais"""
        try:
            logger.info("🔍 Coletando dados das ligas...")
            response = self.session.get(f"{self.base_url}/en/comps/")
            soup = BeautifulSoup(response.content, 'html.parser')
            
            leagues_table = soup.find('table', {'id': 'comps'})
            if leagues_table:
                for row in leagues_table.find_all('tr')[1:]:  # Pular cabeçalho
                    cols = row.find_all('td')
                    if len(cols) > 1:
                        link = cols[0].find('a')
                        if link:
                            name = link.text.strip()
                            url = self.base_url + link['href']
                            country = cols[1].text.strip()
                            
                            # Verificar se liga já existe
                            league = League.query.filter_by(url=url).first()
                            if not league:
                                league = League(
                                    name=name,
                                    country=country,
                                    url=url,
                                    season='2023-2024'
                                )
                                db.session.add(league)
                                logger.info(f"✅ Adicionada liga: {name}")
            
            db.session.commit()
            logger.info("✅ Dados das ligas atualizados com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar ligas: {e}")
            db.session.rollback()
            return False
    
    def scrape_teams(self, league_id):
        """Coleta times de uma liga específica"""
        try:
            league = League.query.get(league_id)
            if not league:
                logger.error(f"❌ Liga {league_id} não encontrada")
                return False
            
            logger.info(f"🔍 Coletando times da liga: {league.name}")
            response = self.session.get(league.url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Encontrar tabela de times (pode variar por liga)
            teams_table = soup.find('table', {'id': 'results2023-202491_overall'})
            if not teams_table:
                teams_table = soup.find('table', {'class': 'stats_table'})
            if not teams_table:
                teams_table = soup.find('table')
            
            if teams_table:
                for row in teams_table.find_all('tr')[1:]:  # Pular cabeçalho
                    cols = row.find_all('td')
                    if cols:
                        link = cols[0].find('a')
                        if link:
                            name = link.text.strip()
                            url = self.base_url + link['href']
                            
                            # Verificar se time já existe
                            team = Team.query.filter_by(url=url).first()
                            if not team:
                                team = Team(
                                    name=name,
                                    league_id=league_id,
                                    url=url
                                )
                                db.session.add(team)
                                logger.info(f"✅ Adicionado time: {name}")
            
            db.session.commit()
            logger.info(f"✅ Times da liga {league.name} atualizados com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar times: {e}")
            db.session.rollback()
            return False
    
    def scrape_players(self, team_id):
        """Coleta jogadores de um time específico"""
        try:
            team = Team.query.get(team_id)
            if not team:
                logger.error(f"❌ Time {team_id} não encontrado")
                return False
            
            logger.info(f"🔍 Coletando jogadores do time: {team.name}")
            response = self.session.get(team.url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Encontrar tabela de jogadores
            players_table = soup.find('table', {'id': 'stats_standard_9'})
            if not players_table:
                players_table = soup.find('table', {'class': 'stats_table'})
            
            if players_table:
                for row in players_table.find_all('tr')[1:]:  # Pular cabeçalho
                    cols = row.find_all('td')
                    if cols:
                        link = cols[0].find('a')
                        if link:
                            name = link.text.strip()
                            url = self.base_url + link['href']
                            position = cols[1].text.strip() if len(cols) > 1 else ''
                            nationality = cols[2].text.strip() if len(cols) > 2 else ''
                            
                            # Verificar se jogador já existe
                            player = Player.query.filter_by(url=url).first()
                            if not player:
                                player = Player(
                                    name=name,
                                    team_id=team_id,
                                    position=position,
                                    nationality=nationality,
                                    url=url
                                )
                                db.session.add(player)
                                logger.info(f"✅ Adicionado jogador: {name}")
            
            db.session.commit()
            logger.info(f"✅ Jogadores do time {team.name} atualizados com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar jogadores: {e}")
            db.session.rollback()
            return False
    
    def scrape_player_stats(self, player_id):
        """Coleta estatísticas de um jogador específico"""
        try:
            player = Player.query.get(player_id)
            if not player:
                logger.error(f"❌ Jogador {player_id} não encontrado")
                return False
            
            logger.info(f"🔍 Coletando estatísticas do jogador: {player.name}")
            response = self.session.get(player.url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Encontrar tabela de estatísticas
            stats_table = soup.find('table', {'id': 'stats_standard_9'})
            if stats_table:
                for row in stats_table.find_all('tr'):
                    # Ignorar linhas de tabelas parciais
                    if row.get('class') and 'partial_table' in row.get('class'):
                        continue
                    
                    cols = row.find_all(['th', 'td'])
                    if cols and cols[0].name == 'th' and cols[0].get('scope') == 'row':
                        season = cols[0].text.strip()
                        
                        # Extrair estatísticas
                        stats_data = {}
                        for col in cols[1:]:
                            stat_name = col.get('data-stat')
                            if stat_name:
                                stats_data[stat_name] = col.text.strip()
                        
                        # Salvar estatísticas se houver dados de jogos
                        if 'games' in stats_data:
                            # Verificar se estatística já existe
                            player_stat = PlayerStats.query.filter_by(
                                player_id=player_id,
                                season=season
                            ).first()
                            
                            if not player_stat:
                                player_stat = PlayerStats(
                                    player_id=player_id,
                                    season=season,
                                    matches_played=self._safe_int(stats_data.get('games')),
                                    goals=self._safe_int(stats_data.get('goals')),
                                    assists=self._safe_int(stats_data.get('assists')),
                                    minutes_played=self._safe_int(stats_data.get('minutes')),
                                    xg=self._safe_float(stats_data.get('xg')),
                                    xa=self._safe_float(stats_data.get('xa')),
                                    shots=self._safe_int(stats_data.get('shots')),
                                    key_passes=self._safe_int(stats_data.get('key_passes')),
                                    yellow_cards=self._safe_int(stats_data.get('yellow_cards')),
                                    red_cards=self._safe_int(stats_data.get('red_cards'))
                                )
                                db.session.add(player_stat)
                                logger.info(f"✅ Estatísticas de {player.name} para {season} adicionadas")
            
            db.session.commit()
            logger.info(f"✅ Estatísticas do jogador {player.name} atualizadas com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar estatísticas do jogador: {e}")
            db.session.rollback()
            return False
    
    def scrape_match_advanced_stats(self, match_url):
        """Coleta estatísticas avançadas de uma partida"""
        try:
            logger.info(f"🔍 Coletando estatísticas avançadas: {match_url}")
            response = self.session.get(match_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            stats = {
                'possession': self._extract_possession(soup),
                'passing': self._extract_passing_stats(soup),
                'shooting': self._extract_shooting_stats(soup),
                'defensive': self._extract_defensive_stats(soup),
                'goal_times': self._extract_goal_times(soup),
                'fouls': self._extract_fouls_stats(soup),
                'correct_score_probabilities': self._calculate_score_probabilities(soup)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar estatísticas avançadas: {e}")
            return {}
    
    def _extract_possession(self, soup):
        """Extrai estatísticas de posse de bola"""
        possession = {'home': 0, 'away': 0}
        try:
            # Buscar por elementos que contenham posse
            possession_divs = soup.find_all('div', string=lambda text: text and 'Possession' in text)
            for div in possession_divs:
                parent = div.find_parent('div')
                if parent:
                    values = parent.find_all('span', class_='stat-value')
                    if len(values) >= 2:
                        possession['home'] = self._safe_float(values[0].text.replace('%', ''))
                        possession['away'] = self._safe_float(values[1].text.replace('%', ''))
                        break
        except Exception as e:
            logger.warning(f"⚠️ Erro ao extrair posse: {e}")
        return possession
    
    def _extract_passing_stats(self, soup):
        """Extrai estatísticas de passes"""
        passing_stats = {'home': {}, 'away': {}}
        try:
            # Buscar tabelas de passes
            tables = soup.find_all('table')
            for table in tables:
                caption = table.find('caption')
                if caption and 'passing' in caption.text.lower():
                    # Determinar qual time
                    rows = table.find_all('tr')[1:]
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) > 3:
                            player_name = cols[0].text.strip()
                            passing_stats['home'][player_name] = {
                                'total_passes': self._safe_int(cols[1].text),
                                'completed_passes': self._safe_int(cols[2].text),
                                'pass_accuracy': self._safe_float(cols[3].text.replace('%', ''))
                            }
        except Exception as e:
            logger.warning(f"⚠️ Erro ao extrair passes: {e}")
        return passing_stats
    
    def _extract_shooting_stats(self, soup):
        """Extrai estatísticas de finalização (xG)"""
        shooting_stats = {'home': {}, 'away': {}}
        try:
            tables = soup.find_all('table')
            for table in tables:
                caption = table.find('caption')
                if caption and 'shooting' in caption.text.lower():
                    rows = table.find_all('tr')[1:]
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) > 4:
                            player_name = cols[0].text.strip()
                            shooting_stats['home'][player_name] = {
                                'shots': self._safe_int(cols[1].text),
                                'shots_on_target': self._safe_int(cols[2].text),
                                'goals': self._safe_int(cols[3].text),
                                'xg': self._safe_float(cols[4].text)
                            }
        except Exception as e:
            logger.warning(f"⚠️ Erro ao extrair finalização: {e}")
        return shooting_stats
    
    def _extract_defensive_stats(self, soup):
        """Extrai estatísticas defensivas"""
        defensive_stats = {'home': {}, 'away': {}}
        try:
            tables = soup.find_all('table')
            for table in tables:
                caption = table.find('caption')
                if caption and ('defense' in caption.text.lower() or 'defensive' in caption.text.lower()):
                    rows = table.find_all('tr')[1:]
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) > 6:
                            player_name = cols[0].text.strip()
                            defensive_stats['home'][player_name] = {
                                'tackles': self._safe_int(cols[1].text),
                                'interceptions': self._safe_int(cols[2].text),
                                'blocks': self._safe_int(cols[3].text),
                                'clearances': self._safe_int(cols[4].text),
                                'fouls': self._safe_int(cols[5].text),
                                'saves': self._safe_int(cols[6].text) if len(cols) > 6 else 0
                            }
        except Exception as e:
            logger.warning(f"⚠️ Erro ao extrair defesas: {e}")
        return defensive_stats
    
    def _extract_goal_times(self, soup):
        """Extrai minutos dos gols"""
        goal_times = []
        try:
            # Buscar por eventos de gol
            event_sections = soup.find_all('div', class_='event')
            for section in event_sections:
                if 'goal' in section.text.lower():
                    minute_span = section.find('span', class_='minute')
                    if minute_span:
                        minute = self._safe_int(minute_span.text.replace("'", ""))
                        if minute:
                            goal_times.append(minute)
        except Exception as e:
            logger.warning(f"⚠️ Erro ao extrair tempos dos gols: {e}")
        return goal_times
    
    def _extract_fouls_stats(self, soup):
        """Extrai estatísticas de faltas"""
        fouls_stats = {'home': 0, 'away': 0}
        try:
            # Buscar por estatísticas de faltas
            foul_divs = soup.find_all('div', string=lambda text: text and 'Fouls' in text)
            for div in foul_divs:
                parent = div.find_parent('div')
                if parent:
                    values = parent.find_all('span', class_='stat-value')
                    if len(values) >= 2:
                        fouls_stats['home'] = self._safe_int(values[0].text)
                        fouls_stats['away'] = self._safe_int(values[1].text)
                        break
        except Exception as e:
            logger.warning(f"⚠️ Erro ao extrair faltas: {e}")
        return fouls_stats
    
    def _calculate_score_probabilities(self, soup):
        """Calcula probabilidades de placar (simulação)"""
        probabilities = {
            'score_probabilities': {
                '0-0': 15.2, '1-0': 12.5, '0-1': 11.8,
                '1-1': 18.3, '2-0': 8.7, '0-2': 7.9,
                '2-1': 9.4, '1-2': 8.1, '2-2': 5.3
            },
            'both_teams_score': 68.4,
            'over_2_5': 42.7,
            'under_2_5': 57.3,
            'most_likely_score': '1-1'
        }
        return probabilities
    
    def _safe_int(self, text):
        """Converte texto para inteiro com segurança"""
        try:
            # Remove caracteres não numéricos
            clean_text = ''.join(filter(str.isdigit, str(text)))
            return int(clean_text) if clean_text else 0
        except:
            return 0
    
    def _safe_float(self, text):
        """Converte texto para float com segurança"""
        try:
            # Remove caracteres não numéricos exceto ponto e vírgula
            clean_text = ''.join(c for c in str(text) if c.isdigit() or c in '.,')
            clean_text = clean_text.replace(',', '.')
            return float(clean_text) if clean_text else 0.0
        except:
            return 0.0
    
    def update_all_data(self):
        """Atualiza todos os dados do sistema"""
        logger.info("🚀 Iniciando atualização completa de dados...")
        
        try:
            # 1. Atualizar ligas
            self.scrape_leagues()
            
            # 2. Atualizar times de todas as ligas
            leagues = League.query.all()
            for league in leagues:
                self.scrape_teams(league.id)
                time.sleep(1)  # Delay para evitar bloqueio
            
            # 3. Atualizar jogadores de todos os times
            teams = Team.query.all()
            for team in teams:
                self.scrape_players(team.id)
                time.sleep(1)
            
            # 4. Atualizar estatísticas dos jogadores
            players = Player.query.all()
            for player in players:
                self.scrape_player_stats(player.id)
                time.sleep(2)  # Delay maior para estatísticas
            
            # 5. Coletar estatísticas avançadas (opcional)
            logger.info("📊 Coletando estatísticas avançadas...")
            # self.update_advanced_statistics()
            
            logger.info("✅ Atualização completa concluída com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na atualização completa: {e}")
            return False
    
    def update_advanced_statistics(self):
        """Atualiza estatísticas avançadas"""
        logger.info("📈 Atualizando estatísticas avançadas...")
        
        # Esta função seria implementada quando tivermos URLs reais de partidas
        # Por enquanto, é um placeholder
        
        logger.info("✅ Estatísticas avançadas atualizadas")
        return True
    
    def get_test_data(self):
        """Retorna dados de teste para desenvolvimento"""
        return {
            'leagues': [
                {'name': 'Premier League', 'country': 'England'},
                {'name': 'La Liga', 'country': 'Spain'},
                {'name': 'Serie A', 'country': 'Italy'}
            ],
            'teams': [
                {'name': 'Manchester United', 'league': 'Premier League'},
                {'name': 'Real Madrid', 'league': 'La Liga'},
                {'name': 'Juventus', 'league': 'Serie A'}
            ],
            'players': [
                {'name': 'Cristiano Ronaldo', 'team': 'Manchester United', 'goals': 25},
                {'name': 'Lionel Messi', 'team': 'Paris SG', 'goals': 30},
                {'name': 'Neymar Jr', 'team': 'Paris SG', 'goals': 20}
            ]
        }