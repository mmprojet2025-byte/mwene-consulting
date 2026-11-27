def test_accueil_repond(client):
    """La page « / » répond avec le code 200 (OK)."""
    response = client.get("/")
    assert response.status_code == 200
