import requests
import random
import string

url = lambda x: "http://127.0.0.1:5000" + x
token = "wc45vcws4rc5sc67657t9ynt4v545"

random_string = lambda: ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


def _get_all_countries():
    return requests.get(url("/countries")).json()


def test_token():
    r = requests.post(url("/auth"), data={"login": "university", "password": "wrong_pass"})
    assert "message" in r.json()
    assert r.status_code == 403

    r = requests.post(url("/auth"), data=dict(login="university", password="university")).json()
    assert "token" in r


def test_get_list_countries():
    r = requests.get(url("/countries"))
    countries = r.json()
    assert r.status_code == 200

    r = requests.get(url("/countries/{}".format(countries[0]["id"]))).json()
    assert r["id"] == countries[0]["id"]

    r = requests.get(url("/countries/199999"))
    assert r.status_code == 404

    country_name = random_string()
    r = requests.post(url("/countries"), data=dict(token=token, name=country_name)).json()
    assert "name" in r

    r = requests.post(url("/countries"), data=dict(token=token, name=country_name))
    assert r.status_code == 409


def test_regions():
    countries = _get_all_countries()
    if len(countries) > 0:
        r = requests.get(url("/countries/{}/regions".format(countries[0]["id"])))
        assert r.status_code == 200
        regions = r.json()

        if len(regions) > 0:
            r = requests.get(url("/countries/{}/regions/{}".format(countries[0]["id"], regions[0]["id"])))
            assert r.status_code == 200
