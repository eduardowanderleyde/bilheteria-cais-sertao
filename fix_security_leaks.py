#!/usr/bin/env python3
"""
Script para corrigir vazamentos de segurança de forma definitiva
"""

import os
import re
import subprocess
import sys
from pathlib import Path

# Lista de padrões sensíveis para remover
SENSITIVE_PATTERNS = [
    r'18091992123',
    r'***REMOVED***',
    r'gestora123',
    r'bilheteira123',
    r'***REMOVED***',
    r'funcionario1',
    r'***REMOVED***',
    r'Januario 76',
    r'Januario72',
    r'af5463df1a2dfa7ef04c91d89779a943f3a775469d26e18fa8cc2f5789bd55ab',
    r'password.*=.*["\'][^"\']+["\']',
    r'username.*=.*["\'][^"\']+["\']',
    r'admin.*=.*["\'][^"\']+["\']',
]

def find_sensitive_files():
    """Encontra arquivos com credenciais sensíveis"""
    sensitive_files = []
    
    for pattern in SENSITIVE_PATTERNS:
        try:
            result = subprocess.run(
                f'grep -r -l "{pattern}" . --exclude-dir=.git --exclude-dir=__pycache__ --exclude="*.pyc"',
                shell=True, capture_output=True, text=True
            )
            if result.returncode == 0:
                files = result.stdout.strip().split('\n')
                sensitive_files.extend(files)
        except:
            pass
    
    return list(set(sensitive_files))

def create_secure_env_example():
    """Cria arquivo .env.example seguro"""
    env_content = """# Database Configuration
DATABASE_URL=sqlite:///./bilheteria.db
# Para PostgreSQL: DATABASE_URL=postgresql://user:password@localhost:5432/bilheteria

# Security (OBRIGATÓRIO em produção)
SECRET_KEY=your-secret-key-here-generate-with-secrets-token-hex-32

# Admin User (created by seed_admin.py)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=CHANGE_ME_SECURE_PASSWORD_123!

# Other Users
GESTORA_PASSWORD=CHANGE_ME_GESTORA_PASSWORD_123!
BILHETEIRA_PASSWORD=CHANGE_ME_BILHETEIRA_PASSWORD_123!

# Test Credentials
TEST_USERNAME=admin
TEST_PASSWORD=CHANGE_ME_TEST_PASSWORD_123!

# Application Settings
DEBUG=True
HOST=127.0.0.1
PORT=8000
SECURE_COOKIES=false
"""
    
    with open(".env.example", "w") as f:
        f.write(env_content)
    
    print("Arquivo .env.example criado com configuracoes seguras")

def create_git_hooks():
    """Cria hooks do Git para prevenir vazamentos futuros"""
    hooks_dir = Path(".git/hooks")
    hooks_dir.mkdir(exist_ok=True)
    
    pre_commit_hook = """#!/bin/bash
# Pre-commit hook para verificar credenciais sensiveis

echo "Verificando credenciais sensiveis..."

# Lista de padroes proibidos
PATTERNS=(
    "password.*=.*[\"'][^\"']+[\"']"
    "username.*=.*[\"'][^\"']+[\"']"
    "admin.*=.*[\"'][^\"']+[\"']"
    "secret.*=.*[\"'][^\"']+[\"']"
    "key.*=.*[\"'][^\"']+[\"']"
    "token.*=.*[\"'][^\"']+[\"']"
)

# Verificar arquivos staged
for pattern in "${PATTERNS[@]}"; do
    if git diff --cached --name-only | xargs grep -l "$pattern" 2>/dev/null; then
        echo "ERRO: Credenciais sensiveis detectadas!"
        echo "Use variaveis de ambiente em vez de valores hardcoded."
        echo "Padrao encontrado: $pattern"
        exit 1
    fi
done

echo "Nenhuma credencial sensivel detectada"
exit 0
"""
    
    with open(hooks_dir / "pre-commit", "w") as f:
        f.write(pre_commit_hook)
    
    # Tornar executável
    os.chmod(hooks_dir / "pre-commit", 0o755)
    
    print("Hook pre-commit criado para prevenir vazamentos futuros")

def create_security_readme():
    """Cria README de segurança"""
    security_readme = """# Guia de Seguranca

## IMPORTANTE: Credenciais Sensiveis

Este projeto NAO deve conter credenciais hardcoded no codigo.

### Como usar credenciais de forma segura:

1. Use variaveis de ambiente:
   ```python
   import os
   username = os.getenv("ADMIN_USERNAME")
   password = os.getenv("ADMIN_PASSWORD")
   ```

2. Configure no arquivo .env (nao versionado):
   ```bash
   cp .env.example .env
   # Edite .env com suas credenciais
   ```

3. Para producao (Render/Heroku):
   - Configure variaveis de ambiente no painel
   - NUNCA commite arquivos .env

### Credenciais que DEVEM ser trocadas:

- ADMIN_PASSWORD
- GESTORA_PASSWORD  
- BILHETEIRA_PASSWORD
- TEST_PASSWORD
- SECRET_KEY

### Scripts de configuracao:

```bash
# Configurar ambiente local
python setup_env.py

# Criar usuarios no banco
python seed_admin.py

# Testar sistema
python test_login.py
```

### Checklist de seguranca:

- [ ] Nenhuma senha hardcoded no codigo
- [ ] Variaveis de ambiente configuradas
- [ ] Arquivo .env no .gitignore
- [ ] Credenciais de producao diferentes das de desenvolvimento
- [ ] SECRET_KEY forte e unica
- [ ] Hooks pre-commit ativados
"""
    
    with open("SECURITY.md", "w") as f:
        f.write(security_readme)
    
    print("Guia de seguranca criado (SECURITY.md)")

def main():
    """Função principal"""
    print("Corrigindo vazamentos de seguranca...")
    
    # 1. Encontrar arquivos sensíveis
    print("\n1. Procurando arquivos com credenciais sensíveis...")
    sensitive_files = find_sensitive_files()
    
    if sensitive_files:
        print(f"   ATENCAO: Encontrados {len(sensitive_files)} arquivos com credenciais:")
        for file in sensitive_files:
            print(f"   - {file}")
        print("\n   Execute: python clean_git_history.py --confirm")
        print("   para remover do historico Git")
    else:
        print("   Nenhum arquivo com credenciais sensiveis encontrado")
    
    # 2. Criar arquivos de configuração seguros
    print("\n2. Criando arquivos de configuração seguros...")
    create_secure_env_example()
    create_git_hooks()
    create_security_readme()
    
    # 3. Instruções finais
    print("\n3. Proximos passos:")
    print("   Configure suas credenciais no arquivo .env")
    print("   Execute: python clean_git_history.py --confirm")
    print("   Force push: git push origin --force --all")
    print("   Revogue credenciais expostas anteriormente")
    
    print("\nCorrecao de seguranca concluida!")

if __name__ == "__main__":
    main()
