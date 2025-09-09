import pytest


class TestAddressDefaultValuesPermissions:
    endpoint: str = "/@types/Content"

    @pytest.mark.parametrize("attr,expected", [["state", "SP"], ["country", "BR"]])
    def test_default_values(self, manager_request, attr, expected):
        response = manager_request.get(self.endpoint)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert data["properties"][attr]["default"] == expected
