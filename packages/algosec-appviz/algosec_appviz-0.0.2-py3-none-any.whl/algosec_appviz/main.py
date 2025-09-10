import requests
from algosec_appviz import environment
from mydict import MyDict


class AlgoSecAppViz:
    def __init__(self, tenant_id, client_id, client_secret):
        self.url = "https://eu.app.algosec.com/api/algosaas/auth/v1/access-keys/login"

        data = {
            "tenantId": environment.get_tenant_id(),
            "clientId": environment.get_client_id(),
            "clientSecret": environment.get_client_secret()
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        response = requests.post(self.url, json=data, headers=headers)
        if response.status_code != 200:
            raise ConnectionError(f"Authentication to AppViz failed: {response.text}")
        self._token_type = response.json()['token_type']
        self._token = response.json()['access_token']

    def get_applications(self):
        url = 'https://eu.app.algosec.com/BusinessFlow/rest/v1/applications'
        headers = {
            'Accept': 'application/json',
            'Authorization': f'{self._token_type} {self._token}'
        }

        response = requests.get(url, headers=headers)
        return [MyDict(x) for x in response.json()]

    def get_network_objects(self):
        url = 'https://eu.app.algosec.com/ObjectFlow/rest/v1/network_objects/name/'
        headers = {
            'Accept': 'application/json',
            'Authorization': f'{self._token_type} {self._token}'
        }

        response = requests.get(url, headers=headers)
        return [MyDict(x) for x in response.json()]

    def _make_api_call(self, method, url):
        headers = {
            'Accept': 'application/json',
            'Authorization': f'{self._token_type} {self._token}'
        }

        if method.lower() == 'get':
            response = requests.get(url, headers=headers)
        elif method.lower() == 'post':
            response = requests.get(url, headers=headers)
        else:
            raise AssertionError("Invalid method, must be: 'GET' or 'POST'")