#!/usr/bin/env python3
"""Teste dos endpoints de grupos"""

import requests
import json
import os

def test_groups_api():
    """Testa os endpoints de grupos"""
    base_url = "http://127.0.0.1:8000"
    
    # 1) Login
    print("1. Fazendo login...")
    session = requests.Session()
    
    # GET login page
    r = session.get(f"{base_url}/auth/login")
    csrf_match = r.text.split('name="csrf_token" value="')[1].split('"')[0]
    
    # Get credentials from environment
    username = os.getenv("TEST_USERNAME", "***REMOVED***")
    password = os.getenv("TEST_PASSWORD")
    
    if not password:
        print("   ERRO: TEST_PASSWORD deve ser definida nas variáveis de ambiente")
        return
    
    # POST login
    login_data = {
        "username": username,
        "password": password,
        "csrf_token": csrf_match
    }
    r = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=False)
    
    if r.status_code not in (302, 303):
        print(f"   ERRO no login: {r.status_code}")
        return
    
    print("   OK - Login realizado")
    
    # 2) Testar KPIs
    print("\n2. Testando KPIs de grupos...")
    r = session.get(f"{base_url}/reports/api/groups/kpis")
    if r.status_code == 200:
        data = r.json()
        print(f"   Grupos (30 dias): {data.get('groups', 0)}")
        print(f"   Pessoas (30 dias): {data.get('people', 0)}")
        print(f"   Dias com visitas: {data.get('days_with', 0)}")
    else:
        print(f"   ERRO: {r.status_code}")
    
    # 3) Testar relatório semanal
    print("\n3. Testando relatório semanal...")
    r = session.get(f"{base_url}/reports/api/groups/weekly?weeks=4")
    if r.status_code == 200:
        data = r.json()
        print(f"   Semanas retornadas: {len(data)}")
        if data:
            print(f"   Primeira semana: {data[0]}")
    else:
        print(f"   ERRO: {r.status_code}")
    
    # 4) Testar relatório mensal
    print("\n4. Testando relatório mensal...")
    r = session.get(f"{base_url}/reports/api/groups/monthly?months=6")
    if r.status_code == 200:
        data = r.json()
        print(f"   Meses retornados: {len(data)}")
        if data:
            print(f"   Primeiro mês: {data[0]}")
    else:
        print(f"   ERRO: {r.status_code}")
    
    # 5) Testar top origens
    print("\n5. Testando top origens...")
    r = session.get(f"{base_url}/reports/api/groups/top-origins?days=90&limit=5")
    if r.status_code == 200:
        data = r.json()
        print(f"   Origens retornadas: {len(data)}")
        for i, origin in enumerate(data[:3]):
            print(f"   {i+1}. {origin['state']}-{origin['city']}: {origin['groups']} grupos, {origin['people']} pessoas")
    else:
        print(f"   ERRO: {r.status_code}")
    
    # 6) Testar export Excel
    print("\n6. Testando export Excel...")
    r = session.get(f"{base_url}/reports/groups/export.xlsx")
    if r.status_code == 200:
        print(f"   OK - Excel exportado")
        print(f"   Content-Type: {r.headers.get('content-type', 'N/A')}")
        print(f"   Content-Length: {len(r.content)} bytes")
    else:
        print(f"   ERRO: {r.status_code}")
    
    print("\nOK - Teste concluído!")

if __name__ == "__main__":
    test_groups_api()
