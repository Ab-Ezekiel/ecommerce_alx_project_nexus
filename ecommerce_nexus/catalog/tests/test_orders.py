def test_customer_cannot_view_other_orders(api_client, two_customers_with_orders):
    cust1, cust2, order1, order2 = two_customers_with_orders
    api_client.force_authenticate(cust1)

    res = api_client.get(f"/api/orders/{order2.id}/")
    assert res.status_code == 403

def test_admin_can_view_all_orders(api_client, admin_user, two_customers_with_orders):
    _, _, order1, order2 = two_customers_with_orders
    api_client.force_authenticate(admin_user)

    res = api_client.get(f"/api/orders/{order1.id}/")
    res2 = api_client.get(f"/api/orders/{order2.id}/")

    assert res.status_code == 200
    assert res2.status_code == 200
