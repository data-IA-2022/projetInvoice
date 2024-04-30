from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)


def test_get_list():
    response = client.get("/invoices", headers={'accept': 'application/json'})
    assert response.status_code == 200
    resp=response.json()
    assert 'invoices' in resp
    assert len(resp['invoices'])==1000

    response = client.get("/invoices?start_date=2025-01-01", headers={'accept': 'application/json'})
    assert response.status_code == 200
    resp=response.json()
    assert 'invoices' in resp
    assert len(resp['invoices'])==0

def test_get_invoice():
    response = client.get("/invoices/FAC_2019_0018-8393420")
    assert response.status_code == 200
    print(response.headers.get('content-type'))
    assert response.headers.get('content-type')=='image/png'

def test_get_wrong_invoice():
    response = client.get("/invoices/FAC_2019_0018-5555")
    assert response.status_code == 403
    assert 'Invalid n°' in response.text
