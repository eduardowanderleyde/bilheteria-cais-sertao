#!/usr/bin/env python3
"""Teste simples de login"""

import requests
import re
import os

def test_login():
    """Testa o login"""
    base_url = "http://127.0.0.1:8000"
    
    # 1) GET /auth/login (pega cookie + CSRF)
    print("1. Acessando página de login...")
    try:
        session = requests.Session()
        r = session.get(f"{base_url}/auth/login")
        print(f"   Status: {r.status_code}")
        
        if r.status_code != 200:
            print(f"   Erro: {r.text}")
            return
            
        # Extrai CSRF token
        csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', r.text)
        if not csrf_match:
            print("   Erro: CSRF token não encontrado")
            return
            
        csrf_token = csrf_match.group(1)
        print(f"   CSRF Token: {csrf_token[:20]}...")
        
    except Exception as e:
        print(f"   Erro na requisição: {e}")
        return
    
    # 2) POST /auth/login (usa o MESMO cookie e o MESMO token)
    print("\n2. Fazendo login...")
    try:
        # Get credentials from environment variables
        username = os.getenv("TEST_USERNAME", "admingeral")
        password = os.getenv("TEST_PASSWORD")
        
        if not password:
            print("   ERRO: TEST_PASSWORD deve ser definida nas variáveis de ambiente")
            print("   Exemplo: export TEST_PASSWORD=sua_senha")
            return
        
        login_data = {
            "username": username,
            "password": password,
            "csrf_token": csrf_token
        }
        
        r = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=False)
        print(f"   Status: {r.status_code}")
        
        if r.status_code in (302, 303):
            print("   OK - Login realizado com sucesso!")
        else:
            print(f"   ERRO no login: {r.text}")
            return
            
    except Exception as e:
        print(f"   Erro na requisição: {e}")
        return
    
    # 3) Acessa dashboard autenticado
    print("\n3. Acessando dashboard...")
    try:
        r = session.get(f"{base_url}/dashboard")
        print(f"   Status: {r.status_code}")
        
        if r.status_code == 200:
            print("   OK - Dashboard acessado com sucesso!")
        else:
            print(f"   ERRO no dashboard: {r.text}")
            
    except Exception as e:
        print(f"   Erro na requisição: {e}")

if __name__ == "__main__":
    test_login()
