def test_application_repond(client):
    """L'application démarre et « / » répond (redirection vers /pt/ depuis l'étape 3)."""
    response = client.get("/", follow_redirects=True)
    assert response.status_code == 200
