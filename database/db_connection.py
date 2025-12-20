from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
import MySQLdb
import os

# Inicializar SQLAlchemy
db = SQLAlchemy()

# Inicializar Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'

def get_db_connection():
    """
    Estabelece conexão direta com MySQL
    Para uso em queries SQL diretas quando necessário
    """
    try:
        connection = MySQLdb.connect(
            host=os.environ.get('DB_HOST') or 'localhost',
            user=os.environ.get('DB_USER') or 'root',
            password=os.environ.get('DB_PASSWORD') or '',
            database=os.environ.get('DB_NAME') or 'futebol_analytics',
            charset='utf8mb4',
            autocommit=True
        )
        return connection
    except Exception as e:
        print(f"❌ Erro ao conectar com o banco de dados: {e}")
        return None

def test_connection():
    """Testa a conexão com o banco de dados"""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result is not None
    except Exception as e:
        print(f"❌ Teste de conexão falhou: {e}")
        return False