# deploy_example.py
# Exemplo de deploy para produção

import os
import subprocess
import sys
from config import ProductionConfig

def deploy_to_production():
    """Exemplo de deploy para produção"""
    print("🚀 Deploy para Produção - Sistema de Bilheteria")
    print("=" * 50)
    
    # 1. Verificar ambiente
    print("1️⃣ Verificando ambiente...")
    if os.getenv("ENV") != "production":
        print("⚠️  Definindo ENV=production")
        os.environ["ENV"] = "production"
    
    # 2. Instalar dependências
    print("\n2️⃣ Instalando dependências de produção...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        print("✅ Dependências instaladas")
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar dependências")
        return False
    
    # 3. Configurar banco de dados
    print("\n3️⃣ Configurando banco de dados...")
    config = ProductionConfig()
    print(f"   Banco: {config.DATABASE_URL}")
    print(f"   Host: {config.HOST}")
    print(f"   Porta: {config.PORT}")
    
    # 4. Criar diretórios necessários
    print("\n4️⃣ Criando diretórios...")
    dirs = ["templates", "static", "temp", "logs"]
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
        print(f"   ✅ {dir_name}")
    
    # 5. Configurar logs
    print("\n5️⃣ Configurando logs...")
    log_config = """
# logging.conf
[loggers]
keys=root,uvicorn

[handlers]
keys=default,file

[formatters]
keys=default

[logger_root]
level=INFO
handlers=default

[logger_uvicorn]
level=INFO
handlers=file
qualname=uvicorn
propagate=0

[handler_default]
class=StreamHandler
formatter=default
args=(sys.stdout,)

[handler_file]
class=FileHandler
formatter=default
args=('logs/bilheteria.log',)

[formatter_default]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
"""
    
    with open("logging.conf", "w") as f:
        f.write(log_config)
    print("   ✅ logging.conf criado")
    
    # 6. Criar script de inicialização
    print("\n6️⃣ Criando script de inicialização...")
    startup_script = f"""#!/bin/bash
# startup.sh - Script de inicialização para produção

export ENV=production
export HOST={config.HOST}
export PORT={config.PORT}

# Iniciar servidor
python -m uvicorn web_app:app --host {config.HOST} --port {config.PORT} --log-config logging.conf
"""
    
    with open("startup.sh", "w") as f:
        f.write(startup_script)
    print("   ✅ startup.sh criado")
    
    # 7. Criar Dockerfile (opcional)
    print("\n7️⃣ Criando Dockerfile...")
    dockerfile = """FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Criar diretórios
RUN mkdir -p templates static temp logs

# Expor porta
EXPOSE 8000

# Comando de inicialização
CMD ["python", "-m", "uvicorn", "web_app:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    
    with open("Dockerfile", "w") as f:
        f.write(dockerfile)
    print("   ✅ Dockerfile criado")
    
    # 8. Criar docker-compose.yml
    print("\n8️⃣ Criando docker-compose.yml...")
    docker_compose = """version: '3.8'

services:
  bilheteria:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./bilheteria.db:/app/bilheteria.db
      - ./logs:/app/logs
    environment:
      - ENV=production
    restart: unless-stopped
"""
    
    with open("docker-compose.yml", "w") as f:
        f.write(docker_compose)
    print("   ✅ docker-compose.yml criado")
    
    # 9. Instruções de deploy
    print("\n" + "=" * 50)
    print("🎉 Configuração de produção concluída!")
    print("\n📋 Opções de deploy:")
    print("\n1️⃣ Deploy Local:")
    print("   python -m uvicorn web_app:app --host 0.0.0.0 --port 8000")
    
    print("\n2️⃣ Deploy com Docker:")
    print("   docker-compose up -d")
    
    print("\n3️⃣ Deploy em Servidor:")
    print("   - Copie todos os arquivos para o servidor")
    print("   - Execute: chmod +x startup.sh")
    print("   - Execute: ./startup.sh")
    
    print("\n4️⃣ Deploy em Cloud (Render/Railway):")
    print("   - Conecte o repositório Git")
    print("   - Configure ENV=production")
    print("   - Configure PORT=8000")
    print("   - Deploy automático")
    
    print("\n🔧 Configurações de produção:")
    print(f"   Host: {config.HOST}")
    print(f"   Porta: {config.PORT}")
    print(f"   Banco: {config.DATABASE_URL}")
    print("   Logs: logs/bilheteria.log")
    
    print("\n⚠️  Lembre-se de:")
    print("   - Fazer backup do banco de dados")
    print("   - Configurar firewall se necessário")
    print("   - Monitorar logs de erro")
    print("   - Configurar SSL/HTTPS em produção")
    
    return True

if __name__ == "__main__":
    deploy_to_production()
