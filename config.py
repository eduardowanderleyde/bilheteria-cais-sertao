# config.py
# Configurações do Sistema de Bilheteria

import os
from typing import Dict, Any

class Config:
    """Configurações gerais do sistema"""
    
    # Banco de dados
    DATABASE_URL = "bilheteria.db"
    
    # Servidor web
    HOST = "127.0.0.1"
    PORT = 8000
    
    # Preços dos ingressos (em centavos)
    PRICES = {
        "inteira": 1000,    # R$ 10,00
        "meia": 500,        # R$ 5,00
        "gratuita": 0       # R$ 0,00
    }
    
    # Tipos de ingresso
    TICKET_TYPES = ["inteira", "meia", "gratuita"]
    
    # Usuário padrão
    DEFAULT_USER = {
        "username": "funcionario1",
        "password": "123456",
        "role": "operator"
    }
    
    # Configurações de relatórios
    REPORTS = {
        "max_days": 30,  # Máximo de dias no resumo
        "auto_refresh": 30,  # Atualização automática (segundos)
        "export_format": "xlsx"
    }
    
    # Configurações de segurança
    SECURITY = {
        "session_timeout": 3600,  # 1 hora em segundos
        "max_login_attempts": 5,
        "password_min_length": 6
    }
    
    # Configurações de interface
    UI = {
        "theme": "light",  # light, dark
        "language": "pt-BR",
        "currency": "BRL"
    }
    
    # Configurações de backup
    BACKUP = {
        "auto_backup": True,
        "backup_interval": 24,  # horas
        "max_backups": 7  # dias
    }

class DevelopmentConfig(Config):
    """Configurações para desenvolvimento"""
    DEBUG = True
    HOST = "127.0.0.1"
    PORT = 8000

class ProductionConfig(Config):
    """Configurações para produção"""
    DEBUG = False
    HOST = "0.0.0.0"
    PORT = int(os.getenv("PORT", 8000))

# Configuração ativa baseada no ambiente
config = DevelopmentConfig if os.getenv("ENV") != "production" else ProductionConfig

def get_config() -> Dict[str, Any]:
    """Retorna configurações como dicionário"""
    return {
        "database_url": config.DATABASE_URL,
        "host": config.HOST,
        "port": config.PORT,
        "prices": config.PRICES,
        "ticket_types": config.TICKET_TYPES,
        "default_user": config.DEFAULT_USER,
        "reports": config.REPORTS,
        "security": config.SECURITY,
        "ui": config.UI,
        "backup": config.BACKUP,
        "debug": getattr(config, 'DEBUG', False)
    }

# Função para obter preço formatado
def format_price(price_cents: int) -> str:
    """Formata preço em centavos para string"""
    return f"R$ {price_cents / 100:.2f}"

# Função para obter preço por tipo
def get_price(ticket_type: str) -> int:
    """Retorna preço em centavos para o tipo de ingresso"""
    return config.PRICES.get(ticket_type, 0)

# Função para validar tipo de ingresso
def is_valid_ticket_type(ticket_type: str) -> bool:
    """Valida se o tipo de ingresso é válido"""
    return ticket_type in config.TICKET_TYPES
