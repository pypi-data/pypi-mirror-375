from collective.contact_behaviors import PACKAGE_NAME

import pytest


class TestVocabAvailableCountries:
    name = f"{PACKAGE_NAME}.available_countries"

    @property
    def endpoint(self):
        return f"/@vocabularies/{self.name}"

    def test_manager_can_view(self, manager_request):
        response = manager_request.get(self.endpoint)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "batching" in data
        assert data["items_total"] == 249
        assert data["items"][0]["title"] == "Afghanistan"
        assert data["items"][0]["token"] == "AF"  # noQA: S105

    def test_anonymous_can_view(self, anon_request):
        response = anon_request.get(self.endpoint)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "batching" in data
        assert data["items_total"] == 249
        assert data["items"][0]["title"] == "Afghanistan"
        assert data["items"][0]["token"] == "AF"  # noQA: S105

    @pytest.mark.parametrize(
        "language_code,idx,expected_title,expected_token",
        [
            ["en", 0, "Afghanistan", "AF"],
            ["pt_BR", 0, "Afeganistão", "AF"],
            ["es", 0, "Afganistán", "AF"],
            ["de", 0, "Afghanistan", "AF"],
            ["nl", 0, "Afghanistan", "AF"],
            ["en", 24, "Bhutan", "BT"],
            ["pt_BR", 24, "Butão", "BT"],
            ["es", 24, "Bután", "BT"],
            ["de", 24, "Bhutan", "BT"],
            ["nl", 24, "Bhutan", "BT"],
        ],
    )
    def test_translation(
        self, request_factory, language_code, idx, expected_title, expected_token
    ):
        session = request_factory()
        session.headers["Accept-Language"] = f"{language_code};q=0.5"
        response = session.get(self.endpoint)
        data = response.json()
        assert data["items"][idx]["title"] == expected_title
        assert data["items"][idx]["token"] == expected_token


class TestVocabCountries:
    name = f"{PACKAGE_NAME}.countries"

    @property
    def endpoint(self):
        return f"/@vocabularies/{self.name}"

    def test_manager_can_view(self, manager_request):
        response = manager_request.get(self.endpoint)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "batching" not in data
        assert data["items_total"] == 1
        assert data["items"][0]["title"] == "Germany"
        assert data["items"][0]["token"] == "DE"  # noQA: S105

    def test_anonymous_can_view(self, anon_request):
        response = anon_request.get(self.endpoint)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "batching" not in data
        assert data["items_total"] == 1
        assert data["items"][0]["title"] == "Germany"
        assert data["items"][0]["token"] == "DE"  # noQA: S105

    @pytest.mark.parametrize(
        "language_code,idx,expected_title,expected_token",
        [
            ["en", 0, "Germany", "DE"],
            ["pt_BR", 0, "Alemanha", "DE"],
            ["es", 0, "Alemania", "DE"],
            ["de", 0, "Deutschland", "DE"],
            ["nl", 0, "Duitsland", "DE"],
        ],
    )
    def test_translation(
        self, request_factory, language_code, idx, expected_title, expected_token
    ):
        session = request_factory()
        session.headers["Accept-Language"] = f"{language_code};q=0.5"
        response = session.get(self.endpoint)
        data = response.json()
        assert data["items"][idx]["title"] == expected_title
        assert data["items"][idx]["token"] == expected_token
