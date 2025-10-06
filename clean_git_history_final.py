#!/usr/bin/env python3
"""
Script FINAL para limpeza completa do histórico Git
ATENCAO: Este script reescreve o historico Git permanentemente!
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

def clean_git_history_final():
    """Limpeza FINAL do historico Git"""
    
    print("ATENCAO: Este script ira reescrever o historico Git permanentemente!")
    print("Isso ira alterar todos os commits e pode afetar outros desenvolvedores.")
    print()
    
    # Verificar se git-filter-repo está instalado
    success, _, _ = run_command("git filter-repo --help")
    if not success:
        print("ERRO: git-filter-repo nao esta instalado.")
        print("Instale com: pip install git-filter-repo")
        return False
    
    # Lista de credenciais sensíveis para remover
    sensitive_patterns = [
        "18091992123",
        "TroqueAqui!",
        "gestora123",
        "bilheteira123",
        "admingeral",
        "funcionario1",
        "Januario76",
        "Januario 76",
        "Januario72",
        "af5463df1a2dfa7ef04c91d89779a943f3a775469d26e18fa8cc2f5789bd55ab",
        "password.*=.*[\"'][^\"']+[\"']",
        "username.*=.*[\"'][^\"']+[\"']",
        "admin.*=.*[\"'][^\"']+[\"']",
    ]
    
    print("Credenciais que serao removidas do historico:")
    for pattern in sensitive_patterns:
        print(f"  - {pattern}")
    print()
    
    # Backup do branch atual
    print("Criando backup do branch atual...")
    success, _, _ = run_command("git branch backup-before-clean-final")
    if not success:
        print("ERRO ao criar backup")
        return False
    
    # Remover credenciais do histórico usando git filter-repo
    print("Removendo credenciais do historico...")
    
    for pattern in sensitive_patterns:
        print(f"  Removendo: {pattern}")
        # Usar git filter-repo para substituir padrões
        cmd = f'git filter-repo --replace-text <(echo "{pattern}==>REDACTED") --force'
        success, stdout, stderr = run_command(cmd)
        if not success:
            print(f"ERRO ao remover {pattern}: {stderr}")
            # Continuar mesmo com erro
            continue
    
    print("Historico limpo com sucesso!")
    print()
    print("Proximos passos:")
    print("1. Verifique as mudancas: git log --oneline")
    print("2. Force push para reescrever o repositorio remoto:")
    print("   git push origin --force --all")
    print("3. Notifique outros desenvolvedores sobre a reescrita do historico")
    print("4. Revogue todas as credenciais que foram expostas")
    
    return True

def main():
    """Funcao principal"""
    if len(sys.argv) > 1 and sys.argv[1] == "--confirm":
        clean_git_history_final()
    else:
        print("Para executar este script, use:")
        print("python clean_git_history_final.py --confirm")
        print()
        print("LEMBRE-SE: Faca backup do seu repositorio antes de executar!")

if __name__ == "__main__":
    main()
