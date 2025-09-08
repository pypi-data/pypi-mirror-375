import requests
from urllib.parse import urljoin


def test_version(pulp_api_v3_url):
    r = requests.get(urljoin(pulp_api_v3_url, "smart_proxy/version"))
    assert "version" in r.json()


def test_features(pulp_api_v3_url):
    r = requests.get(urljoin(pulp_api_v3_url, "smart_proxy/features"))
    assert ["pulpcore"] == r.json()


def test_features_v2(pulp_api_v3_url):
    r = requests.get(urljoin(pulp_api_v3_url, "smart_proxy/v2/features"))
    assert "pulpcore" in r.json()


def test_features_v2_without_rhsm_url(pulp_api_v3_url):
    r = requests.get(urljoin(pulp_api_v3_url, "smart_proxy/v2/features"))
    features = r.json()
    assert "rhsm_url" not in features["pulpcore"]["settings"]
