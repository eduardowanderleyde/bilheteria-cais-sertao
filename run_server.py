#!/usr/bin/env python3
"""Script simples para rodar o servidor"""

import os
import uvicorn

# Configurar variáveis de ambiente
os.environ["SECURE_COOKIES"] = "false"
os.environ["SECRET_KEY"] = "af5463df1a2dfa7ef04c91d89779a943f3a775469d26e18fa8cc2f5789bd55ab"

if __name__ == "__main__":
    print("Iniciando servidor...")
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
