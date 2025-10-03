#!/usr/bin/env python3
"""
Teste simples para verificar se o sistema está funcionando
"""
import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test_server():
    """Testa se o servidor está rodando"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("OK: Servidor rodando")
            return True
    except:
        pass
    
    print("ERRO: Servidor nao esta rodando")
    return False

def test_login_page():
    """Testa página de login"""
    try:
        response = requests.get(f"{BASE_URL}/auth/login", timeout=5)
        if response.status_code == 200:
            print("OK: Pagina de login carregada")
            return True
    except Exception as e:
        print(f"ERRO: Login page - {e}")
    
    return False

def test_dashboard():
    """Testa dashboard"""
    try:
        response = requests.get(f"{BASE_URL}/dashboard", timeout=5)
        if response.status_code in [200, 401, 403, 307]:
            print("OK: Dashboard acessivel")
            return True
    except Exception as e:
        print(f"ERRO: Dashboard - {e}")
    
    return False

def main():
    print("Testando sistema...")
    print("-" * 30)
    
    tests = [
        ("Servidor", test_server),
        ("Login", test_login_page),
        ("Dashboard", test_dashboard),
    ]
    
    passed = 0
    for name, test_func in tests:
        print(f"Testando {name}...")
        if test_func():
            passed += 1
        time.sleep(1)
    
    print("-" * 30)
    print(f"Resultado: {passed}/{len(tests)} testes passaram")
    
    if passed == len(tests):
        print("SUCESSO: Sistema funcionando!")
    else:
        print("ATENCAO: Alguns testes falharam")
    
    print("\nAcesse: http://127.0.0.1:8000")
    print("Login: ***REMOVED*** / ***REMOVED***")

if __name__ == "__main__":
    main()
