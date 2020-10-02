import requests

from app import recreate_db, errors

url = lambda x: "http://127.0.0.1:5000" + x
token = "wc45vcws4rc5sc67657t9ynt4v545"


class TestToken:

    def test_acquire_token_with_invalid_credentials(self):
        r = requests.post(url("/auth"), data={"login": "university", "password": "wrong_pass"})
        assert "message" in r.json()
        assert r.status_code == 403

    def test_acquire_token(self):
        r = requests.post(url("/auth"), data=dict(login="university", password="university")).json()
        assert "token" in r


class TestCountry:
    def setup_class(self):
        recreate_db()

    def test_get_list_countries(self):
        r = requests.get(url("/countries")).json()
        assert len(r) == 2

    def test_get_country(self):
        r = requests.get(url("/countries/1")).json()
        assert r["id"] == 1

        # Test not found

        r = requests.get(url("/countries/10"))
        assert r.json()["message"] == errors["ElementNotFoundError"]["message"]
        assert r.status_code == errors["ElementNotFoundError"]["status"]

    def test_success_add_new_country(self):
        r = requests.post(url("/countries"), data=dict(token=token, name="China")).json()
        assert "name" in r

        # Test duplication

        r = requests.post(url("/countries"), data=dict(token=token, name="China"))
        assert r.json()["message"] == errors["ResourceAlreadyExistsError"]["message"]
        assert r.status_code == errors["ResourceAlreadyExistsError"]["status"]

    def test_success_update_country(self):
        requests.put(url("/countries/1"), data=dict(token=token, name="Russia"))
        r = requests.get(url("/countries/1")).json()
        assert r["name"] == "Russia"

        # Test duplication

        r = requests.put(url("/countries/1"), data=dict(token=token, name="Germany"))
        assert r.json()["message"] == errors["ResourceAlreadyExistsError"]["message"]
        assert r.status_code == errors["ResourceAlreadyExistsError"]["status"]

    def test_success_delete_country(self):
        r = requests.delete(url("/countries/1"), data=dict(token=token))
        assert r.status_code == 204
        r = requests.get(url("/countries/1"))
        assert r.status_code == 404
        recreate_db()

    def test_error_add_new_country_no_name(self):
        r = requests.post(url("/countries"), data=dict(token=token, name=""))
        assert r.status_code == 400
        assert "message" in r.json()

    def test_error_add_new_country_no_token(self):
        r = requests.post(url("/countries"), data=dict(name="Palestina"))
        assert r.status_code == 400
        assert "message" in r.json()

    def test_error_add_new_country_invalid_token(self):
        r = requests.post(url("/countries"), data=dict(token="invalid-token", name="Palestina"))
        assert r.status_code == 401
        assert "message" in r.json()

    def test_error_update_country_no_name(self):
        r = requests.put(url("/countries/1"), data=dict(token=token, name=""))
        assert r.status_code == 400
        assert "message" in r.json()

    def test_error_update_country_no_token(self):
        r = requests.put(url("/countries/1"), data=dict(name="Palestina"))
        assert r.status_code == 400
        assert "message" in r.json()

    def test_error_update_country_no_invalid(self):
        r = requests.put(url("/countries/1"), data=dict(token="invalid-token", name="Palestina"))
        assert r.status_code == 401
        assert "message" in r.json()

    def test_error_delete_country_no_token(self):
        r = requests.delete(url("/countries/1"))
        assert r.status_code == 400

    def test_error_delete_country_invalid_token(self):
        r = requests.delete(url("/countries/1"), data=dict(token="invalid-token"))
        assert r.status_code == 401


class TestRegion:
    def setup_class(self):
        recreate_db()

    def test_get_list_regions(self):
        r = requests.get(url("/countries/1/regions")).json()
        assert len(r) == 2

    def test_get_region(self):
        r = requests.get(url("/countries/1/regions/1")).json()
        assert r["id"] == 1

        # Test not found

        r = requests.get(url("/countries/1/regions/10"))
        assert r.json()["message"] == errors["ElementNotFoundError"]["message"]
        assert r.status_code == errors["ElementNotFoundError"]["status"]


    def test_success_add_new_region(self):
        r = requests.post(url("/countries/1/regions"), data=dict(token=token, name="Nikolsk")).json()
        assert "name" in r

        # Test duplication

        r = requests.post(url("/countries/1/regions"), data=dict(token=token, name="Nikolsk"))
        assert r.json()["message"] == errors["ResourceAlreadyExistsError"]["message"]
        assert r.status_code == errors["ResourceAlreadyExistsError"]["status"]

    def test_success_update_region(self):
        requests.put(url("/countries/1/regions/1"), data=dict(token=token, name="Balashiha"))
        r = requests.get(url("/countries/1/regions/1")).json()
        assert r["name"] == "Balashiha"

        # Test duplication

        r = requests.put(url("/countries/1/regions/1"), data=dict(token=token, name="Korolev"))
        assert r.json()["message"] == errors["ResourceAlreadyExistsError"]["message"]
        assert r.status_code == errors["ResourceAlreadyExistsError"]["status"]

    def test_success_delete_region(self):
        r = requests.delete(url("/countries/1/regions/1"), data=dict(token=token))
        assert r.status_code == 204
        r = requests.get(url("/countries/1/regions/1"))
        assert r.status_code == 404
        recreate_db()

    def test_error_add_new_region_no_name(self):
        r = requests.post(url("/countries/1/regions"), data=dict(token=token, name=""))
        assert r.status_code == 400
        assert "message" in r.json()

    def test_error_add_new_country_no_token(self):
        r = requests.post(url("/countries/1/regions"), data=dict(name="Palestina"))
        assert r.status_code == 400
        assert "message" in r.json()

    def test_error_add_new_region_invalid_token(self):
        r = requests.post(url("/countries/1/regions"), data=dict(token="invalid-token", name="Palestina"))
        assert r.status_code == 401
        assert "message" in r.json()

    def test_error_update_region_no_name(self):
        r = requests.put(url("/countries/1/regions/1"), data=dict(token=token, name=""))
        assert r.status_code == 400
        assert "message" in r.json()

    def test_error_update_region_no_token(self):
        r = requests.put(url("/countries/1/regions/1"), data=dict(name="Palestina"))
        assert r.status_code == 400
        assert "message" in r.json()

    def test_error_update_region_no_invalid(self):
        r = requests.put(url("/countries/1/regions/1"), data=dict(token="invalid-token", name="Palestina"))
        assert r.status_code == 401
        assert "message" in r.json()

    def test_error_delete_region_no_token(self):
        r = requests.delete(url("/countries/1/regions/1"))
        assert r.status_code == 400

    def test_error_delete_region_invalid_token(self):
        r = requests.delete(url("/countries/1/regions/1"), data=dict(token="invalid-token"))
        assert r.status_code == 401
