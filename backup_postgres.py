#!/usr/bin/env python3
"""
Script de backup para PostgreSQL
Uso: python backup_postgres.py
"""
import os
import subprocess
import datetime
from pathlib import Path

def create_backup():
    """Cria backup do banco PostgreSQL"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ Variável DATABASE_URL não configurada")
        return False
    
    # Gera nome do arquivo de backup
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_bilheteria_{timestamp}.sql"
    
    try:
        print(f"📦 Criando backup: {backup_file}")
        
        # Executa pg_dump
        cmd = ["pg_dump", database_url, "-f", backup_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Backup criado: {backup_file}")
            
            # Mostra tamanho do arquivo
            file_size = Path(backup_file).stat().st_size
            print(f"📊 Tamanho: {file_size / 1024:.1f} KB")
            
            return True
        else:
            print(f"❌ Erro no backup: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ pg_dump não encontrado. Instale PostgreSQL client tools.")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def restore_backup(backup_file):
    """Restaura backup do banco PostgreSQL"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ Variável DATABASE_URL não configurada")
        return False
    
    if not Path(backup_file).exists():
        print(f"❌ Arquivo de backup não encontrado: {backup_file}")
        return False
    
    try:
        print(f"🔄 Restaurando backup: {backup_file}")
        
        # Executa psql
        cmd = ["psql", database_url, "-f", backup_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Backup restaurado com sucesso")
            return True
        else:
            print(f"❌ Erro na restauração: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ psql não encontrado. Instale PostgreSQL client tools.")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def list_backups():
    """Lista arquivos de backup disponíveis"""
    backup_files = list(Path(".").glob("backup_bilheteria_*.sql"))
    
    if not backup_files:
        print("📭 Nenhum backup encontrado")
        return
    
    print("📋 Backups disponíveis:")
    for backup_file in sorted(backup_files, reverse=True):
        file_size = backup_file.stat().st_size
        mod_time = datetime.datetime.fromtimestamp(backup_file.stat().st_mtime)
        print(f"  {backup_file.name} ({file_size / 1024:.1f} KB) - {mod_time.strftime('%Y-%m-%d %H:%M')}")

def main():
    """Função principal"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create":
            create_backup()
        elif command == "restore":
            if len(sys.argv) > 2:
                restore_backup(sys.argv[2])
            else:
                print("❌ Especifique o arquivo de backup: python backup_postgres.py restore backup_file.sql")
        elif command == "list":
            list_backups()
        else:
            print("❌ Comando inválido. Use: create, restore, ou list")
    else:
        print("🗄️ Script de backup PostgreSQL")
        print("\nComandos disponíveis:")
        print("  python backup_postgres.py create    - Criar backup")
        print("  python backup_postgres.py list      - Listar backups")
        print("  python backup_postgres.py restore   - Restaurar backup")
        print("\nExemplo:")
        print("  python backup_postgres.py restore backup_bilheteria_20241203_143022.sql")

if __name__ == "__main__":
    main()
