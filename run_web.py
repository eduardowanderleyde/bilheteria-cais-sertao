# run_web.py
# Script para executar a versão web localmente

import uvicorn

if __name__ == "__main__":
    print("Iniciando servidor web...")
    print("Acesse: http://127.0.0.1:8000")
    print("Pressione Ctrl+C para parar o servidor")
    
    uvicorn.run("web_app:app", host="127.0.0.1", port=8000, reload=True)
