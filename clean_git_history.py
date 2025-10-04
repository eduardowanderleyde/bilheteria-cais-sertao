#!/usr/bin/env python3
"""
Script para limpar credenciais do histórico Git
ATENÇÃO: Este script reescreve o histórico Git permanentemente!
"""

import subprocess
import sys
import os

def run_command(cmd):
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def clean_git_history():
    """Limpa credenciais do histórico Git"""
    
    print("⚠️  ATENÇÃO: Este script irá reescrever o histórico Git permanentemente!")
    print("Isso irá alterar todos os commits e pode afetar outros desenvolvedores.")
    print()
    
    # Lista de credenciais sensíveis para remover
    sensitive_patterns = [
        "18091992123",
        "***REMOVED***",
        "gestora123",
        "bilheteira123",
        "***REMOVED***",
        "funcionario1",
        "***REMOVED***",
        "Januario 76",
        "Januario72"
    ]
    
    print("Credenciais que serão removidas do histórico:")
    for pattern in sensitive_patterns:
        print(f"  - {pattern}")
    print()
    
    # Verificar se git-filter-repo está instalado
    success, _, _ = run_command("git filter-repo --help")
    if not success:
        print("❌ git-filter-repo não está instalado.")
        print("Instale com: pip install git-filter-repo")
        return False
    
    # Backup do branch atual
    print("📦 Criando backup do branch atual...")
    success, _, _ = run_command("git branch backup-before-clean")
    if not success:
        print("❌ Erro ao criar backup")
        return False
    
    # Remover credenciais do histórico
    print("🧹 Removendo credenciais do histórico...")
    
    for pattern in sensitive_patterns:
        print(f"  Removendo: {pattern}")
        cmd = f'git filter-repo --replace-text <(echo "{pattern}==>REDACTED") --force'
        success, stdout, stderr = run_command(cmd)
        if not success:
            print(f"❌ Erro ao remover {pattern}: {stderr}")
            return False
    
    print("✅ Histórico limpo com sucesso!")
    print()
    print("Próximos passos:")
    print("1. Verifique as mudanças: git log --oneline")
    print("2. Force push para reescrever o repositório remoto:")
    print("   git push origin --force --all")
    print("3. Notifique outros desenvolvedores sobre a reescrita do histórico")
    
    return True

def main():
    """Função principal"""
    if len(sys.argv) > 1 and sys.argv[1] == "--confirm":
        clean_git_history()
    else:
        print("Para executar este script, use:")
        print("python clean_git_history.py --confirm")
        print()
        print("⚠️  LEMBRE-SE: Faça backup do seu repositório antes de executar!")

if __name__ == "__main__":
    main()
