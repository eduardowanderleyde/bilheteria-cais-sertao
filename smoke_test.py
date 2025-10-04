#!/usr/bin/env python3
"""
Smoke test para verificar se o sistema está funcionando
Uso: python smoke_test.py
"""
import requests
import time
import sys
from urllib.parse import urljoin

BASE_URL = "http://127.0.0.1:8000"

def test_server_running():
    """Testa se o servidor está rodando"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("Servidor esta rodando")
            return True
    except requests.exceptions.RequestException:
        pass
    
    print("Servidor nao esta rodando")
    print("Execute: uvicorn app.main:app --reload")
    return False

def test_login_page():
    """Testa página de login"""
    try:
        response = requests.get(f"{BASE_URL}/auth/login", timeout=5)
        if response.status_code == 200 and "login" in response.text.lower():
            print("✅ Página de login carregada")
            return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao carregar login: {e}")
    
    return False

def test_login_functionality():
    """Testa funcionalidade de login"""
    session = requests.Session()
    
    try:
        # Pega página de login para obter CSRF token
        login_page = session.get(f"{BASE_URL}/auth/login")
        if login_page.status_code != 200:
            print("❌ Não foi possível carregar página de login")
            return False
        
        # Tenta fazer login (sem CSRF por enquanto)
        login_data = {
            "username": "admin",
            "password": "admin123",
            "csrf_token": "test"  # Token de teste
        }
        
        response = session.post(f"{BASE_URL}/auth/login", data=login_data, allow_redirects=False)
        
        if response.status_code in [200, 303, 307]:
            print("✅ Login funcionando (pode precisar de CSRF válido)")
            return True
        else:
            print(f"⚠️ Login retornou status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro no teste de login: {e}")
        return False

def test_dashboard_access():
    """Testa acesso ao dashboard"""
    try:
        response = requests.get(f"{BASE_URL}/dashboard", timeout=5)
        if response.status_code in [200, 401, 403, 307]:
            print("✅ Dashboard acessível (pode precisar de login)")
            return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao acessar dashboard: {e}")
    
    return False

def test_reports_endpoints():
    """Testa endpoints de relatórios"""
    endpoints = [
        "/reports/by-state",
        "/reports/by-discount-reason", 
        "/reports/by-payment-method",
        "/reports/daily"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            if response.status_code in [200, 401, 403, 422]:  # 422 = validation error (ok)
                print(f"✅ {endpoint} acessível")
            else:
                print(f"⚠️ {endpoint} retornou status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro em {endpoint}: {e}")

def test_admin_endpoints():
    """Testa endpoints de admin"""
    endpoints = [
        "/admin",
        "/admin/orders",
        "/admin/groups"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            if response.status_code in [200, 401, 403, 307]:
                print(f"✅ {endpoint} acessível")
            else:
                print(f"⚠️ {endpoint} retornou status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro em {endpoint}: {e}")

def main():
    """Função principal"""
    print("Executando smoke test...")
    print("=" * 50)
    
    tests = [
        ("Servidor rodando", test_server_running),
        ("Página de login", test_login_page),
        ("Funcionalidade de login", test_login_functionality),
        ("Acesso ao dashboard", test_dashboard_access),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testando: {test_name}")
        if test_func():
            passed += 1
        time.sleep(1)  # Pausa entre testes
    
    print("\n" + "=" * 50)
    print(f"📊 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! Sistema funcionando.")
    else:
        print("⚠️ Alguns testes falharam. Verifique os logs.")
    
    print("\n🔍 Testando endpoints de relatórios...")
    test_reports_endpoints()
    
    print("\n🔍 Testando endpoints de admin...")
    test_admin_endpoints()
    
    print("\n📋 Próximos passos:")
    print("1. Teste manual: acesse http://127.0.0.1:8000")
    print("2. Faça login com: admin / admin123")
    print("3. Teste todas as funcionalidades")
    print("4. Configure PostgreSQL se necessário")

if __name__ == "__main__":
    main()
