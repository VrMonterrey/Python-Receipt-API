def test_create_receipt(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    receipt_data = {
        "products": [
            {"name": "soap", "price": 1.5, "quantity": 2},
            {"name": "apples", "price": 3, "quantity": 3},
        ],
        "payment": {"type": "cash", "amount": 20},
    }
    response = client.post("/receipts/", headers=headers, json=receipt_data)
    assert response.status_code == 200
    assert response.json()["total"] == 12
    assert response.json()["rest"] == 8


def test_list_receipts(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/receipts/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_public_receipt_view(client):
    response = client.get("/receipts/1", params={"line_width": 40})
    assert response.status_code == 200
    assert "Дякуємо за покупку!" in response.text


def test_invalid_receipt_access(client):
    response = client.get("/receipts/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Receipt not found"