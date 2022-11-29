import requests

class HttpClient:
    def get(self, url, headers = None):
        # TODO: Add error handling
        return requests.get(url, headers=headers)

    def post(self, url, json = None, headers = None):
        # TODO: Add error handling
        return requests.post(url, json = json, headers=headers)

    def put(self, url, json = None, headers = None):
        # TODO: Add error handling
        return requests.put(url, json = json, headers=headers)

    def request(self, method, url, json = None, headers = None):
        # TODO: Add error handling
        return requests.request(method, url, json = json, headers = headers)
