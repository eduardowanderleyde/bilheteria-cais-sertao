#!/usr/bin/env python3
"""
Script para limpeza COMPLETA do repositório Git
ATENCAO: Este script reescreve o historico Git permanentemente!
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def clean_repo_complete():
    """Limpeza COMPLETA do repositório"""
    
    print("ATENCAO: Este script ira reescrever o historico Git permanentemente!")
    print("Isso ira alterar todos os commits e pode afetar outros desenvolvedores.")
    print()
    
    # Verificar se git-filter-repo está instalado
    success, _, _ = run_command("git filter-repo --help")
    if not success:
        print("ERRO: git-filter-repo nao esta instalado.")
        print("Instale com: pip install git-filter-repo")
        return False
    
    # Criar diretório temporário
    temp_dir = Path(os.environ.get("TEMP", "/tmp")) / "bilheteria-clean"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)
    
    print(f"Trabalhando em: {temp_dir}")
    
    # 1. Clone espelhado (bare/mirror)
    print("\n1. Clonando repositório espelhado...")
    success, _, stderr = run_command(
        f"git clone --mirror https://github.com/eduardowanderleyde/bilheteria-cais-sertao.git",
        cwd=temp_dir
    )
    if not success:
        print(f"ERRO ao clonar: {stderr}")
        return False
    
    repo_dir = temp_dir / "bilheteria-cais-sertao.git"
    
    # 2. Reescrever o histórico removendo os ARQUIVOS
    print("\n2. Removendo arquivos com credenciais do histórico...")
    success, _, stderr = run_command(
        "git filter-repo --invert-paths --path seed_admin.py --path test_login.py --path run_server.py --path setup_env.py",
        cwd=repo_dir
    )
    if not success:
        print(f"ERRO ao limpar histórico: {stderr}")
        return False
    
    # 3. Force-push de volta (todas as branches e tags)
    print("\n3. Enviando histórico limpo para o repositório remoto...")
    success, _, stderr = run_command("git push origin --force --all", cwd=repo_dir)
    if not success:
        print(f"ERRO ao enviar branches: {stderr}")
        return False
    
    success, _, stderr = run_command("git push origin --force --tags", cwd=repo_dir)
    if not success:
        print(f"ERRO ao enviar tags: {stderr}")
        return False
    
    print("Histórico limpo enviado com sucesso!")
    
    # 4. Instruções para re-clonar
    print("\n4. Próximos passos:")
    print("   a) Re-clone o repositório em uma nova pasta:")
    print("      cd C:\\Users\\Eduardo\\Documents")
    print("      git clone https://github.com/eduardowanderleyde/bilheteria-cais-sertao.git")
    print("      cd bilheteria-cais-sertao")
    print()
    print("   b) Copie os arquivos limpos:")
    print("      copy seed_admin_clean.py seed_admin.py")
    print("      copy setup_env_clean.py setup_env.py")
    print("      copy test_login_clean.py test_login.py")
    print("      copy run_server_clean.py run_server.py")
    print()
    print("   c) Commit e push:")
    print("      git add seed_admin.py setup_env.py test_login.py run_server.py")
    print("      git commit -m \"chore(security): re-add sanitized files (env vars only)\"")
    print("      git push origin main")
    print()
    print("   d) Para outros clones existentes:")
    print("      git fetch --all")
    print("      git reset --hard origin/main")
    print("      git clean -fdx")
    
    # Limpar diretório temporário
    shutil.rmtree(temp_dir)
    
    return True

def main():
    """Função principal"""
    if len(sys.argv) > 1 and sys.argv[1] == "--confirm":
        clean_repo_complete()
    else:
        print("Para executar este script, use:")
        print("python clean_repo_complete.py --confirm")
        print()
        print("LEMBRE-SE: Faca backup do seu repositorio antes de executar!")
        print("Este script ira reescrever o historico Git permanentemente!")

if __name__ == "__main__":
    main()
