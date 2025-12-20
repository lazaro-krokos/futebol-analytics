import schedule
import time
import logging
from datetime import datetime
from .fbref_scraper import FBRefScraper

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def daily_update():
    """Executa atualização diária dos dados"""
    logger.info(f"🔄 Iniciando atualização diária em {datetime.now()}")
    try:
        scraper = FBRefScraper()
        
        # Executar atualização básica
        success = scraper.update_all_data()
        
        if success:
            logger.info("✅ Atualização diária concluída com sucesso")
        else:
            logger.error("❌ Atualização diária falhou")
            
    except Exception as e:
        logger.error(f"❌ Erro na atualização diária: {e}")

def weekly_update():
    """Executa atualização semanal mais completa"""
    logger.info(f"🔄 Iniciando atualização semanal em {datetime.now()}")
    try:
        scraper = FBRefScraper()
        
        # Atualização básica
        scraper.update_all_data()
        
        # Atualização avançada (estatísticas detalhadas)
        scraper.update_advanced_statistics()
        
        logger.info("✅ Atualização semanal concluída com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro na atualização semanal: {e}")

def manual_update():
    """Executa atualização manual"""
    logger.info(f"🔧 Executando atualização manual em {datetime.now()}")
    try:
        scraper = FBRefScraper()
        success = scraper.update_all_data()
        
        if success:
            logger.info("✅ Atualização manual concluída com sucesso")
            return True
        else:
            logger.error("❌ Atualização manual falhou")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro na atualização manual: {e}")
        return False

def test_scraper():
    """Testa o scraper"""
    logger.info("🧪 Testando scraper...")
    try:
        scraper = FBRefScraper()
        test_data = scraper.get_test_data()
        
        logger.info(f"✅ Teste concluído. Dados de teste: {len(test_data['leagues'])} ligas, {len(test_data['teams'])} times, {len(test_data['players'])} jogadores")
        return True
    except Exception as e:
        logger.error(f"❌ Teste falhou: {e}")
        return False

def run_scheduler():
    """Executa o agendador de tarefas"""
    logger.info("⏰ Agendador iniciado")
    
    # Agendar atualização diária às 2h da manhã
    schedule.every().day.at("02:00").do(daily_update)
    
    # Agendar atualização semanal às 4h de domingo
    schedule.every().sunday.at("04:00").do(weekly_update)
    
    # Agendar teste diário às 6h
    schedule.every().day.at("06:00").do(test_scraper)
    
    logger.info("📅 Agendamentos configurados:")
    logger.info("  - Atualização diária: 02:00")
    logger.info("  - Atualização semanal: Domingo 04:00")
    logger.info("  - Teste diário: 06:00")
    
    # Executar manualmente na primeira vez
    logger.info("🔧 Executando primeira atualização...")
    manual_update()
    
    # Loop principal
    while True:
        schedule.run_pending()
        time.sleep(60)  # Verificar a cada minuto

if __name__ == "__main__":
    run_scheduler()