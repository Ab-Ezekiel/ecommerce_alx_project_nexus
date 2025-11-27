# accounts/tests/test_permissions.py
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

# Mark all tests in this module to run against the database
pytestmark = pytest.mark.django_db

def test_user_cannot_list_all_users(api_client, customer_user, admin_user):
    """
    Ensure a standard customer cannot access the list of all users.
    """
    api_client.force_authenticate(customer_user)
    # Assumes you have a UserViewSet registered with a URL name like 'user-list'
    url = reverse("user-list") 
    res = api_client.get(url)
    
    # Standard users should typically be forbidden (403) from listing all users
    # or sometimes get a 404 depending on configuration. 403 is common for DRF.
    assert res.status_code == 403

def test_admin_can_list_all_users(api_client, customer_user, admin_user):
    """
    Ensure an admin can access the list of all users.
    """
    api_client.force_authenticate(admin_user)
    # Assumes you have a UserViewSet registered with a URL name like 'user-list'
    url = reverse("user-list")
    res = api_client.get(url)
    
    assert res.status_code == 200
    assert len(res.data) >= 2 # Should see both the customer and the admin user

def test_user_can_only_view_their_own_details(api_client, customer_user, admin_user):
    """
    Ensure a standard user cannot fetch details for another user's account.
    """
    api_client.force_authenticate(customer_user)
    # Try to access the admin user's details
    # Assumes a 'user-detail' URL name
    url = reverse("user-detail", args=[admin_user.id])
    res = api_client.get(url)
    
    assert res.status_code == 403 

def test_user_can_view_their_own_details(api_client, customer_user):
    """
    Ensure a user can fetch details for their own account.
    """
    api_client.force_authenticate(customer_user)
    # Assumes a 'user-detail' URL name
    url = reverse("user-detail", args=[customer_user.id])
    res = api_client.get(url)
    
    assert res.status_code == 200
    assert res.data['email'] == customer_user.email
