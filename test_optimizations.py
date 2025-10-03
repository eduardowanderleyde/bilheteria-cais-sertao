#!/usr/bin/env python3
"""Teste das otimizações implementadas"""

import requests
import time
import json

def test_optimizations():
    """Testa as otimizações de performance"""
    base_url = "http://127.0.0.1:8000"
    
    # 1) Login
    print("1. Fazendo login...")
    session = requests.Session()
    
    r = session.get(f"{base_url}/auth/login")
    csrf_match = r.text.split('name="csrf_token" value="')[1].split('"')[0]
    
    login_data = {
        "username": "***REMOVED***",
        "password": "18091992123",
        "csrf_token": csrf_match
    }
    r = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=False)
    
    if r.status_code not in (302, 303):
        print(f"   ERRO no login: {r.status_code}")
        return
    
    print("   OK - Login realizado")
    
    # 2) Testar KPIs (query otimizada)
    print("\n2. Testando KPIs otimizados...")
    start_time = time.time()
    r = session.get(f"{base_url}/reports/api/groups/kpis?days=30")
    end_time = time.time()
    
    if r.status_code == 200:
        data = r.json()
        print(f"   Tempo: {(end_time - start_time)*1000:.1f}ms")
        print(f"   Grupos: {data.get('groups', 0)}")
        print(f"   Pessoas: {data.get('people', 0)}")
        print(f"   Dias: {data.get('days_with', 0)}")
    else:
        print(f"   ERRO: {r.status_code}")
    
    # 3) Testar relatório semanal (PostgreSQL otimizado)
    print("\n3. Testando relatório semanal otimizado...")
    start_time = time.time()
    r = session.get(f"{base_url}/reports/api/groups/weekly?weeks=8")
    end_time = time.time()
    
    if r.status_code == 200:
        data = r.json()
        print(f"   Tempo: {(end_time - start_time)*1000:.1f}ms")
        print(f"   Semanas: {len(data)}")
    else:
        print(f"   ERRO: {r.status_code}")
    
    # 4) Testar relatório mensal (PostgreSQL otimizado)
    print("\n4. Testando relatório mensal otimizado...")
    start_time = time.time()
    r = session.get(f"{base_url}/reports/api/groups/monthly?months=12")
    end_time = time.time()
    
    if r.status_code == 200:
        data = r.json()
        print(f"   Tempo: {(end_time - start_time)*1000:.1f}ms")
        print(f"   Meses: {len(data)}")
    else:
        print(f"   ERRO: {r.status_code}")
    
    # 5) Testar top origens (com limites)
    print("\n5. Testando top origens com limites...")
    start_time = time.time()
    r = session.get(f"{base_url}/reports/api/groups/top-origins?days=180&limit=10")
    end_time = time.time()
    
    if r.status_code == 200:
        data = r.json()
        print(f"   Tempo: {(end_time - start_time)*1000:.1f}ms")
        print(f"   Origens: {len(data)}")
    else:
        print(f"   ERRO: {r.status_code}")
    
    # 6) Testar export Excel otimizado
    print("\n6. Testando export Excel otimizado...")
    start_time = time.time()
    r = session.get(f"{base_url}/reports/groups/export.xlsx?months=6")
    end_time = time.time()
    
    if r.status_code == 200:
        print(f"   Tempo: {(end_time - start_time)*1000:.1f}ms")
        print(f"   Content-Type: {r.headers.get('content-type', 'N/A')}")
        print(f"   Tamanho: {len(r.content)} bytes")
    else:
        print(f"   ERRO: {r.status_code}")
    
    # 7) Testar export CSV streaming
    print("\n7. Testando export CSV streaming...")
    start_time = time.time()
    r = session.get(f"{base_url}/reports/groups/export.csv?months=6")
    end_time = time.time()
    
    if r.status_code == 200:
        print(f"   Tempo: {(end_time - start_time)*1000:.1f}ms")
        print(f"   Content-Type: {r.headers.get('content-type', 'N/A')}")
        print(f"   Tamanho: {len(r.content)} bytes")
    else:
        print(f"   ERRO: {r.status_code}")
    
    # 8) Testar limites de segurança
    print("\n8. Testando limites de segurança...")
    
    # Testar limite de semanas
    r = session.get(f"{base_url}/reports/api/groups/weekly?weeks=100")
    if r.status_code == 200:
        data = r.json()
        print(f"   Semanas limitadas: {len(data)} (máx 52)")
    
    # Testar limite de meses
    r = session.get(f"{base_url}/reports/api/groups/monthly?months=50")
    if r.status_code == 200:
        data = r.json()
        print(f"   Meses limitados: {len(data)} (máx 24)")
    
    # Testar limite de dias
    r = session.get(f"{base_url}/reports/api/groups/kpis?days=500")
    if r.status_code == 200:
        data = r.json()
        print(f"   Dias limitados: {data.get('groups', 0)} grupos (máx 365 dias)")
    
    print("\nOK - Teste de otimizações concluído!")

if __name__ == "__main__":
    test_optimizations()
