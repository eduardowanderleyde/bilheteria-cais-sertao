"""
Sales functionality tests
"""
import pytest
from fastapi.testclient import TestClient
from app.models import Order, OrderItem


def test_sell_page(client: TestClient, auth_headers):
    """Test sell page loads correctly"""
    response = client.get("/sell", headers=auth_headers)
    assert response.status_code == 200
    assert "Vender Ingressos" in response.text


def test_create_sale(client: TestClient, auth_headers, db_session):
    """Test creating a new sale"""
    response = client.post("/sell", data={
        "ticket_type": "inteira",
        "quantity": 2,
        "payment_method": "pix",
        "customer_name": "João Silva",
        "customer_state": "PE",
        "customer_city": "Recife"
    }, headers=auth_headers)
    
    assert response.status_code in [200, 302]
    
    # Check if order was created
    order = db_session.query(Order).first()
    assert order is not None
    assert order.customer_name == "João Silva"
    assert order.payment_method == "pix"


def test_create_sale_with_discount(client: TestClient, auth_headers, db_session):
    """Test creating a sale with discount"""
    response = client.post("/sell", data={
        "ticket_type": "meia",
        "quantity": 1,
        "payment_method": "credito",
        "discount_reason": "estudante_publica",
        "customer_name": "Maria Santos",
        "customer_state": "PB",
        "customer_city": "João Pessoa"
    }, headers=auth_headers)
    
    assert response.status_code in [200, 302]
    
    # Check if order was created with discount
    order = db_session.query(Order).first()
    assert order is not None
    assert order.customer_name == "Maria Santos"


def test_sale_validation(client: TestClient, auth_headers):
    """Test sale validation"""
    # Test invalid quantity
    response = client.post("/sell", data={
        "ticket_type": "inteira",
        "quantity": 0,  # Invalid
        "payment_method": "pix"
    }, headers=auth_headers)
    
    assert response.status_code == 400


def test_sale_without_discount_reason(client: TestClient, auth_headers):
    """Test sale validation for discount tickets"""
    response = client.post("/sell", data={
        "ticket_type": "meia",
        "quantity": 1,
        "payment_method": "pix"
        # Missing discount_reason
    }, headers=auth_headers)
    
    assert response.status_code == 400
