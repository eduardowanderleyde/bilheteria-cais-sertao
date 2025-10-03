#!/usr/bin/env python3
"""Script simples para rodar o servidor"""

import os
import uvicorn
import secrets

# Configurar variáveis de ambiente
os.environ["SECURE_COOKIES"] = "false"

# Gerar SECRET_KEY se não estiver definida
if not os.getenv("SECRET_KEY"):
    os.environ["SECRET_KEY"] = secrets.token_hex(32)
    print("⚠️  SECRET_KEY gerada automaticamente. Para produção, defina SECRET_KEY nas variáveis de ambiente.")

if __name__ == "__main__":
    print("Iniciando servidor...")
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
