class TestContactViewPermissions:
    endpoint: str = "/content-1"

    def test_manager_can_view(self, manager_request):
        response = manager_request.get(self.endpoint)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "contact_email" in data
        assert data["contact_email"] == "foo@bar.de"
        assert "contact_website" in data
        assert data["contact_website"] == "https://plone.org"
        assert "contact_website" in data
        assert data["contact_phone"] == "+4917637752521"

    def test_anonymous_can_view(self, anon_request):
        response = anon_request.get(self.endpoint)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "contact_email" not in data
        assert "contact_website" not in data
        assert "contact_phone" not in data
