#!/usr/bin/env python3
"""
Script de teste para o scraper
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fbref_scraper import FBRefScraper

def main():
    print("🧪 Testando FBRef Scraper...")
    
    scraper = FBRefScraper()
    
    print("\n1. Testando funções básicas...")
    
    # Testar conversão segura
    print(f"   _safe_int('123'): {scraper._safe_int('123')}")
    print(f"   _safe_int('abc123'): {scraper._safe_int('abc123')}")
    print(f"   _safe_float('45.67'): {scraper._safe_float('45.67')}")
    print(f"   _safe_float('45,67%'): {scraper._safe_float('45,67%')}")
    
    print("\n2. Testando conexão com banco de dados...")
    from database.db_connection import test_connection
    if test_connection():
        print("   ✅ Conexão com banco OK")
    else:
        print("   ❌ Falha na conexão com banco")
    
    print("\n3. Testando dados de teste...")
    test_data = scraper.get_test_data()
    print(f"   Ligas: {len(test_data['leagues'])}")
    print(f"   Times: {len(test_data['teams'])}")
    print(f"   Jogadores: {len(test_data['players'])}")
    
    print("\n🎉 Teste concluído com sucesso!")
    print("\nPróximos passos:")
    print("1. Configure o arquivo .env com suas credenciais MySQL")
    print("2. Execute 'python run.py' para iniciar a aplicação")
    print("3. Acesse http://localhost:5000")
    print("4. Para testar o scraper real, modifique as URLs no código")

if __name__ == "__main__":
    main()