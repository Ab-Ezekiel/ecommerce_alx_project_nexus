def test_customer_cannot_create_product(api_client, customer_user):
    api_client.force_authenticate(customer_user)
    res = api_client.post("/api/products/", {"name": "Phone", "price": 200})
    assert res.status_code == 403


def test_admin_can_create_product(api_client, admin_user):
    api_client.force_authenticate(admin_user)
    res = api_client.post("/api/products/", {"name": "Phone", "price": 200})
    assert res.status_code == 201
