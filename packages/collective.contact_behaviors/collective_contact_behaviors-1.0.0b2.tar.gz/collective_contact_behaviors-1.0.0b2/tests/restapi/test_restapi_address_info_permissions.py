class TestAddressViewPermissions:
    endpoint: str = "/content-1"

    def test_manager_can_view(self, manager_request):
        response = manager_request.get(self.endpoint)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "address" in data
        assert data["address"] == "Riesstraße 21"
        assert "address_2" in data
        assert "city" in data
        assert "state" in data
        assert "postal_code" in data
        assert "country" in data

    def test_anonymous_can_view(self, anon_request):
        response = anon_request.get(self.endpoint)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "address" not in data
        assert "address_2" not in data
        assert "city" in data
        assert "state" in data
        assert "postal_code" in data
        assert "country" in data
