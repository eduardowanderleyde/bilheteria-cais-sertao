# test_web.py
# Teste simples da aplicação web

import requests
import time
import subprocess
import sys
import os

def test_web_app():
    """Testa se a aplicação web está funcionando"""
    print("Testando aplicacao web...")
    
    # Inicia o servidor em background
    print("Iniciando servidor...")
    process = subprocess.Popen([sys.executable, "run_web.py"], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
    
    # Aguarda o servidor inicializar
    print("Aguardando servidor inicializar...")
    time.sleep(5)
    
    try:
        # Testa se o servidor está respondendo
        response = requests.get("http://127.0.0.1:8000", timeout=10)
        if response.status_code == 200:
            print("SUCESSO: Servidor web esta funcionando!")
            print("Acesse: http://127.0.0.1:8000")
            print("Usuario: funcionario1")
            print("Senha: 123456")
            return True
        else:
            print(f"ERRO: Servidor retornou status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"ERRO: Nao foi possivel conectar ao servidor: {e}")
        return False
    finally:
        # Para o servidor
        process.terminate()
        process.wait()

if __name__ == "__main__":
    test_web_app()
