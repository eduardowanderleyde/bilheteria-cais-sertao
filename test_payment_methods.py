#!/usr/bin/env python3
"""Teste das formas de pagamento incluindo Dinheiro"""

import requests
import re
import os

def test_payment_methods():
    """Testa se todas as formas de pagamento estão disponíveis"""
    base_url = "http://127.0.0.1:8000"
    
    # 1) Login
    print("1. Fazendo login...")
    session = requests.Session()
    
    # GET login page
    r = session.get(f"{base_url}/auth/login")
    csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', r.text)
    csrf_token = csrf_match.group(1)
    
    # Get credentials from environment
    username = os.getenv("TEST_USERNAME", "admingeral")
    password = os.getenv("TEST_PASSWORD")
    
    if not password:
        print("   ERRO: TEST_PASSWORD deve ser definida nas variáveis de ambiente")
        return
    
    # POST login
    login_data = {
        "username": username,
        "password": password,
        "csrf_token": csrf_token
    }
    r = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=False)
    
    if r.status_code not in (302, 303):
        print(f"   ERRO no login: {r.status_code}")
        return
    
    print("   OK - Login realizado")
    
    # 2) Verificar página de venda individual
    print("\n2. Verificando página de venda individual...")
    r = session.get(f"{base_url}/sell")
    
    if r.status_code != 200:
        print(f"   ERRO: {r.status_code}")
        return
    
    # Verificar se todas as formas de pagamento estão presentes
    payment_methods = ["credito", "debito", "pix", "dinheiro"]
    found_methods = []
    
    for method in payment_methods:
        if f'value="{method}"' in r.text:
            found_methods.append(method)
            print(f"   OK - {method.upper()} encontrado")
        else:
            print(f"   ERRO - {method.upper()} NÃO encontrado")
    
    print(f"   Total encontrados: {len(found_methods)}/{len(payment_methods)}")
    
    # 3) Verificar página de grupos
    print("\n3. Verificando página de grupos...")
    r = session.get(f"{base_url}/groups")
    
    if r.status_code != 200:
        print(f"   ERRO: {r.status_code}")
        return
    
    # Verificar se todas as formas de pagamento estão presentes
    found_methods_groups = []
    
    for method in payment_methods:
        if f'value="{method}"' in r.text:
            found_methods_groups.append(method)
            print(f"   OK - {method.upper()} encontrado")
        else:
            print(f"   ERRO - {method.upper()} NÃO encontrado")
    
    print(f"   Total encontrados: {len(found_methods_groups)}/{len(payment_methods)}")
    
    # 4) Verificar relatório por pagamento
    print("\n4. Verificando relatório por pagamento...")
    r = session.get(f"{base_url}/reports/by-payment.csv")
    
    if r.status_code == 200:
        print("   OK - Relatório CSV acessível")
        print(f"   Content-Type: {r.headers.get('content-type', 'N/A')}")
        print(f"   Content-Length: {len(r.content)} bytes")
    else:
        print(f"   ERRO: {r.status_code}")
    
    # 5) Verificar página de relatórios
    print("\n5. Verificando página de relatórios...")
    r = session.get(f"{base_url}/reports")
    
    if r.status_code != 200:
        print(f"   ERRO: {r.status_code}")
        return
    
    if "Por Pagamento" in r.text and "by-payment.csv" in r.text:
        print("   OK - Link para relatório por pagamento encontrado")
    else:
        print("   ERRO - Link para relatório por pagamento NÃO encontrado")
    
    print("\nOK - Teste concluído!")

if __name__ == "__main__":
    test_payment_methods()
