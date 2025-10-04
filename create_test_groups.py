#!/usr/bin/env python3
"""Criar dados de teste para grupos"""

import os
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import GroupVisit

# Configurar banco
DATABASE_URL = "sqlite:///./bilheteria.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_test_groups():
    """Criar grupos de teste"""
    db = SessionLocal()
    try:
        # Criar grupos para os últimos 3 meses
        institutions = [
            "Escola Municipal João Silva",
            "Colégio Estadual Maria Santos", 
            "Instituto Federal de Pernambuco",
            "Universidade Federal de Pernambuco",
            "Escola Técnica Estadual",
            "Colégio Dom Bosco",
            "Escola Municipal do Recife",
            "Instituto de Educação Superior"
        ]
        
        cities = [
            ("PE", "Recife"),
            ("PE", "Olinda"),
            ("PE", "Jaboatão dos Guararapes"),
            ("PE", "Paulista"),
            ("PE", "Camaragibe"),
            ("PE", "Abreu e Lima"),
            ("PE", "Igarassu"),
            ("PE", "Itapissuma")
        ]
        
        # Criar grupos para os últimos 90 dias
        for i in range(90):
            visit_date = date.today() - timedelta(days=i)
            
            # Criar 1-3 grupos por dia (com probabilidade)
            import random
            if random.random() < 0.7:  # 70% chance de ter pelo menos 1 grupo
                num_groups = random.randint(1, 3)
                
                for j in range(num_groups):
                    institution = random.choice(institutions)
                    state, city = random.choice(cities)
                    size = random.randint(15, 80)
                    scheduled = random.choice([True, True, True, False])  # 75% agendados
                    
                    group = GroupVisit(
                        date=visit_date,
                        institution=institution,
                        size=size,
                        state=state,
                        city=city,
                        scheduled=scheduled,
                        contact_name=f"Contato {i}-{j}",
                        contact_phone=f"(81) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                        price_total=round(size * random.uniform(5.0, 15.0), 2)
                    )
                    
                    db.add(group)
        
        db.commit()
        print("OK - Criados grupos de teste para os últimos 90 dias")
        
        # Mostrar estatísticas
        total_groups = db.query(GroupVisit).count()
        total_people = db.query(GroupVisit.size).all()
        total_people = sum(size[0] for size in total_people)
        
        print(f"Total de grupos: {total_groups}")
        print(f"Total de pessoas: {total_people}")
        
    except Exception as e:
        print(f"ERRO: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_groups()
